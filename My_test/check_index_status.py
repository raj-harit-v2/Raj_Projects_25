"""Check index status"""
import json
from pathlib import Path

# Check metadata
idx_path = Path('faiss_index/metadata.json')
if idx_path.exists():
    data = json.loads(idx_path.read_text())
    docs = set(c['doc'] for c in data)
    print('Documents in index:')
    for d in sorted(docs):
        count = len([c for c in data if c['doc'] == d])
        print(f'  - {d} ({count} chunks)')
    print(f'\nTotal chunks: {len(data)}')
    canvas_docs = [d for d in docs if 'Canvas' in d]
    print(f'Canvas LMS files: {len(canvas_docs)}')
    if canvas_docs:
        for doc in canvas_docs:
            chunks = [c for c in data if c['doc'] == doc]
            print(f'\n  {doc}: {len(chunks)} chunks')
            if chunks:
                print(f'  First chunk preview: {chunks[0]["chunk"][:200]}...')
else:
    print("Index not found!")

