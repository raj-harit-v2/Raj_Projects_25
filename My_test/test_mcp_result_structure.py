"""Test actual MCP result structure"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.multimcp import MultiMCP

async def test():
    print("=" * 80)
    print("TESTING ACTUAL MCP RESULT STRUCTURE")
    print("=" * 80)
    
    # Initialize MultiMCP
    multimcp = MultiMCP()
    await multimcp.initialize()
    
    # Call search_stored_documents
    query = "Don Tapscott"
    print(f"\nQuery: '{query}'")
    
    try:
        result = await multimcp.call_tool(
            server_id="documents",
            tool_name="search_stored_documents",
            input_data={"query": query}
        )
        
        print(f"\nResult type: {type(result)}")
        print(f"Result: {result}")
        print(f"Result dir: {[x for x in dir(result) if not x.startswith('_')]}")
        
        if hasattr(result, 'content'):
            print(f"\nHas 'content' attribute")
            print(f"Content type: {type(result.content)}")
            print(f"Content: {result.content}")
            
            if result.content and len(result.content) > 0:
                print(f"\nContent[0] type: {type(result.content[0])}")
                print(f"Content[0]: {result.content[0]}")
                print(f"Content[0] dir: {[x for x in dir(result.content[0]) if not x.startswith('_')]}")
                
                if hasattr(result.content[0], 'text'):
                    text = result.content[0].text
                    print(f"\nContent[0].text type: {type(text)}")
                    print(f"Content[0].text (first 200 chars): {text[:200]}")
                    
                    # Try parsing
                    import json
                    try:
                        parsed = json.loads(text)
                        print(f"\nParsed type: {type(parsed)}")
                        print(f"Parsed length: {len(parsed) if isinstance(parsed, list) else 'N/A'}")
                        if isinstance(parsed, list) and len(parsed) > 0:
                            print(f"First item type: {type(parsed[0])}")
                            print(f"First item (first 100 chars): {str(parsed[0])[:100]}")
                    except Exception as e:
                        print(f"\nJSON parse error: {e}")
        
    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
    
    await multimcp.close()

if __name__ == "__main__":
    asyncio.run(test())

