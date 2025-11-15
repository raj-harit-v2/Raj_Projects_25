"""Analyze different join strategies for relationship queries"""
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
print("ANALYZING JOIN STRATEGIES FOR RELATIONSHIP QUERIES")
print("=" * 80)

# Load index and metadata
index = faiss.read_index(str(INDEX_PATH))
with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Test relationship queries
test_cases = [
    {
        "name": "Don Tapscott and Anthony Williams",
        "entity1": "Don Tapscott",
        "entity2": "Anthony Williams",
        "combined": "Don Tapscott and Anthony Williams"
    },
    {
        "name": "Gensol and Go-Auto",
        "entity1": "Gensol",
        "entity2": "Go-Auto",
        "combined": "Gensol Go-Auto relationship"
    }
]

for test in test_cases:
    print(f"\n{'=' * 80}")
    print(f"TEST CASE: {test['name']}")
    print(f"{'=' * 80}")
    
    # Strategy 1: Combined query (INNER JOIN semantics - both entities together)
    print(f"\n1. COMBINED QUERY (INNER JOIN - both entities together):")
    print(f"   Query: '{test['combined']}'")
    query_vec = get_embedding(test['combined']).reshape(1, -1)
    D, I = index.search(query_vec, k=10)
    
    chunks_with_both = []
    chunks_with_one = []
    
    for rank in range(len(I[0])):
        idx = I[0][rank]
        if idx < len(metadata):
            data = metadata[idx]
            chunk_text = data.get('chunk', '').lower()
            doc_name = data.get('doc', '')
            distance = D[0][rank]
            
            has_entity1 = test['entity1'].lower() in chunk_text
            has_entity2 = test['entity2'].lower() in chunk_text
            
            if has_entity1 and has_entity2:
                chunks_with_both.append({
                    'rank': rank + 1,
                    'distance': distance,
                    'doc': doc_name,
                    'preview': chunk_text[:100]
                })
            elif has_entity1 or has_entity2:
                chunks_with_one.append({
                    'rank': rank + 1,
                    'distance': distance,
                    'doc': doc_name,
                    'has': test['entity1'] if has_entity1 else test['entity2'],
                    'preview': chunk_text[:100]
                })
    
    print(f"   Chunks with BOTH entities: {len(chunks_with_both)}")
    for chunk in chunks_with_both[:3]:
        print(f"     Rank {chunk['rank']}: {chunk['doc'][:50]} (distance: {chunk['distance']:.2f})")
    
    print(f"   Chunks with ONE entity only: {len(chunks_with_one)}")
    for chunk in chunks_with_one[:3]:
        print(f"     Rank {chunk['rank']}: {chunk['doc'][:50]} (has: {chunk['has']}, distance: {chunk['distance']:.2f})")
    
    # Strategy 2: Separate queries (FULL OUTER JOIN - all from both)
    print(f"\n2. SEPARATE QUERIES (FULL OUTER JOIN - all from both):")
    print(f"   Query 1: '{test['entity1']}'")
    query1_vec = get_embedding(test['entity1']).reshape(1, -1)
    D1, I1 = index.search(query1_vec, k=10)
    
    print(f"   Query 2: '{test['entity2']}'")
    query2_vec = get_embedding(test['entity2']).reshape(1, -1)
    D2, I2 = index.search(query2_vec, k=10)
    
    # Collect all unique chunks
    all_chunks = {}
    for rank in range(len(I1[0])):
        idx = I1[0][rank]
        if idx < len(metadata):
            data = metadata[idx]
            chunk_id = data.get('chunk_id', f'chunk_{idx}')
            chunk_text = data.get('chunk', '').lower()
            all_chunks[chunk_id] = {
                'doc': data.get('doc', ''),
                'chunk_text': chunk_text,
                'has_entity1': True,
                'has_entity2': test['entity2'].lower() in chunk_text,
                'distance1': D1[0][rank],
                'distance2': None,
                'rank1': rank + 1,
                'rank2': None
            }
    
    for rank in range(len(I2[0])):
        idx = I2[0][rank]
        if idx < len(metadata):
            data = metadata[idx]
            chunk_id = data.get('chunk_id', f'chunk_{idx}')
            chunk_text = data.get('chunk', '').lower()
            if chunk_id in all_chunks:
                # Already in set, update
                all_chunks[chunk_id]['has_entity2'] = True
                all_chunks[chunk_id]['distance2'] = D2[0][rank]
                all_chunks[chunk_id]['rank2'] = rank + 1
            else:
                # New chunk
                all_chunks[chunk_id] = {
                    'doc': data.get('doc', ''),
                    'chunk_text': chunk_text,
                    'has_entity1': test['entity1'].lower() in chunk_text,
                    'has_entity2': True,
                    'distance1': None,
                    'distance2': D2[0][rank],
                    'rank1': None,
                    'rank2': rank + 1
                }
    
    # Categorize
    chunks_both_separate = [c for c in all_chunks.values() if c['has_entity1'] and c['has_entity2']]
    chunks_only_entity1 = [c for c in all_chunks.values() if c['has_entity1'] and not c['has_entity2']]
    chunks_only_entity2 = [c for c in all_chunks.values() if not c['has_entity1'] and c['has_entity2']]
    
    print(f"   Total unique chunks: {len(all_chunks)}")
    print(f"   Chunks with BOTH entities: {len(chunks_both_separate)}")
    print(f"   Chunks with ONLY {test['entity1']}: {len(chunks_only_entity1)}")
    print(f"   Chunks with ONLY {test['entity2']}: {len(chunks_only_entity2)}")
    
    # Strategy 3: INNER JOIN (only chunks with both entities)
    print(f"\n3. INNER JOIN (only chunks with both entities):")
    inner_join_chunks = [c for c in all_chunks.values() if c['has_entity1'] and c['has_entity2']]
    print(f"   Chunks with BOTH: {len(inner_join_chunks)}")
    for chunk in inner_join_chunks[:3]:
        print(f"     Doc: {chunk['doc'][:50]}")
        dist1_str = f"{chunk['distance1']:.2f}" if chunk['distance1'] is not None else "N/A"
        dist2_str = f"{chunk['distance2']:.2f}" if chunk['distance2'] is not None else "N/A"
        print(f"       Distance1: {dist1_str}")
        print(f"       Distance2: {dist2_str}")
    
    # Strategy 4: LEFT JOIN (all from entity1, matching from entity2)
    print(f"\n4. LEFT JOIN (all from {test['entity1']}, matching from {test['entity2']}):")
    left_join_chunks = [c for c in all_chunks.values() if c['has_entity1']]
    print(f"   Total chunks: {len(left_join_chunks)}")
    print(f"   With both: {sum(1 for c in left_join_chunks if c['has_entity2'])}")
    print(f"   Only entity1: {sum(1 for c in left_join_chunks if not c['has_entity2'])}")
    
    # Recommendation
    print(f"\n5. RECOMMENDATION FOR THIS CASE:")
    if len(chunks_with_both) > 0:
        print(f"   [BEST] Use COMBINED QUERY (Strategy 1) - finds {len(chunks_with_both)} chunks with both entities")
        print(f"   Combined query already returns chunks where both appear together")
    elif len(chunks_both_separate) > 0:
        print(f"   [GOOD] Use SEPARATE QUERIES + INNER JOIN (Strategy 3)")
        print(f"   Find {len(chunks_both_separate)} chunks with both entities from separate searches")
    else:
        print(f"   [FALLBACK] Use FULL OUTER JOIN (Strategy 2)")
        print(f"   No chunks with both entities found - return all chunks from both searches")
        print(f"   Let LLM synthesize relationship from separate information")

print(f"\n{'=' * 80}")
print("GENERAL RECOMMENDATION")
print(f"{'=' * 80}")
print("""
For relationship queries, use a HIERARCHICAL approach:

1. FIRST: Combined query (INNER JOIN semantics)
   - Query: "entity1 and entity2" or "entity1 entity2 relationship"
   - Returns chunks where both entities appear together
   - Best for finding direct relationships

2. FALLBACK: Separate queries + INNER JOIN
   - Search each entity separately
   - Keep only chunks that contain BOTH entities
   - Good when combined query doesn't work

3. LAST RESORT: FULL OUTER JOIN
   - Search each entity separately
   - Return ALL chunks from both searches
   - Let LLM synthesize relationship from separate information
   - Use when no chunks contain both entities together

The current prompt uses FULL OUTER JOIN, which is safe but may return irrelevant chunks.
For relationship queries, INNER JOIN (combined query first) is more precise.
""")

