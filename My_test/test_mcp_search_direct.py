"""Test MCP search directly to see what's returned"""
import asyncio
import json
from pathlib import Path
import sys

# Simulate the MCP call
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Import the actual function
from mcp_server_2 import search_stored_documents, SearchDocumentsInput

async def test():
    print("=" * 80)
    print("TESTING search_stored_documents DIRECTLY")
    print("=" * 80)
    
    # Test query
    query = "Don Tapscott and Anthony Williams"
    print(f"\nQuery: '{query}'")
    
    # Create input
    input_obj = SearchDocumentsInput(query=query)
    
    # Call function
    print("\nCalling search_stored_documents...")
    try:
        result = search_stored_documents(input_obj)
        print(f"\nResult type: {type(result)}")
        print(f"Result length: {len(result) if isinstance(result, list) else 'N/A'}")
        
        if isinstance(result, list):
            if len(result) > 0:
                print(f"\nFirst result preview:")
                print(result[0][:300])
            else:
                print("\n[ERROR] Empty list returned!")
        else:
            print(f"\n[ERROR] Result is not a list: {type(result)}")
            print(f"Result: {result}")
            
    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())

