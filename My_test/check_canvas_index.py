"""Check if Canvas LMS content is in the FAISS index"""
import json
from pathlib import Path

idx_path = Path('faiss_index/metadata.json')
if not idx_path.exists():
    print("Index not found!")
    exit(1)

data = json.loads(idx_path.read_text())
canvas_chunks = [c for c in data if 'Canvas' in c.get('chunk', '') or 'canvas' in c.get('chunk', '').lower() or 'LMS' in c.get('chunk', '')]

print(f"Found {len(canvas_chunks)} chunks containing Canvas/LMS")
print(f"Total chunks in index: {len(data)}\n")

for i, c in enumerate(canvas_chunks[:5]):
    print(f"Chunk {i+1} (from {c['doc']}):")
    print(f"{c['chunk'][:500]}...")
    print("\n" + "="*80 + "\n")

# Check for image captions
image_chunks = [c for c in data if '**Image:**' in c.get('chunk', '')]
print(f"\nFound {len(image_chunks)} chunks containing image captions")
if image_chunks:
    print("\nSample image caption chunk:")
    print(image_chunks[0]['chunk'][:300] + "...")

