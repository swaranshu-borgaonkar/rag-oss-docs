"""
Minimal RAG pipeline over Swaranshu's own OSS project docs
(lambda-preflight, token-budget-contracts, tbcontracts-mcp).

Stack: manual chunking + TF-IDF embeddings (scikit-learn, fully local,
       no network/API key needed) + Chroma (vector store, persisted).

Note: a neural embedding model (e.g. sentence-transformers) would give
richer semantic retrieval, but this sandbox's network policy blocks
huggingface.co, so this pipeline uses TF-IDF vectors instead -- still a
real embedding representation, indexed and queried through a real vector
store, just a simpler one. Swap in HuggingFaceEmbedding() for production
use in an environment with model-hub access.
"""

import glob
import os
import re

import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer

DOCS_DIR = "/home/claude/rag-project/docs"
CHROMA_PATH = "/home/claude/rag-project/chroma_db"
COLLECTION_NAME = "oss_docs"
CHUNK_SIZE = 400   # chars
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


print(f"Loading + chunking docs from {DOCS_DIR} ...")
chunks, metadatas, ids = load_and_chunk(DOCS_DIR)
print(f"Produced {len(chunks)} chunks from {len(glob.glob(os.path.join(DOCS_DIR, '*.md')))} source files.")

# Fit a TF-IDF vectorizer over the corpus -- this is our local "embedding model"
print("Fitting TF-IDF vectorizer (local embedding step)...")
vectorizer = TfidfVectorizer(stop_words="english", max_features=512)
doc_vectors = vectorizer.fit_transform(chunks).toarray()
print(f"Embedded {doc_vectors.shape[0]} chunks into {doc_vectors.shape[1]}-dim vectors.")

# Store in Chroma (real vector DB, persisted to disk)
print("Storing vectors in Chroma...")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
try:
    chroma_client.delete_collection(COLLECTION_NAME)
except Exception:
    pass
collection = chroma_client.create_collection(COLLECTION_NAME)
collection.add(
    embeddings=doc_vectors.tolist(),
    documents=chunks,
    metadatas=metadatas,
    ids=ids,
)
print(f"Chroma collection '{COLLECTION_NAME}' now has {collection.count()} chunks.")


def retrieve(query, top_k=2):
    q_vec = vectorizer.transform([query]).toarray().tolist()
    results = collection.query(query_embeddings=q_vec, n_results=top_k)
    return results


test_queries = [
    "How does the CannotEvaluate result work in lambda-preflight?",
    "How does tbcontracts decide which agent to take tokens from during reallocation?",
    "What observability signals does tbcontracts-mcp emit?",
    "What is the licensing situation for token-budget-contracts?",
]

print("\n" + "=" * 70)
print("RETRIEVAL RESULTS (query -> top matching chunks)")
print("=" * 70)

for q in test_queries:
    print(f"\nQUERY: {q}")
    res = retrieve(q, top_k=2)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists), 1):
        snippet = doc.strip().replace("\n", " ")[:180]
        print(f"  [{i}] distance={dist:.3f} source={meta['file_name']}")
        print(f"      \"{snippet}...\"")

print("\n" + "=" * 70)
print("Done. Vector DB persisted at:", CHROMA_PATH)
print("Collection count:", collection.count())
