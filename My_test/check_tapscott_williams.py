"""Check if Don Tapscott and Anthony Williams are in the indexed documents"""
import json
from pathlib import Path
import faiss
import numpy as np

ROOT = Path(__file__).parent
INDEX_PATH = ROOT / "faiss_index" / "index.bin"
METADATA_PATH = ROOT / "faiss_index" / "metadata.json"

print("Checking for Don Tapscott and Anthony Williams in indexed documents...\n")

if not INDEX_PATH.exists() or not METADATA_PATH.exists():
    print("[ERROR] FAISS index not found. Run: python mcp_server_2.py index")
    exit(1)

# Load metadata
with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(f"Total chunks in index: {len(metadata)}\n")

# Search for mentions
tapscott_chunks = []
williams_chunks = []
both_chunks = []

for idx, data in enumerate(metadata):
    chunk_text = data.get('chunk', '').lower()
    doc_name = data.get('doc', '')
    
    has_tapscott = 'tapscott' in chunk_text or 'don tapscott' in chunk_text
    has_williams = 'williams' in chunk_text or 'anthony williams' in chunk_text
    
    if has_tapscott:
        tapscott_chunks.append((idx, doc_name, chunk_text[:200]))
    if has_williams:
        williams_chunks.append((idx, doc_name, chunk_text[:200]))
    if has_tapscott and has_williams:
        both_chunks.append((idx, doc_name, chunk_text[:200]))

print("=" * 80)
print("SEARCH RESULTS")
print("=" * 80)

print(f"\nDon Tapscott mentions: {len(tapscott_chunks)}")
if tapscott_chunks:
    for idx, doc, preview in tapscott_chunks[:3]:
        print(f"  - Doc: {doc}")
        print(f"    Preview: {preview}...")
        print()

print(f"\nAnthony Williams mentions: {len(williams_chunks)}")
if williams_chunks:
    for idx, doc, preview in williams_chunks[:3]:
        print(f"  - Doc: {doc}")
        print(f"    Preview: {preview}...")
        print()

print(f"\nBoth mentioned together: {len(both_chunks)}")
if both_chunks:
    for idx, doc, preview in both_chunks[:3]:
        print(f"  - Doc: {doc}")
        print(f"    Preview: {preview}...")
        print()

# List unique documents
all_docs = set()
for data in metadata:
    if 'tapscott' in data.get('chunk', '').lower() or 'williams' in data.get('chunk', '').lower():
        all_docs.add(data.get('doc', ''))

if all_docs:
    print(f"\nDocuments containing these names: {len(all_docs)}")
    for doc in sorted(all_docs):
        print(f"  - {doc}")

print("\n" + "=" * 80)
if tapscott_chunks or williams_chunks:
    print("[OK] Don Tapscott and/or Anthony Williams found in indexed documents")
else:
    print("[WARNING] Not found in indexed documents")
print("=" * 80)

