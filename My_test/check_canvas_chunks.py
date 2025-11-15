"""Check Canvas LMS PDF chunks in detail"""
import json
from pathlib import Path

idx_path = Path('faiss_index/metadata.json')
data = json.loads(idx_path.read_text())

canvas_chunks = [c for c in data if 'How to use Canvas LMS.pdf' in c.get('doc', '')]

print(f"Found {len(canvas_chunks)} chunks from Canvas LMS PDF\n")

for i, c in enumerate(canvas_chunks):
    print(f"Chunk {i+1} (ID: {c.get('chunk_id', 'N/A')}):")
    chunk_text = c.get('chunk', '')
    print(f"Length: {len(chunk_text)} characters")
    print(f"Content preview:\n{chunk_text[:800]}")
    print("\n" + "="*80 + "\n")

