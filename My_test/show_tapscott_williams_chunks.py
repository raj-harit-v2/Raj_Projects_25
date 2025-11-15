"""Show chunks containing Don Tapscott and Anthony Williams"""
import json
import sys
import io
from pathlib import Path

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent
METADATA_PATH = ROOT / "faiss_index" / "metadata.json"

with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Find chunks with Don Tapscott and Anthony Williams
relevant_chunks = []
for idx, data in enumerate(metadata):
    if "Tesla_Motors_IP_Open_Innovation" in data.get('doc', ''):
        chunk_text = data.get('chunk', '').lower()
        if 'tapscott' in chunk_text or ('williams' in chunk_text and 'anthony' in chunk_text):
            relevant_chunks.append((idx, data))

print("=" * 80)
print("CHUNKS CONTAINING DON TAPSCOTT AND/OR ANTHONY WILLIAMS")
print("=" * 80)
print(f"\nFound {len(relevant_chunks)} relevant chunk(s)\n")

for i, (idx, data) in enumerate(relevant_chunks, 1):
    chunk_id = data.get('chunk_id', f'chunk_{idx}')
    chunk_index = data.get('chunk_index', idx)
    chunk_position = data.get('chunk_position', 'N/A')
    word_count = data.get('word_count', len(data.get('chunk', '').split()))
    char_count = data.get('char_count', len(data.get('chunk', '')))
    
    chunk_text = data.get('chunk', '')
    
    print(f"{'=' * 80}")
    print(f"CHUNK {i} - {chunk_id}")
    print(f"{'=' * 80}")
    print(f"Position: {chunk_position} | Words: {word_count} | Chars: {char_count}")
    print(f"\nFULL CONTENT:")
    print("-" * 80)
    print(chunk_text)
    print("-" * 80)
    print()

print(f"{'=' * 80}")
print(f"TOTAL: {len(relevant_chunks)} chunk(s) containing Don Tapscott and/or Anthony Williams")
print(f"{'=' * 80}")

