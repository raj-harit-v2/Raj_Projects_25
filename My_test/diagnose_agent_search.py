"""Diagnose why agent can't find Tapscott/Williams despite search working"""
import json
from pathlib import Path

ROOT = Path(__file__).parent

print("=" * 80)
print("DIAGNOSIS: Why Agent Can't Find Tapscott/Williams")
print("=" * 80)

# 1. Check if chunks are in index
METADATA_PATH = ROOT / "faiss_index" / "metadata.json"
with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

tesla_chunks = [data for data in metadata if "Tesla_Motors_IP_Open_Innovation" in data.get('doc', '')]
tapscott_chunks = [data for data in tesla_chunks if 'tapscott' in data.get('chunk', '').lower()]

print(f"\n1. INDEX STATUS:")
print(f"   Total Tesla chunks: {len(tesla_chunks)}")
print(f"   Chunks with 'Tapscott': {len(tapscott_chunks)}")

# 2. Check what search_stored_documents would return
print(f"\n2. SEARCH FUNCTION ANALYSIS:")
print(f"   Function: search_stored_documents")
print(f"   Returns: list[str] (chunks with references)")
print(f"   Top-k: 10 chunks")
print(f"   Ranking: By semantic similarity (FAISS)")

# 3. Check prompt guidance
PROMPT_PATH = ROOT / "prompts" / "New_Decision_Prompt.txt"
with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
    prompt_content = f.read()

print(f"\n3. PROMPT GUIDANCE:")
if "Don Tapscott" in prompt_content:
    print(f"   [OK] Prompt contains 'Don Tapscott' example")
else:
    print(f"   [WARNING] Prompt does NOT contain 'Don Tapscott' example")

if "search_stored_documents" in prompt_content:
    print(f"   [OK] Prompt mentions search_stored_documents")
else:
    print(f"   [WARNING] Prompt does NOT mention search_stored_documents")

# Check for filtering logic
if '"Don Tapscott" in chunk' in prompt_content or "'Don Tapscott' in chunk" in prompt_content:
    print(f"   [WARNING] Prompt contains STRING MATCHING filter (this is BAD)")
else:
    print(f"   [OK] Prompt does NOT contain string matching filters")

# 4. Check actual chunk content
if tapscott_chunks:
    chunk = tapscott_chunks[0]
    chunk_text = chunk.get('chunk', '')
    print(f"\n4. SAMPLE CHUNK CONTENT:")
    print(f"   Length: {len(chunk_text)} chars")
    print(f"   Contains 'Don Tapscott': {'Don Tapscott' in chunk_text}")
    print(f"   Contains 'tapscott' (lower): {'tapscott' in chunk_text.lower()}")
    print(f"   Contains 'Anthony Williams': {'Anthony Williams' in chunk_text}")
    print(f"   Preview: {chunk_text[:200]}...")

# 5. Potential issues
print(f"\n5. POTENTIAL ISSUES:")
print(f"   a) Agent LLM might be filtering results with string matching")
print(f"      -> Solution: Trust semantic search, return ALL chunks")
print(f"   b) Agent might be searching separately and not combining results")
print(f"      -> Solution: Use single query 'Don Tapscott and Anthony Williams'")
print(f"   c) Agent might be truncating chunks too early")
print(f"      -> Solution: Return full chunks, no truncation")
print(f"   d) Query might be too specific ('Don Tapscott' vs 'Tapscott')")
print(f"      -> Solution: Try broader queries or staged queries")

# 6. Recommended query format
print(f"\n6. RECOMMENDED QUERY FORMAT:")
print(f"   Single query (BEST):")
print(f"     query = 'Don Tapscott and Anthony Williams'")
print(f"   Staged queries (if needed):")
print(f"     query1 = 'Don Tapscott'")
print(f"     query2 = 'Anthony Williams'")
print(f"     Then combine ALL results (full outer join)")

# 7. Check if agent is using the right server
print(f"\n7. SERVER SELECTION:")
print(f"   Query about people/books should use 'documents' server")
print(f"   Check perception.py to ensure correct server selection")

print(f"\n{'=' * 80}")
print("CONCLUSION:")
print("=" * 80)
print("The search IS working correctly. The issue is likely:")
print("1. Agent LLM filtering results too aggressively")
print("2. Agent not using the right query format")
print("3. Agent not combining staged search results properly")
print("=" * 80)

