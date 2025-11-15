# Fix: JSON Parsing Errors in Agent Queries

## Problem Identified

The agent was generating code that tried to parse ALL tool results as JSON, causing errors:

```
Expecting value: line 1 column 1 (char 0)
```

## Root Cause

The prompt (`prompts/New_Decision_Prompt.txt`) incorrectly instructed the LLM to:
- Always use `json.loads(result.content[0].text)` for ALL tools
- This works for math tools (which return JSON)
- But FAILS for:
  - `search_stored_documents` - returns `list[str]` directly
  - `duckduckgo_search_results` - returns formatted text string, not JSON

## Fix Applied

Updated `prompts/New_Decision_Prompt.txt` to clarify different return formats:

### 1. Added Tool-Specific Response Extraction Section

```python
# FOR MATH TOOLS (add, subtract, multiply, etc.):
response_data = json.loads(result.content[0].text)
final_value = response_data["result"]

# FOR search_stored_documents (returns list[str] directly):
chunks = result  # result IS the list, no parsing needed
for chunk in chunks:
    chunk_text = str(chunk)
    # Process chunk_text directly

# FOR duckduckgo_search_results (returns formatted text string):
search_text = result.content[0].text  # This is a STRING, NOT JSON
# Use search_text directly - it's already formatted text
```

### 2. Added Web Search Example

Added a complete example showing how to handle `duckduckgo_search_results`:

```python
async def solve():
    result = await mcp.call_tool('duckduckgo_search_results', {"input": {"query": "Don Tapscott", "max_results": 3}})
    
    # duckduckgo_search_results returns formatted TEXT string - NOT JSON!
    search_results_text = result.content[0].text
    
    # Use the text directly
    return f"FINAL_ANSWER: {search_results_text}"
```

## Index Status

**Current Index:**
- Size: 318 KB (index.bin) + 412.5 KB (metadata.json)
- Total chunks: 106
- Documents indexed: 9

**Note:** The index size (318 KB) is reasonable for 106 chunks. If you need it larger:
- Add more documents to `documents/` folder
- Run `python mcp_server_2.py index` to rebuild

**Note:** `.docx` files require `pip install markitdown[docx]` to be indexed.

## Testing

After this fix, the agent should:
1. ✅ Correctly handle `search_stored_documents` (no JSON parsing)
2. ✅ Correctly handle `duckduckgo_search_results` (use text directly)
3. ✅ Still correctly handle math tools (JSON parsing)

## Files Modified

- `prompts/New_Decision_Prompt.txt` - Updated with tool-specific extraction examples

## Next Steps

1. Test with a web search query: "What do you know about Don Tapscott?"
2. Test with a document query: "How much did Anmol Singh pay for DLF apartment?"
3. Verify no more JSON parsing errors occur

---

**Date:** November 14, 2025  
**Status:** ✅ Fixed

