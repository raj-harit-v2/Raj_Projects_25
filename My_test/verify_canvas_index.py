"""Verify Canvas LMS content in index"""
import json
from pathlib import Path

# Check metadata
idx_path = Path('faiss_index/metadata.json')
if idx_path.exists():
    data = json.loads(idx_path.read_text())
    canvas_chunks = [c for c in data if 'Canvas' in c.get('doc', '')]
    print(f"Canvas LMS chunks: {len(canvas_chunks)}")
    print(f"Total chunks: {len(data)}")
    if canvas_chunks:
        print(f"\nFirst chunk preview:")
        print(canvas_chunks[0]['chunk'][:500] + "...")
        # Check for image captions
        if '**Image:**' in canvas_chunks[0]['chunk']:
            print("\n[OK] Image captions found in chunks!")
        else:
            print("\n[WARN] No image caption markers found")
else:
    print("Index not found!")

# Check cache
cache_path = Path('faiss_index/doc_index_cache.json')
if cache_path.exists():
    cache = json.loads(cache_path.read_text())
    print(f"\nFiles in cache: {len(cache)}")
    print(f"Canvas LMS in cache: {'How to use Canvas LMS.pdf' in cache}")

