#!/usr/bin/env python3
"""
RAG simples: busca BM25 nos docs convertidos + resposta via Claude
Uso: python3 rag_query.py "sua pergunta aqui"
"""

import sys
import os
import re
import math
import json
import urllib.request
from pathlib import Path

DOCS_DIR = Path("/root/.openclaw/workspace/docling-output")
# O RAG busca em todos os .md dentro de docling-output (incluindo subpastas)
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Chunking ─────────────────────────────────────────────────────────────────

def load_chunks(docs_dir: Path, chunk_size: int = 400, overlap: int = 50):
    chunks = []
    for md_file in docs_dir.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        words = text.split()
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append({"source": md_file.name, "text": chunk})
            i += chunk_size - overlap
    return chunks

# ── BM25 ─────────────────────────────────────────────────────────────────────

def tokenize(text: str):
    return re.findall(r'\w+', text.lower())

def bm25_score(query_tokens, doc_tokens, avgdl, k1=1.5, b=0.75):
    dl = len(doc_tokens)
    freq = {}
    for t in doc_tokens:
        freq[t] = freq.get(t, 0) + 1
    score = 0
    for t in query_tokens:
        f = freq.get(t, 0)
        if f == 0:
            continue
        idf = math.log(1 + 1)  # simplificado — corpus pequeno
        score += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avgdl))
    return score

def search(query: str, chunks: list, top_k: int = 5):
    query_tokens = tokenize(query)
    doc_tokens_list = [tokenize(c["text"]) for c in chunks]
    avgdl = sum(len(d) for d in doc_tokens_list) / max(len(doc_tokens_list), 1)
    scored = [
        (bm25_score(query_tokens, dt, avgdl), c)
        for c, dt in zip(chunks, doc_tokens_list)
    ]
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:top_k] if _ > 0]

# ── Claude ───────────────────────────────────────────────────────────────────

def ask_claude(question: str, context_chunks: list, api_key: str) -> str:
    context = "\n\n---\n\n".join(
        f"[{c['source']}]\n{c['text']}" for c in context_chunks
    )
    prompt = f"""Você é a Flávia, COO Digital da MENSURA e MIA Engenharia.
Responda à pergunta abaixo com base APENAS nas informações dos documentos fornecidos.
Se a informação não estiver nos documentos, diga claramente que não encontrou.

## Documentos
{context}

## Pergunta
{question}

## Resposta (em português, direta e objetiva):"""

    payload = json.dumps({
        "model": "claude-haiku-4-5",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["content"][0]["text"]

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 rag_query.py \"sua pergunta\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    if not ANTHROPIC_KEY:
        print("Erro: defina ANTHROPIC_API_KEY")
        sys.exit(1)

    print(f"🔍 Pergunta: {question}\n")
    chunks = load_chunks(DOCS_DIR)
    print(f"📄 {len(chunks)} chunks carregados de {DOCS_DIR}")

    relevant = search(question, chunks)
    print(f"✅ {len(relevant)} chunks relevantes encontrados\n")

    answer = ask_claude(question, relevant, ANTHROPIC_KEY)
    print("=" * 60)
    print(answer)
    print("=" * 60)

if __name__ == "__main__":
    main()
