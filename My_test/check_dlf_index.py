"""Check DLF document content in FAISS index"""

import json
import sys
from pathlib import Path

# Fix Unicode output for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load metadata
meta_path = Path("faiss_index/metadata.json")
metadata = json.loads(meta_path.read_text())

# Find DLF-related chunks
dlf_chunks = [m for m in metadata if 'DLF' in m['doc'] or 'dlf' in m['doc'].lower()]

print(f"Total chunks in index: {len(metadata)}")
print(f"DLF-related chunks: {len(dlf_chunks)}")
print(f"\nDocuments with DLF content:")
docs = set(c['doc'] for c in dlf_chunks)
for doc in docs:
    print(f"  - {doc}")

# Show sample chunks
print(f"\n=== Sample DLF Chunks ===")
for i, chunk in enumerate(dlf_chunks[:5], 1):
    print(f"\nChunk {i} from {chunk['doc']}:")
    print(f"  Content: {chunk['chunk'][:400]}...")
    
    # Check for payment-related keywords
    chunk_lower = chunk['chunk'].lower()
    keywords = ['anmol', 'singh', 'capbridge', 'paid', 'payment', 'amount', 'rupee', 'rs']
    found = [kw for kw in keywords if kw in chunk_lower]
    if found:
        print(f"  Keywords found: {found}")

# Search for payment amount patterns
print(f"\n=== Searching for Payment Amounts ===")
import re
for chunk in dlf_chunks:
    chunk_text = chunk['chunk']
    # Look for currency patterns (avoid Unicode rupee symbol)
    patterns = [
        r'Rs\.?\s*([\d,]+)',
        r'INR\s*([\d,]+)',
        r'([\d,]+)\s*(?:rupees?|lakh|crore)',
        r'([\d,]+)\s*(?:crores?|lakhs?)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, chunk_text, re.IGNORECASE)
        if matches:
            print(f"Found in {chunk['doc']}: {matches}")
    
    # Check specifically for Anmol Singh and Capbridge
    chunk_lower = chunk_text.lower()
    if 'anmol' in chunk_lower and ('capbridge' in chunk_lower or 'paid' in chunk_lower or 'payment' in chunk_lower):
        print(f"\n*** RELEVANT CHUNK FOUND in {chunk['doc']} ***")
        # Replace Unicode rupee symbol for display
        display_text = chunk_text.replace('\u20b9', 'Rs').replace('\u00a0', ' ')
        print(f"Content: {display_text[:800]}")
        
        # Try to extract amount
        import re
        amount_patterns = [
            r'Rs\.?\s*([\d,]+)',
            r'([\d,]+)\s*(?:crores?|lakhs?|rupees?)',
            r'INR\s*([\d,]+)',
        ]
        for pattern in amount_patterns:
            matches = re.findall(pattern, chunk_text, re.IGNORECASE)
            if matches:
                print(f"  Amount found: {matches}")

