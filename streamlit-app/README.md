# RAG Search — My Own Published Libraries (Streamlit)

A small, real RAG (retrieval half) pipeline over the documentation of
three of my own published Python libraries: `lambda-preflight`,
`token-budget-contracts`, and `tbcontracts-mcp`.

Deployed free on Streamlit Community Cloud.

## Pipeline

1. **Chunking** — docs split into 400-character chunks, 80-character overlap
2. **Embedding** — TF-IDF vectors (scikit-learn), fully local
3. **Vector store** — Chroma (in-memory client)
4. **Retrieval** — cosine-similarity top-k lookup against the query vector

Retrieval-only by design — returns real source text, not a generated
answer, so there's no hallucination risk.

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to a public GitHub repo (or a subfolder of one)
2. Go to share.streamlit.io → "Create app"
3. Point it at the repo and set the main file path to `streamlit_app.py`
4. Deploy — it builds automatically and gives you a public URL

## Author

Swaranshu Borgaonkar
- https://pypi.org/project/token-budget-contracts/
- https://pypi.org/project/lambda-preflight/
- https://pypi.org/project/tbcontracts-mcp/
