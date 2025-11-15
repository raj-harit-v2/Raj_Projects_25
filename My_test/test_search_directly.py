"""Test search_stored_documents directly to see why it's not finding chunks"""
import json
import faiss
import numpy as np
import requests
from pathlib import Path
import sys

ROOT = Path(__file__).parent
INDEX_PATH = ROOT / "faiss_index" / "index.bin"
METADATA_PATH = ROOT / "faiss_index" / "metadata.json"
EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

def get_embedding(text: str) -> np.ndarray:
    result = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    result.raise_for_status()
    return np.array(result.json()["embedding"], dtype=np.float32)

print("=" * 80)
print("TESTING search_stored_documents DIRECTLY")
print("=" * 80)

# Check if index exists
if not INDEX_PATH.exists():
    print(f"[ERROR] Index not found: {INDEX_PATH}")
    sys.exit(1)

if not METADATA_PATH.exists():
    print(f"[ERROR] Metadata not found: {METADATA_PATH}")
    sys.exit(1)

# Load index and metadata
print("\n1. Loading index and metadata...")
index = faiss.read_index(str(INDEX_PATH))
with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(f"   Index dimensions: {index.d}")
print(f"   Total chunks in index: {index.ntotal}")
print(f"   Total metadata entries: {len(metadata)}")

# Test query
query = "Don Tapscott and Anthony Williams"
print(f"\n2. Testing query: '{query}'")

# Get embedding
print("   Getting embedding...")
query_vec = get_embedding(query).reshape(1, -1)
print(f"   Embedding shape: {query_vec.shape}")

# Search
print("   Searching index...")
D, I = index.search(query_vec, k=10)
print(f"   Found {len(I[0])} results")

# Process results like search_stored_documents does
results = []
for rank, idx in enumerate(I[0]):
    if idx < len(metadata):
        distance = D[0][rank]
        data = metadata[idx]
        chunk_text = data.get('chunk', '')
        doc_name = data.get('doc', '')
        
        # Check if chunk contains the entities
        chunk_lower = chunk_text.lower()
        has_tapscott = 'tapscott' in chunk_lower
        has_williams = 'williams' in chunk_lower and 'anthony' in chunk_lower
        
        print(f"\n   Result {rank+1}:")
        print(f"     Index: {idx}")
        print(f"     Distance: {distance:.2f}")
        print(f"     Doc: {doc_name}")
        print(f"     Has Tapscott: {has_tapscott}")
        print(f"     Has Williams: {has_williams}")
        print(f"     Chunk length: {len(chunk_text)}")
        print(f"     Preview: {chunk_text[:100]}...")
        
        # Build reference like search_stored_documents does
        ref_parts = [f"Source: {doc_name}"]
        ref_parts.append(f"ID: {data.get('chunk_id', 'unknown')}")
        
        if 'chunk_position' in data:
            ref_parts.append(f"Position: {data['chunk_position']}")
        
        reference = " | ".join(ref_parts)
        
        # Format like search_stored_documents
        result_str = f"{chunk_text}\n[{reference}]"
        results.append(result_str)

print(f"\n3. Final results count: {len(results)}")
if results:
    print(f"   First result length: {len(results[0])}")
    print(f"   First result preview: {results[0][:200]}...")
else:
    print("   [ERROR] No results returned!")

# Check for Tesla PDF chunks
print(f"\n4. Checking for Tesla PDF chunks in metadata...")
tesla_chunks = [data for data in metadata if "Tesla_Motors_IP_Open_Innovation" in data.get('doc', '')]
print(f"   Tesla PDF chunks in metadata: {len(tesla_chunks)}")

if tesla_chunks:
    for i, data in enumerate(tesla_chunks[:3], 1):
        chunk_text = data.get('chunk', '').lower()
        has_tapscott = 'tapscott' in chunk_text
        has_williams = 'williams' in chunk_text and 'anthony' in chunk_text
        print(f"   Chunk {i}: Tapscott={has_tapscott}, Williams={has_williams}")

print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)
if len(results) == 0:
    print("[ERROR] search_stored_documents would return empty list!")
    print("Possible causes:")
    print("  1. Index and metadata mismatch")
    print("  2. Embedding model issue")
    print("  3. Search parameters issue")
else:
    print(f"[OK] search_stored_documents would return {len(results)} results")
    if any('tapscott' in r.lower() and 'williams' in r.lower() for r in results):
        print("[OK] Results contain Tapscott and Williams")
    else:
        print("[WARNING] Results don't contain both entities")

