"""Test the search_stored_documents function directly"""

import sys
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_search():
    """Test search with different queries"""
    
    # Import the search function
    from mcp_server_2 import search_stored_documents, SearchDocumentsInput
    
    queries = [
        "Anmol Singh DLF apartment Capbridge payment",
        "Anmol Singh Capbridge",
        "Capbridge payment",
        "DLF apartment payment",
        "Anmol Singh",
    ]
    
    print("Testing search_stored_documents with different queries:\n")
    
    for query in queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print('='*70)
        
        try:
            result = search_stored_documents(SearchDocumentsInput(query=query))
            
            if result:
                print(f"Found {len(result)} results:")
                for i, chunk in enumerate(result[:3], 1):  # Show first 3
                    chunk_str = str(chunk)
                    # Check for keywords
                    has_anmol = 'anmol' in chunk_str.lower()
                    has_capbridge = 'capbridge' in chunk_str.lower()
                    has_payment = 'paid' in chunk_str.lower() or 'payment' in chunk_str.lower()
                    
                    print(f"\n  Result {i}:")
                    print(f"    Has 'Anmol': {has_anmol}")
                    print(f"    Has 'Capbridge': {has_capbridge}")
                    print(f"    Has 'payment': {has_payment}")
                    print(f"    Preview: {chunk_str[:200]}...")
            else:
                print("No results found")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())

