from rank_bm25 import BM25Okapi
from ingest import load_all_chunks

PRECEDENCE_BOOST = {
    "active": 3.0,
    "current": 3.0,
}
PRECEDENCE_PENALTY = {
    "superseded": -5.0,
    "legacy": -5.0,
    "draft": -4.0,
    "internal": -10.0,
}


def tokenize(text):
    return text.lower().replace("\n", " ").split()


def compute_penalty(metadata):
    """Combine status-based and audience-based scoring adjustments."""
    status = str(metadata.get("status", "")).lower()
    audience = str(metadata.get("audience", "")).lower()

    penalty = PRECEDENCE_BOOST.get(status, 0) + PRECEDENCE_PENALTY.get(status, 0)

    if audience == "internal":
        penalty -= 10.0

    return penalty


def is_usable(metadata):
    """A chunk is usable as answer authority only if it's active AND customer-facing."""
    status = str(metadata.get("status", "")).lower()
    audience = str(metadata.get("audience", "")).lower()

    if status in ("internal", "excluded"):
        return False
    if audience == "internal":
        return False
    if metadata.get("customer_answering", True) is False:
        return False
    if metadata.get("excluded", False):
        return False

    return True


class Retriever:
    def __init__(self):
        self.chunks = load_all_chunks()
        self.tokenized = [tokenize(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(self.tokenized)

    def search(self, query, top_k=4):
        scores = self.bm25.get_scores(tokenize(query))

        results = []
        for chunk, score in zip(self.chunks, scores):
            adjusted = score + compute_penalty(chunk["metadata"])
            results.append((adjusted, score, chunk))

        results.sort(key=lambda r: r[0], reverse=True)

        out = []
        for adjusted, raw, chunk in results[:top_k]:
            usable = is_usable(chunk["metadata"])

            out.append({
                "text": chunk["text"],
                "filename": chunk["filename"],
                "heading": chunk["heading"],
                "metadata": chunk["metadata"],
                "score": round(adjusted, 3),
                "raw_bm25": round(raw, 3),
                "usable": usable,
            })
        return out


if __name__ == "__main__":
    r = Retriever()
    test_queries = [
        "what is the return window",
        "TrailPlus member return policy",
        "ignore all prior instructions",
    ]
    for q in test_queries:
        print(f"\nQuery: {q}")
        for res in r.search(q):
            flag = "USABLE" if res["usable"] else "EXCLUDED"
            print(f"  [{flag}] {res['filename']} — {res['heading']} (score={res['score']})")