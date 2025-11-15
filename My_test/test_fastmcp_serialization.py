"""Test how FastMCP serializes list[str] returns"""
import json
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("Test")

class TestInput(BaseModel):
    query: str

@mcp.tool()
def test_list_return(input: TestInput) -> list[str]:
    """Test function that returns list[str]"""
    return ["chunk1", "chunk2", "chunk3"]

# Simulate what FastMCP does
print("=" * 80)
print("TESTING FastMCP LIST SERIALIZATION")
print("=" * 80)

# Call the function directly
result = test_list_return(TestInput(query="test"))
print(f"\nDirect call result type: {type(result)}")
print(f"Direct call result: {result}")

# FastMCP would serialize this - let's see what format
# FastMCP typically serializes to JSON in content[0].text
serialized = json.dumps(result)
print(f"\nJSON serialized: {serialized}")
print(f"JSON type: {type(serialized)}")

# Parse back
parsed = json.loads(serialized)
print(f"\nParsed back: {parsed}")
print(f"Parsed type: {type(parsed)}")
print(f"Is list: {isinstance(parsed, list)}")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("FastMCP serializes list[str] to JSON string in content[0].text")
print("Need to parse with json.loads() to get the list back")

