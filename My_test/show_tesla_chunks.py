"""Show all chunks from Tesla Motors PDF"""
import json
import sys
import io
from pathlib import Path

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent
METADATA_PATH = ROOT / "faiss_index" / "metadata.json"

if not METADATA_PATH.exists():
    print("[ERROR] FAISS index not found. Run: python mcp_server_2.py index")
    exit(1)

with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Filter chunks from Tesla Motors PDF
tesla_chunks = []
for idx, data in enumerate(metadata):
    if "Tesla_Motors_IP_Open_Innovation" in data.get('doc', ''):
        tesla_chunks.append((idx, data))

print("=" * 80)
print(f"TESLA MOTORS PDF CHUNKS ({len(tesla_chunks)} chunks found)")
print("=" * 80)

if not tesla_chunks:
    print("\n[WARNING] No chunks found for Tesla Motors PDF")
    print("Available documents:")
    docs = set(data.get('doc', '') for data in metadata)
    for doc in sorted(docs):
        print(f"  - {doc}")
    exit(1)

# Sort by chunk_index if available, otherwise by metadata index
tesla_chunks.sort(key=lambda x: x[1].get('chunk_index', x[0]))

for i, (idx, data) in enumerate(tesla_chunks, 1):
    chunk_id = data.get('chunk_id', f'chunk_{idx}')
    chunk_index = data.get('chunk_index', 'N/A')
    chunk_position = data.get('chunk_position', 'N/A')
    section = data.get('section', 'N/A')
    page = data.get('page', 'N/A')
    word_count = data.get('word_count', 'N/A')
    char_count = data.get('char_count', 'N/A')
    
    chunk_text = data.get('chunk', '')
    
    print(f"\n{'=' * 80}")
    print(f"CHUNK {i}/{len(tesla_chunks)}")
    print(f"{'=' * 80}")
    print(f"ID: {chunk_id}")
    print(f"Index: {chunk_index} | Position: {chunk_position}")
    if section != 'N/A':
        print(f"Section: {section}")
    if page != 'N/A':
        print(f"Page: {page}")
    print(f"Words: {word_count} | Chars: {char_count}")
    print(f"\nCONTENT:")
    print("-" * 80)
    # Print chunk text (truncate if too long for readability)
    if len(chunk_text) > 2000:
        print(chunk_text[:2000])
        print(f"\n... [truncated, {len(chunk_text) - 2000} more characters] ...")
    else:
        print(chunk_text)
    print("-" * 80)

print(f"\n{'=' * 80}")
print(f"TOTAL: {len(tesla_chunks)} chunks from Tesla Motors PDF")
print(f"{'=' * 80}")

