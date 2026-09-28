---
title: RAG Search - My OSS Docs
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# RAG Search over My Own Published Libraries

A small, real, deployed RAG (retrieval half) pipeline over the
documentation of three of my own published Python libraries:
`lambda-preflight`, `token-budget-contracts`, and `tbcontracts-mcp`.

Ask a question and get back the actual matching documentation text —
no hallucination risk, since this version is retrieval-only (no LLM
generation step).

## Pipeline

1. **Chunking** — docs split into 400-character chunks with 80-character overlap
2. **Embedding** — TF-IDF vectors (scikit-learn), fully local
3. **Vector store** — Chroma (in-memory client for this demo)
4. **Retrieval** — cosine-similarity top-k lookup against the query vector

## Deploying this yourself

1. Create a new Space on huggingface.co (SDK: Gradio)
2. Push these files: `app.py`, `requirements.txt`, `docs/`, this `README.md`
3. The Space builds and serves `app.py` automatically

## Upgrading to neural embeddings

Swap the `TfidfVectorizer` in `app.py` for a real embedding model —
Spaces have internet access, so this works out of the box:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
doc_vectors = model.encode(chunks)
```

(Add `sentence-transformers` to `requirements.txt` if you do this.)

## Adding a generation step (full RAG)

This is retrieval-only by design. To add generation, feed the
retrieved chunks + question into an LLM API call and return the
synthesized answer instead of raw chunks — see the code comments in
`app.py` for where that would slot in.

## Author

Swaranshu Borgaonkar — built over my own published PyPI packages:
- https://pypi.org/project/token-budget-contracts/
- https://pypi.org/project/lambda-preflight/
- https://pypi.org/project/tbcontracts-mcp/
