"""Analyze Canvas LMS PDF processing breakdown"""
import json
from pathlib import Path

print("=" * 80)
print("CANVAS LMS PDF PROCESSING ANALYSIS")
print("=" * 80)

# Check metadata
idx_path = Path('faiss_index/metadata.json')
if idx_path.exists():
    data = json.loads(idx_path.read_text())
    canvas_chunks = [c for c in data if 'Canvas' in c.get('doc', '')]
    
    print(f"\nTotal Canvas LMS chunks in index: {len(canvas_chunks)}")
    
    if canvas_chunks:
        print(f"\nChunks breakdown:")
        for i, chunk in enumerate(canvas_chunks[:10], 1):
            chunk_text = chunk['chunk']
            # Count images in this chunk
            image_count = chunk_text.count('**Image:**')
            print(f"\n  Chunk {i} (ID: {chunk.get('chunk_id', 'N/A')}):")
            print(f"    Length: {len(chunk_text)} characters")
            print(f"    Images: {image_count}")
            if image_count > 0:
                # Extract first image caption
                import re
                matches = re.findall(r'\*\*Image:\*\* (.+?)(?=\*\*Image:\*\*|$)', chunk_text, re.DOTALL)
                if matches:
                    print(f"    First caption preview: {matches[0][:100]}...")
            print(f"    Content preview: {chunk_text[:200]}...")
    else:
        print("\n[WARNING] No Canvas LMS chunks found in index!")
        print("The PDF may not have been processed yet.")
        
        # Check what documents ARE in the index
        docs = set(c['doc'] for c in data)
        print(f"\nDocuments currently in index ({len(docs)}):")
        for doc in sorted(docs):
            count = len([c for c in data if c['doc'] == doc])
            print(f"  - {doc} ({count} chunks)")
else:
    print("\n[ERROR] Index file not found!")

# Check cache
cache_path = Path('faiss_index/doc_index_cache.json')
if cache_path.exists():
    cache = json.loads(cache_path.read_text())
    print(f"\n\nCache status:")
    print(f"  Canvas LMS in cache: {'How to use Canvas LMS.pdf' in cache}")
    if 'How to use Canvas LMS.pdf' in cache:
        print(f"  Cache hash: {cache['How to use Canvas LMS.pdf']}")

print("\n" + "=" * 80)

