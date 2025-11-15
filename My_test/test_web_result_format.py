"""Test how FastMCP returns string results"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_format():
    """Test the actual return format"""
    from core.session import MultiMCP
    import yaml
    
    # Load config
    with open("config/profiles.yaml", "r") as f:
        profile = yaml.safe_load(f)
        mcp_servers_list = profile.get("mcp_servers", [])
        mcp_servers = {server["id"]: server for server in mcp_servers_list}
    
    multi_mcp = MultiMCP(server_configs=list(mcp_servers.values()))
    await multi_mcp.initialize()
    
    try:
        # Test duckduckgo_search_results
        print("Testing duckduckgo_search_results...")
        result = await multi_mcp.call_tool('duckduckgo_search_results', {
            "input": {"query": "test", "max_results": 1}
        })
        
        print(f"\nResult type: {type(result)}")
        print(f"Result: {result}")
        
        # Check if it has content attribute
        if hasattr(result, 'content'):
            print(f"Has content: {result.content}")
            if result.content and len(result.content) > 0:
                print(f"content[0] type: {type(result.content[0])}")
                if hasattr(result.content[0], 'text'):
                    print(f"content[0].text: {result.content[0].text[:100]}...")
        
        # Try direct access
        try:
            text = result.content[0].text
            print(f"\n[OK] Access via result.content[0].text works")
            print(f"Text preview: {text[:200]}...")
        except Exception as e:
            print(f"\n[ERROR] Error accessing result.content[0].text: {e}")
            # Try other formats
            if isinstance(result, str):
                print(f"✅ Result is string directly: {result[:200]}...")
            elif hasattr(result, '__dict__'):
                print(f"Result attributes: {result.__dict__}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pass  # Don't close, just test

if __name__ == "__main__":
    asyncio.run(test_format())

