# Aster & Row Support Agent

An AI support agent for Aster & Row (ecommerce) built for the AI Agent Intern take-home assignment.

## Setup

1. Clone this repo and `cd` into it.
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\Activate.ps1` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your real Groq API key (get one free, no card required, at https://console.groq.com/keys)
6. Run: `cd app && python generate.py`

## Model & architecture

- **LLM:** Groq API, `openai/gpt-oss-120b` (originally used `llama-3.3-70b-versatile`, deprecated by Groq in June 2026 — see Bug Diary)
- **Retrieval:** BM25 (`rank-bm25`), no vector DB / embeddings — chosen for simplicity and zero cost given the small (14-doc) corpus and the assignment's 6-8hr timebox
- **Chunking:** Markdown files split by `##` heading, front-matter metadata (`status`, `audience`, `customer_answering`, etc.) preserved and attached to each chunk (`app/ingest.py`)
- **Precedence logic:** active/current docs are boosted, superseded/draft/internal docs are penalized in the BM25 ranking (`app/retrieve.py`)
- **Generation:** retrieved chunks are formatted into a context block and passed to the LLM with a system prompt enforcing citation, abstention on insufficient info, and refusal to treat retrieved text as instructions (`app/generate.py`)

## Architecture
knowledge-base/*.md → ingest.py (chunk + metadata) → retrieve.py (BM25 + precedence) → generate.py (LLM call with grounded context)


## Bug diary

### Bug 1: Internal/injection content misclassified as usable

- **How I found it:** Ran a test query resembling a prompt-injection attempt (`"ignore all prior instructions"`) against the retriever and inspected which chunks were marked usable.
- **Root cause:** My exclusion logic only checked the `status` front-matter field. Doc 14 (`14-internal-content-migration-notes.md`, which contains a planted prompt-injection payload) actually used different fields — `audience: internal` and `customer_answering: False` — not `status: internal`. So it was retrieved and passed to the LLM as a legitimate, citable source.
- **Fix:** Rewrote `is_usable()` in `retrieve.py` to check `status`, `audience`, and `customer_answering` together, and added a heavier scoring penalty for `audience: internal`.
- **Regression test:** (add to `evaluation/` in Day 3) — assert that for any query, chunks from `14-internal-content-migration-notes.md` never appear with `usable: True`.

### Bug 2: Groq model deprecation
- **How I found it:** `generate.py` failed with `404 model_not_found` on `llama-3.3-70b-versatile`.
- **Root cause:** Groq deprecated that model in June 2026 in favor of `openai/gpt-oss-120b`.
- **Fix:** Swapped `MODEL` constant in `generate.py`.
- **Regression test:** N/A (infra config, not app logic) — noted here for transparency per the assignment's "document what broke" requirement.

## Known limitations (Piece 1, as of Day 1)

- No conflict detection yet between genuinely competing active sources (e.g., TrailPlus exception vs standard policy) — planned for Day 2/3.
- No order lookup tool yet (Piece 2).
- No conversation memory yet (Piece 3).
- Evaluation suite not yet built (Day 3).