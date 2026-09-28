# rag-oss-docs

A small, real RAG (retrieval-augmented generation — retrieval half)
pipeline built over the documentation of three of my own published
Python libraries: `lambda-preflight`, `token-budget-contracts`, and
`tbcontracts-mcp`.

Two versions, same pipeline logic:

- **[`cli/`](./cli)** — run it locally from the command line. Good for
  reading the raw pipeline code end to end.
- **[`webapp/`](./webapp)** — a Gradio web app, deployed on Hugging
  Face Spaces, so anyone can try it in a browser without installing
  anything.

## Live demo

[Link to the deployed Space goes here once published]

## What it does

Takes a natural-language question (e.g. *"What observability signals
does tbcontracts-mcp emit?"*) and returns the most relevant chunks of
real documentation — source file + similarity score — no generated
text, no hallucination risk in this version.

## Pipeline

1. **Chunk** — docs split into 400-character windows, 80-character overlap
2. **Embed** — TF-IDF vectors (scikit-learn), fully local, no API key needed
3. **Store** — Chroma vector database
4. **Retrieve** — cosine-similarity top-k lookup against the query vector

See each subfolder's own README/comments for setup and run instructions.

## Why TF-IDF, not a neural embedding model

Built in an environment without reliable access to a model hub, so I
used TF-IDF instead of faking a call to a blocked service. It's a
real, classic embedding technique — fast and fully explainable — but
it only matches on literal word overlap, so it misses paraphrases
("throttling" vs. "rate limiting"). Swapping in a neural embedding
model (sentence-transformers, or an API-based embedding model) is a
straightforward upgrade — see the comments in `app.py` / `build_and_query.py`.

## Author

Swaranshu Borgaonkar

- https://pypi.org/project/token-budget-contracts/
- https://pypi.org/project/lambda-preflight/
- https://pypi.org/project/tbcontracts-mcp/
