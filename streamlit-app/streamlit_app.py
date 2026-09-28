"""
RAG demo over my own published OSS library docs
(lambda-preflight, token-budget-contracts, tbcontracts-mcp).

Deployed on Streamlit Community Cloud.

Pipeline: chunk docs -> embed (TF-IDF, local) -> store in Chroma
          -> retrieve top-k chunks for a user's question.

Retrieval-only by design: returns real source text, not a generated
answer, so there is no hallucination risk in this version.
"""

import glob
import os
import re

import chromadb
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80


def load_and_chunk(docs_dir):
    chunks, metadatas, ids = [], [], []
    for path in sorted(glob.glob(os.path.join(docs_dir, "*.md"))):
        text = open(path, encoding="utf-8").read()
        text = re.sub(r"\n{2,}", "\n\n", text).strip()
        start = 0
        idx = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            chunks.append(chunk)
            metadatas.append({"file_name": os.path.basename(path)})
            ids.append(f"{os.path.basename(path)}::{idx}")
            start = end - CHUNK_OVERLAP
            idx += 1
    return chunks, metadatas, ids


@st.cache_resource
def build_index():
    chunks, metadatas, ids = load_and_chunk(DOCS_DIR)

    vectorizer = TfidfVectorizer(stop_words="english", max_features=512)
    doc_vectors = vectorizer.fit_transform(chunks).toarray()

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection("oss_docs")
    collection.add(
        embeddings=doc_vectors.tolist(),
        documents=chunks,
        metadatas=metadatas,
        ids=ids,
    )
    return vectorizer, collection


vectorizer, collection = build_index()

st.set_page_config(page_title="RAG Search - My OSS Docs", page_icon="🔍")

st.title("RAG Search — My Own Published Libraries")
st.markdown(
    "Ask a question about **lambda-preflight**, **token-budget-contracts**, "
    "or **tbcontracts-mcp** (all published on PyPI). This is a retrieval-only "
    "RAG pipeline — it returns the actual matching documentation text, not a "
    "generated answer, so there's no hallucination risk.\n\n"
    "**Pipeline:** chunk → TF-IDF embed → Chroma vector store → cosine-similarity retrieval."
)

EXAMPLES = [
    "How does the CannotEvaluate result work in lambda-preflight?",
    "How does tbcontracts decide which agent to take tokens from during reallocation?",
    "What observability signals does tbcontracts-mcp emit?",
    "What is the licensing situation for token-budget-contracts?",
]

with st.sidebar:
    st.markdown("### Example questions")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state["query"] = ex

query = st.text_input(
    "Your question",
    value=st.session_state.get("query", ""),
    placeholder="e.g. What observability signals does tbcontracts-mcp emit?",
)
top_k = st.slider("Number of results (top-k)", 1, 5, 2)

if query.strip():
    q_vec = vectorizer.transform([query]).toarray().tolist()
    results = collection.query(query_embeddings=q_vec, n_results=int(top_k))

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    if not docs:
        st.info("No matching chunks found.")
    else:
        for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists), 1):
            st.markdown(f"**Result {i}**  ·  source: `{meta['file_name']}`  ·  distance: {dist:.3f}")
            st.markdown(f"> {doc.strip()}")
            st.divider()
else:
    st.info("Type a question above or click an example in the sidebar.")
