"""List all documents in the FAISS index"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
METADATA_PATH = ROOT / "faiss_index" / "metadata.json"

if not METADATA_PATH.exists():
    print("[ERROR] FAISS index not found. Run: python mcp_server_2.py index")
    exit(1)

with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Get unique documents
docs = {}
for data in metadata:
    doc_name = data.get('doc', 'unknown')
    if doc_name not in docs:
        docs[doc_name] = 0
    docs[doc_name] += 1

print("=" * 80)
print("INDEXED DOCUMENTS")
print("=" * 80)
print(f"\nTotal chunks: {len(metadata)}")
print(f"Unique documents: {len(docs)}\n")

for doc, count in sorted(docs.items()):
    print(f"  - {doc} ({count} chunks)")

print("\n" + "=" * 80)

