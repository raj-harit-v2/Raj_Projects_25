"""Test MCP call to search_stored_documents to see what's actually returned"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import MultiMCP
sys.path.insert(0, str(Path(__file__).parent))

from core.multimcp import MultiMCP

async def test_search():
    print("=" * 80)
    print("TESTING MCP CALL TO search_stored_documents")
    print("=" * 80)
    
    # Initialize MultiMCP
    print("\n1. Initializing MultiMCP...")
    multimcp = MultiMCP()
    await multimcp.initialize()
    
    # Get documents server
    print("2. Getting documents server...")
    documents_server = None
    for server_id, server_info in multimcp.servers.items():
        if server_id == "documents":
            documents_server = server_info
            break
    
    if not documents_server:
        print("[ERROR] Documents server not found!")
        return
    
    print(f"   Found server: {documents_server['id']}")
    
    # Call search_stored_documents
    print("\n3. Calling search_stored_documents...")
    query = "Don Tapscott and Anthony Williams"
    print(f"   Query: '{query}'")
    
    try:
        result = await multimcp.call_tool(
            server_id="documents",
            tool_name="search_stored_documents",
            input_data={"query": query}
        )
        
        print(f"\n4. Result type: {type(result)}")
        print(f"   Result: {result}")
        
        if isinstance(result, list):
            print(f"   Result length: {len(result)}")
            if len(result) > 0:
                print(f"   First result length: {len(result[0])}")
                print(f"   First result preview: {result[0][:200]}...")
            else:
                print("   [ERROR] Empty list returned!")
        else:
            print(f"   [WARNING] Result is not a list: {type(result)}")
            print(f"   Result content: {str(result)[:500]}")
            
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
    
    await multimcp.close()

if __name__ == "__main__":
    asyncio.run(test_search())

