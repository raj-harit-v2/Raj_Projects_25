"""Test search for Don Tapscott and Anthony Williams"""
import json
import faiss
import numpy as np
import requests
from pathlib import Path

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
print("TESTING SEARCH FOR DON TAPSCOTT AND ANTHONY WILLIAMS")
print("=" * 80)

# Load index and metadata
index = faiss.read_index(str(INDEX_PATH))
with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Test queries
test_queries = [
    "Don Tapscott",
    "Anthony Williams",
    "Don Tapscott and Anthony Williams",
    "Tapscott Williams",
    "MacroWikinomics",
    "open source clean technology"
]

for query in test_queries:
    print(f"\n{'=' * 80}")
    print(f"QUERY: '{query}'")
    print(f"{'=' * 80}")
    
    # Get embedding
    query_vec = get_embedding(query).reshape(1, -1)
    
    # Search
    D, I = index.search(query_vec, k=10)
    
    # Check results
    found_tapscott = False
    found_williams = False
    found_tesla = False
    
    print(f"\nTop 10 results:")
    for rank, idx in enumerate(I[0], 1):
        if idx < len(metadata):
            data = metadata[idx]
            doc_name = data.get('doc', '')
            chunk_text = data.get('chunk', '').lower()
            
            has_tapscott = 'tapscott' in chunk_text
            has_williams = 'williams' in chunk_text and 'anthony' in chunk_text
            is_tesla = 'tesla' in doc_name.lower()
            
            if has_tapscott:
                found_tapscott = True
            if has_williams:
                found_williams = True
            if is_tesla:
                found_tesla = True
            
            distance = D[0][rank-1]
            preview = chunk_text[:100].replace('\n', ' ')
            
            print(f"\n  Rank {rank}: Distance={distance:.4f}")
            print(f"    Doc: {doc_name}")
            print(f"    Has Tapscott: {has_tapscott}")
            print(f"    Has Williams: {has_williams}")
            print(f"    Preview: {preview}...")
    
    print(f"\n  Summary:")
    print(f"    Found Tapscott: {found_tapscott}")
    print(f"    Found Williams: {found_williams}")
    print(f"    Found Tesla PDF: {found_tesla}")

print(f"\n{'=' * 80}")
print("ANALYSIS")
print(f"{'=' * 80}")

# Check if Tesla chunks are in the index
tesla_chunks = [data for data in metadata if "Tesla_Motors_IP_Open_Innovation" in data.get('doc', '')]
print(f"\nTesla PDF chunks in index: {len(tesla_chunks)}")

# Check embeddings for Tesla chunks
if tesla_chunks:
    print("\nChecking embeddings for Tesla chunks...")
    for i, data in enumerate(tesla_chunks[:3], 1):
        chunk_text = data.get('chunk', '')
        has_tapscott = 'tapscott' in chunk_text.lower()
        has_williams = 'williams' in chunk_text.lower() and 'anthony' in chunk_text.lower()
        print(f"  Chunk {i}: Tapscott={has_tapscott}, Williams={has_williams}, Length={len(chunk_text)}")

