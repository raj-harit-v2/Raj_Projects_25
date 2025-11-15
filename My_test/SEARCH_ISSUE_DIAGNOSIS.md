# Search Issue Diagnosis: Chunks Exist But Agent Can't Find Them

## Problem
Agent returns "No information found" for queries like "Don Tapscott and Anthony Williams", but:
- ✅ Chunks exist in the index (verified)
- ✅ Direct search test works (returns 10 results)
- ✅ Tesla PDF chunk with both entities is at rank 1

## Evidence from Terminal Output

```
[plan] async def solve():
    result = await mcp.call_tool('search_stored_documents', {"input": {"query": "Don Tapscott and Anthony Williams"}})
    chunks = result if isinstance(result, list) else []
    
    if chunks:
        combined_info = "\n\n".join([str(c) for c in chunks])       
        return f"FINAL_ANSWER: {combined_info}"
    
    # Falls through to fallback...
    return f"FINAL_ANSWER: Don Tapscott info:\nNo information found\n\nAnthony Williams info:\nNo information found"
```

## Direct Test Results

When testing `search_stored_documents` directly:
- ✅ Returns 10 results
- ✅ Rank 1: Tesla PDF chunk (distance 382.53)
- ✅ Contains both "Tapscott" and "Williams"
- ✅ Chunk length: 3002 characters

## Possible Causes

1. **MCP Server Error Being Silently Caught**
   - Exception in `get_embedding()` or `index.search()`
   - Error message not being returned correctly

2. **Result Format Mismatch**
   - MCP server returning result in unexpected format
   - Agent expecting `list[str]` but getting something else

3. **Metadata Structure Issue**
   - Missing 'chunk' key in metadata entries
   - KeyError being caught and skipped

4. **Ollama Embedding API Issue**
   - API call failing when called through MCP
   - Timeout or connection error

## Fixes Applied

1. ✅ Added safety check for missing 'chunk' key
2. ✅ Added detailed logging to search function:
   - `[SEARCH]` - Query and result count
   - `[WARNING]` - When no results found
   - `[ERROR]` - With full traceback
3. ✅ Enhanced error handling with traceback logging

## Next Steps

1. **Restart agent and MCP servers**
2. **Check MCP server stderr logs** for:
   - `[SEARCH] Query: ...`
   - `[SEARCH] Returning X results`
   - `[WARNING]` or `[ERROR]` messages
3. **Test with a simple query** to isolate the issue
4. **Verify Ollama embedding API** is accessible from MCP server context

## How to Debug

1. Run agent with query: "Don Tapscott and Anthony Williams"
2. Check stderr output from `mcp_server_2.py` (MCP servers log to stderr)
3. Look for:
   - `[SEARCH] Query: Don Tapscott and Anthony Williams`
   - `[SEARCH] Returning 10 results` (or 0 if issue)
   - Any `[ERROR]` or `[WARNING]` messages

## Expected Behavior

When working correctly:
```
[SEARCH] Query: Don Tapscott and Anthony Williams
[SEARCH] Returning 10 results
```

If there's an issue:
```
[SEARCH] Query: Don Tapscott and Anthony Williams
[ERROR] Search failed: <error message>
[ERROR] Traceback: ...
```

Or:
```
[SEARCH] Query: Don Tapscott and Anthony Williams
[SEARCH] Returning 0 results
[WARNING] No results found - this might indicate an issue
```

