# Search Issue Fix Summary

## Problem Identified

The agent was returning "No information found" for all document queries, even though:
- ✅ Chunks exist in the FAISS index (verified)
- ✅ Direct test of `search_stored_documents` works (returns 10 results)
- ✅ Tesla PDF chunk with Tapscott/Williams is at rank 1

## Root Cause

**MCP Result Format Mismatch:**

1. `search_stored_documents` returns `list[str]` directly
2. FastMCP serializes this to JSON string in `content[0].text`
3. MCP `call_tool` returns a `CallToolResult` object, not the raw list
4. Agent's `SandboxMCP.call_tool` was returning the result object as-is
5. Agent code checks `if isinstance(result, list)` which fails because it's a `CallToolResult` object

## Fix Applied

### 1. Updated `modules/action.py` - SandboxMCP.call_tool

**Before:**
```python
async def call_tool(self, tool_name: str, input_dict: dict):
    result = await self.dispatcher.call_tool(tool_name, input_dict)
    return result  # Returns CallToolResult object
```

**After:**
```python
async def call_tool(self, tool_name: str, input_dict: dict):
    result = await self.dispatcher.call_tool(tool_name, input_dict)
    
    # Extract actual result from MCP response
    if hasattr(result, 'content') and result.content:
        if len(result.content) > 0 and hasattr(result.content[0], 'text'):
            text = result.content[0].text
            # Parse JSON if it's a list
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return parsed  # Return the actual list
            except (json.JSONDecodeError, AttributeError):
                pass
            return text if isinstance(text, str) else [text]
    
    return result  # Fallback
```

### 2. Updated `mcp_server_2.py` - Added docstring note

Added clarification in the docstring about how to extract results from MCP response.

### 3. Updated `prompts/New_Decision_Prompt.txt` - Updated example

Updated the document query example to reflect that SandboxMCP now handles parsing automatically.

## How It Works Now

1. Agent calls `mcp.call_tool('search_stored_documents', {...})`
2. `SandboxMCP.call_tool` intercepts the call
3. Calls real MCP dispatcher, gets `CallToolResult` object
4. Extracts `content[0].text` (JSON string)
5. Parses JSON to get the actual `list[str]`
6. Returns the list to agent code
7. Agent code checks `if isinstance(result, list)` - **NOW WORKS!**

## Testing

After restarting the agent, queries like:
- "What do you know about Don Tapscott and Anthony Williams?"
- "What is the relationship between Gensol and Go-Auto?"
- "How much did Anmol Singh pay for his DLF apartment via Capbridge?"

Should now return actual results from the index instead of "No information found".

## Verification

To verify the fix is working:
1. Restart `agent.py`
2. Run a query: "What do you know about Don Tapscott and Anthony Williams?"
3. Should see actual chunk content in the response
4. Check stderr logs for `[SEARCH] Returning X results` messages

