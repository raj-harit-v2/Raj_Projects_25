# Staged Query Enhancement for Prompt

## Problem

Complex queries like:
- "What do you know about Don Tapscott and Anthony Williams?"
- "What is the relationship between Gensol and Go-Auto?"
- "How much Anmol singh paid for his DLF apartment via Capbridge?"

May benefit from staged/multi-step processing to build up partial results.

## Current Capability

The agent already supports staged queries via `FURTHER_PROCESSING_REQUIRED`:
- Step 1: Initial search/query
- Step 2: Process intermediate results
- Step 3: Synthesize final answer

The loop automatically forwards `FURTHER_PROCESSING_REQUIRED` results to the next step.

## Enhancement Applied

Updated `prompts/New_Decision_Prompt.txt` with:

### 1. Staged Query Section
Added guidance on breaking complex queries into stages:
- Stage 1: Search for initial information
- Stage 2: Refine search based on Stage 1 results
- Stage 3: Combine and synthesize final answer

### 2. Three New Examples

**Example 1: Multiple Entities**
```python
# Search for each entity separately
# Combine results
# Pass to next stage for synthesis
```

**Example 2: Relationship Search**
```python
# Try document search first
# Fallback to web search if needed
# Extract relationship information
```

**Example 3: Payment Extraction**
```python
# Search for relevant chunks
# Filter for payment-related content
# Pass to next stage for amount extraction
```

## How It Works

1. **First solve() call:**
   - Searches documents/web
   - Finds relevant chunks
   - Returns `FURTHER_PROCESSING_REQUIRED: [intermediate results]`

2. **Agent loop:**
   - Detects `FURTHER_PROCESSING_REQUIRED`
   - Creates new context with intermediate results
   - Calls `generate_plan()` again with new context

3. **Second solve() call:**
   - Receives intermediate results in context
   - Processes/synthesizes the information
   - Returns `FINAL_ANSWER: [complete answer]`

## Benefits

✅ **Better for complex queries** - Break down into manageable steps
✅ **More context** - Each stage builds on previous results
✅ **Better extraction** - Can refine searches based on initial findings
✅ **Handles partial results** - Can work with incomplete information

## Testing

Test with these queries:
1. "What do you know about Don Tapscott and Anthony Williams?"
2. "What is the relationship between Gensol and Go-Auto?"
3. "How much Anmol singh paid for his DLF apartment via Capbridge?"

Expected behavior:
- Query 1: Search for each person separately, combine results
- Query 2: Try document search, fallback to web, extract relationship
- Query 3: Search for payment info, extract amount, calculate log

---

**Date:** November 14, 2025  
**Status:** ✅ Enhanced prompt with staged query examples

