"""Show summary of Tesla Motors PDF chunks"""
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
print(f"TESLA MOTORS PDF CHUNKS SUMMARY ({len(tesla_chunks)} chunks)")
print("=" * 80)

if not tesla_chunks:
    print("\n[WARNING] No chunks found for Tesla Motors PDF")
    exit(1)

# Sort by chunk_index if available, otherwise by metadata index
tesla_chunks.sort(key=lambda x: x[1].get('chunk_index', x[0]))

print(f"\nDocument: Tesla_Motors_IP_Open_Innovation_and_the_Carbon_Crisis_-_Matthew_Rimmer.pdf")
print(f"Total Chunks: {len(tesla_chunks)}\n")

for i, (idx, data) in enumerate(tesla_chunks, 1):
    chunk_id = data.get('chunk_id', f'chunk_{idx}')
    chunk_index = data.get('chunk_index', idx)
    chunk_position = data.get('chunk_position', f'{i}/{len(tesla_chunks)}')
    section = data.get('section', None)
    page = data.get('page', None)
    word_count = data.get('word_count', len(data.get('chunk', '').split()))
    char_count = data.get('char_count', len(data.get('chunk', '')))
    
    chunk_text = data.get('chunk', '')
    preview = chunk_text[:150].replace('\n', ' ') + ("..." if len(chunk_text) > 150 else "")
    
    print(f"\nChunk {i}/{len(tesla_chunks)}")
    print(f"  ID: {chunk_id}")
    print(f"  Position: {chunk_position} | Words: {word_count} | Chars: {char_count}")
    if section:
        print(f"  Section: {section}")
    if page:
        print(f"  Page: {page}")
    print(f"  Preview: {preview}")

print(f"\n{'=' * 80}")
print(f"SUMMARY: {len(tesla_chunks)} chunks total")
print(f"{'=' * 80}")

# Check for Don Tapscott and Anthony Williams mentions
tapscott_mentions = []
williams_mentions = []
for idx, data in tesla_chunks:
    chunk_text = data.get('chunk', '').lower()
    if 'tapscott' in chunk_text:
        tapscott_mentions.append(data.get('chunk_id', f'chunk_{idx}'))
    if 'williams' in chunk_text and 'anthony' in chunk_text:
        williams_mentions.append(data.get('chunk_id', f'chunk_{idx}'))

if tapscott_mentions or williams_mentions:
    print(f"\nMENTIONS FOUND:")
    if tapscott_mentions:
        print(f"  Don Tapscott: Found in {len(tapscott_mentions)} chunk(s)")
        for chunk_id in tapscott_mentions:
            print(f"    - {chunk_id}")
    if williams_mentions:
        print(f"  Anthony Williams: Found in {len(williams_mentions)} chunk(s)")
        for chunk_id in williams_mentions:
            print(f"    - {chunk_id}")

