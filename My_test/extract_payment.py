"""Extract payment amount from search results"""

import sys
import asyncio
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_server_2 import search_stored_documents, SearchDocumentsInput

async def extract_payment():
    """Search and extract payment amount"""
    
    query = "Anmol Singh Capbridge"
    result = search_stored_documents(SearchDocumentsInput(query=query))
    
    print(f"Search query: {query}")
    print(f"Found {len(result)} results\n")
    
    for i, chunk in enumerate(result[:5], 1):
        chunk_text = str(chunk)
        
        # Check if this chunk has both Anmol and Capbridge
        if 'anmol' in chunk_text.lower() and 'capbridge' in chunk_text.lower():
            print(f"\n{'='*70}")
            print(f"RELEVANT CHUNK {i}:")
            print('='*70)
            print(chunk_text[:1000])
            print('='*70)
            
            # Try to extract amount - look for Rs. patterns
            patterns = [
                r'Rs\.?\s*([\d,]+(?:\.[\d]+)?)\s*(?:crores?|lakhs?|rupees?)?',
                r'Rs\.?\s*([\d,]+)',
                r'([\d,]+)\s*(?:crores?|lakhs?)\s*(?:rupees?)?',
                r'INR\s*([\d,]+)',
            ]
            
            print("\nTrying to extract amounts:")
            for pattern in patterns:
                matches = re.findall(pattern, chunk_text, re.IGNORECASE)
                if matches:
                    print(f"  Pattern {pattern}: {matches}")

if __name__ == "__main__":
    asyncio.run(extract_payment())

