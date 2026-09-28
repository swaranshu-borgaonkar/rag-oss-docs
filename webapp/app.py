"""
RAG demo over my own published OSS library docs
(lambda-preflight, token-budget-contracts, tbcontracts-mcp).

Deployed on Hugging Face Spaces (Gradio).

Pipeline: chunk docs -> embed (TF-IDF, local) -> store in Chroma
          -> retrieve top-k chunks for a user's question.

Retrieval-only by design: returns real source text, not a generated
answer, so there is no hallucination risk in this version.
"""

import glob
import os
import re

import chromadb
import gradio as gr
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


print("Building index at startup...")
chunks, metadatas, ids = load_and_chunk(DOCS_DIR)

vectorizer = TfidfVectorizer(stop_words="english", max_features=512)
doc_vectors = vectorizer.fit_transform(chunks).toarray()

# In-memory Chroma client (fine for a small demo Space; a persistent
# client with a mounted volume would be used for a larger/persisted corpus)
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("oss_docs")
collection.add(
    embeddings=doc_vectors.tolist(),
    documents=chunks,
    metadatas=metadatas,
    ids=ids,
)
print(f"Indexed {collection.count()} chunks from {len(set(m['file_name'] for m in metadatas))} docs.")


def answer(query, top_k):
    if not query or not query.strip():
        return "Type a question above, e.g. \"What observability signals does tbcontracts-mcp emit?\""

    q_vec = vectorizer.transform([query]).toarray().tolist()
    results = collection.query(query_embeddings=q_vec, n_results=int(top_k))

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    if not docs:
        return "No matching chunks found."

    out = []
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists), 1):
        out.append(
            f"### Result {i}  ·  source: `{meta['file_name']}`  ·  distance: {dist:.3f}\n\n"
            f"{doc.strip()}\n"
        )
    return "\n---\n".join(out)


EXAMPLES = [
    "How does the CannotEvaluate result work in lambda-preflight?",
    "How does tbcontracts decide which agent to take tokens from during reallocation?",
    "What observability signals does tbcontracts-mcp emit?",
    "What is the licensing situation for token-budget-contracts?",
]

with gr.Blocks(title="RAG over my OSS docs") as demo:
    gr.Markdown(
        "# RAG Search — My Own Published Libraries\n"
        "Ask a question about **lambda-preflight**, **token-budget-contracts**, "
        "or **tbcontracts-mcp** (all published on PyPI). This is a retrieval-only "
        "RAG pipeline — it returns the actual matching documentation text, not a "
        "generated answer, so there's no hallucination risk.\n\n"
        "**Pipeline:** chunk → TF-IDF embed → Chroma vector store → cosine-similarity retrieval."
    )
    with gr.Row():
        query_box = gr.Textbox(label="Your question", placeholder="e.g. What observability signals does tbcontracts-mcp emit?")
    top_k_slider = gr.Slider(1, 5, value=2, step=1, label="Number of results (top-k)")
    submit_btn = gr.Button("Search", variant="primary")
    output_box = gr.Markdown()

    gr.Examples(examples=EXAMPLES, inputs=query_box)

    submit_btn.click(fn=answer, inputs=[query_box, top_k_slider], outputs=output_box)
    query_box.submit(fn=answer, inputs=[query_box, top_k_slider], outputs=output_box)

if __name__ == "__main__":
    demo.launch()
