# Staged Queries & Index Rebuild Guide

## 1. Staged Query Support

**YES, staged queries are fully supported!** The agent can handle multiple related questions using the `FURTHER_PROCESSING_REQUIRED` mechanism.

### How It Works:

1. **Stage 1**: Agent searches for first entity/question
2. **Stage 2**: Agent searches for second entity/question  
3. **Stage 3**: Agent combines results and synthesizes final answer

### Example from Prompt:

```python
# Staged Query Example (Multiple Entities):
async def solve():
    # Stage 1: Search for first entity
    result1 = await mcp.call_tool('search_stored_documents', {"input": {"query": "Don Tapscott"}})
    chunks1 = result1 if isinstance(result1, list) else []
    
    # Stage 2: Search for second entity
    result2 = await mcp.call_tool('search_stored_documents', {"input": {"query": "Anthony Williams"}})
    chunks2 = result2 if isinstance(result2, list) else []
    
    # Combine results for further processing
    combined = f"Don Tapscott info: {' '.join(str(c)[:200] for c in chunks1[:2])} | Anthony Williams info: {' '.join(str(c)[:200] for c in chunks2[:2])}"
    
    # Pass to next stage for synthesis
    return f"FURTHER_PROCESSING_REQUIRED: {combined}"
```

### Agent Loop Behavior:

- When `FURTHER_PROCESSING_REQUIRED:` is returned, the agent:
  1. Forwards the intermediate result to the next step
  2. Continues to the next step (within max_steps limit)
  3. Allows the LLM to synthesize the combined results
  4. Returns `FINAL_ANSWER:` when complete

### Current Configuration:

- **max_steps**: 5 (in `config/profiles.yaml`)
- **max_lifelines_per_step**: 3
- This allows up to 5 stages of processing

## 2. Index Rebuild Status

### Current Status:
- ❌ **Canvas LMS PDF is NOT in index** (0 chunks found)
- ✅ Other documents are indexed (140 total chunks)
- ⚠️ **Index rebuild is REQUIRED** to include Canvas LMS PDF

### Why Rebuild is Needed:

1. Canvas LMS PDF was processed but not added to index
2. Images were extracted (20 images found)
3. Image captions need to be generated with llava model
4. Index needs to include these captions for searchability

### How to Rebuild:

```bash
# Remove cache to force reprocessing
Remove-Item faiss_index\doc_index_cache.json -ErrorAction SilentlyContinue

# Rebuild index
python mcp_server_2.py index
```

## 3. Server Restart Requirements

### Do You Need to Restart?

**YES, restart is recommended** because:

1. ✅ **mcp_server_2.py was modified**:
   - Changed `GEMMA_MODEL` from `"gemma2:2b"` to `"llava"`
   - Fixed API response field handling (`response` vs `result`)
   - These changes require server restart to take effect

2. ✅ **Ollama should be running**:
   - llava model needs to be available
   - Check: `curl http://localhost:11434/api/tags`

3. ⚠️ **MCP servers need restart**:
   - mcp_server_2.py (documents server) - **RESTART REQUIRED**
   - mcp_server_1.py (math server) - No restart needed
   - mcp_server_3.py (websearch server) - No restart needed

### Restart Steps:

1. **Stop MCP servers** (if running):
   - Kill any running `mcp_server_2.py` processes

2. **Verify Ollama is running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **Rebuild index**:
   ```bash
   python mcp_server_2.py index
   ```

4. **Start agent** (MCP servers auto-start):
   ```bash
   python agent.py
   ```

## 4. Testing Staged Queries

### Example Queries to Test:

1. **Multiple Entities**:
   ```
   What do you know about Don Tapscott and Anthony Williams?
   ```

2. **Relationship Search**:
   ```
   What is the relationship between Gensol and Go-Auto?
   ```

3. **Payment Extraction**:
   ```
   How much did Anmol Singh pay for his DLF apartment via Capbridge?
   ```

### Expected Behavior:

- Agent searches documents first
- If multiple entities, searches each separately
- Combines results using `FURTHER_PROCESSING_REQUIRED:`
- Synthesizes final answer in subsequent step
- Returns `FINAL_ANSWER:` when complete

## 5. Summary

| Item | Status | Action Needed |
|------|--------|---------------|
| Staged Queries | ✅ Supported | None - already working |
| Canvas LMS in Index | ❌ Missing | **Rebuild index** |
| MCP Server 2 | ⚠️ Modified | **Restart required** |
| Ollama | ✅ Running | Verify llava model |
| Agent Code | ✅ Fixed | No restart needed |

### Recommended Actions:

1. ✅ **Rebuild index**: `python mcp_server_2.py index`
2. ✅ **Restart MCP server 2** (restart agent, it auto-starts servers)
3. ✅ **Test staged queries** with the 3 example questions
4. ✅ **Verify Canvas LMS** query works: `"which course are we teaching on Canvas LMS?"`

