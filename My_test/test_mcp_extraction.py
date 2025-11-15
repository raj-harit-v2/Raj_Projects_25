"""Test MCP result extraction directly"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.session import MultiMCP
import yaml
from pathlib import Path

async def test():
    print("=" * 80)
    print("TESTING MCP RESULT EXTRACTION")
    print("=" * 80)
    
    # Load profile to get MCP config (same as agent.py)
    profile_path = Path(__file__).parent / "config" / "profiles.yaml"
    with open(profile_path) as f:
        profile_data = yaml.safe_load(f)
    server_configs = profile_data.get("mcp_servers", [])
    
    # Initialize MultiMCP
    multimcp = MultiMCP(server_configs)
    await multimcp.initialize()
    
    # Test query
    query = "Don Tapscott and Anthony Williams"
    print(f"\nQuery: '{query}'")
    print("\nCalling search_stored_documents via MultiMCP...")
    
    try:
        # Call the tool
        result = await multimcp.call_tool('search_stored_documents', {"input": {"query": query}})
        
        print(f"\n{'='*80}")
        print("RAW MCP RESULT:")
        print(f"{'='*80}")
        print(f"Type: {type(result)}")
        print(f"Result: {result}")
        print(f"\nResult attributes: {[x for x in dir(result) if not x.startswith('_')]}")
        
        # Test extraction logic (same as in SandboxMCP)
        if hasattr(result, 'content') and result.content:
            print(f"\n{'='*80}")
            print("EXTRACTION TEST:")
            print(f"{'='*80}")
            print(f"Result has 'content' with {len(result.content)} items")
            
            import json
            
            # Strategy 1: JSON parsing
            if len(result.content) > 0:
                content_item = result.content[0]
                print(f"\nContent[0] type: {type(content_item)}")
                print(f"Content[0]: {content_item}")
                
                text = None
                if hasattr(content_item, 'text'):
                    text = content_item.text
                elif isinstance(content_item, str):
                    text = content_item
                elif isinstance(content_item, dict) and 'text' in content_item:
                    text = content_item['text']
                
                if text is not None:
                    print(f"\nText extracted: type={type(text)}, length={len(str(text))}")
                    print(f"Text preview (first 200 chars): {str(text)[:200]}")
                    
                    # Try JSON parsing
                    try:
                        parsed = json.loads(str(text))
                        print(f"\n✅ JSON PARSED: type={type(parsed)}")
                        if isinstance(parsed, list):
                            print(f"✅ SUCCESS: List with {len(parsed)} items")
                            print(f"\nFirst item preview: {str(parsed[0])[:200] if parsed else 'N/A'}")
                            return parsed
                        else:
                            print(f"❌ Parsed but not a list: {type(parsed)}")
                    except json.JSONDecodeError as e:
                        print(f"\n❌ JSON decode error: {e}")
            
            # Strategy 2: Multiple content items
            if len(result.content) > 1:
                print(f"\nMultiple content items ({len(result.content)}) - extracting...")
                extracted_list = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        extracted_list.append(item.text)
                    elif isinstance(item, str):
                        extracted_list.append(item)
                    elif isinstance(item, dict) and 'text' in item:
                        extracted_list.append(item['text'])
                
                if extracted_list:
                    print(f"✅ SUCCESS: Extracted {len(extracted_list)} items")
                    return extracted_list
        
        print(f"\n❌ Could not extract list from result")
        return None
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await multimcp.shutdown()

if __name__ == "__main__":
    result = asyncio.run(test())
    if result:
        print(f"\n{'='*80}")
        print("✅ EXTRACTION SUCCESSFUL!")
        print(f"{'='*80}")
        print(f"Returned list with {len(result)} items")
    else:
        print(f"\n{'='*80}")
        print("❌ EXTRACTION FAILED")
        print(f"{'='*80}")

