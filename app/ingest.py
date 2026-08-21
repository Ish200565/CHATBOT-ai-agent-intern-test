import os
import re
import frontmatter

KB_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge-base")


def chunk_document(filepath):
    """Split one markdown file into chunks by ## heading, keep front-matter metadata."""
    post = frontmatter.load(filepath)
    metadata = dict(post.metadata)
    body = post.content
    filename = os.path.basename(filepath)

    parts = re.split(r"(?m)^(##\s+.*)$", body)

    chunks = []
    if parts[0].strip():

        chunks.append({
            "text": parts[0].strip(),
            "filename": filename,
            "heading": "(intro)",
            "metadata": metadata,
        })

    for i in range(1, len(parts), 2):
        heading = parts[i].strip("# ").strip()
        text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if text:
            chunks.append({
                "text": f"{heading}\n\n{text}",
                "filename": filename,
                "heading": heading,
                "metadata": metadata,
            })

    return chunks


def load_all_chunks():
    all_chunks = []
    for fname in sorted(os.listdir(KB_DIR)):
        if fname.endswith(".md"):
            fpath = os.path.join(KB_DIR, fname)
            all_chunks.extend(chunk_document(fpath))
    return all_chunks


if __name__ == "__main__":
    chunks = load_all_chunks()
    print(f"Loaded {len(chunks)} chunks from {KB_DIR}\n")
    for c in chunks[:5]:
        print(f"[{c['filename']}] {c['heading']}  | status={c['metadata'].get('status')}")
        print(c["text"][:120].replace("\n", " "))
        print("---")