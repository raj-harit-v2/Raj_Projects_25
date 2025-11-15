# Fix: Documents-Only Search Strategy

## Problem

The agent was falling back to web search even for document queries. When searching for information in local documents, it should:
1. **ONLY** search stored documents
2. **NEVER** fall back to web search
3. Return "Information not found in stored documents" if not found

## Root Cause

The prompt template (`prompts/New_Decision_Prompt.txt`) had instructions that allowed web search as a fallback:
- "Only if documents don't have the answer, try web search"
- Examples showed web search fallback for document queries

## Solution

Updated `prompts/New_Decision_Prompt.txt` with strict documents-only policy:

### Changes Made:

1. **Search Strategy Section** (Lines 23-29):
   - Added: "FOR DOCUMENT QUERIES: ONLY use `search_stored_documents` - NEVER use web search"
   - Added: "If documents don't have the answer, return 'FINAL_ANSWER: Information not found in stored documents' - DO NOT search the web"

2. **Staged Queries Section** (Lines 31-39):
   - Changed: "Stage 2: If not found, try web search" → "Stage 2: Search for additional related information in documents"
   - Added: "IMPORTANT: For document queries, ONLY search documents. If information is not found, return 'FINAL_ANSWER: Information not found in stored documents' - DO NOT fall back to web search."

3. **Document Query Example** (Lines 88-108):
   - Removed web search fallback code
   - Changed title to: "Document Query (ONLY search documents - NEVER use web search)"
   - Returns "No information found in stored documents" instead of searching web

4. **Relationship Search Example** (Lines 156-178):
   - Removed web search fallback
   - Now searches each entity separately in documents if combined search fails
   - Returns "No relationship information found in stored documents" if not found

## New Behavior

### Document Queries:
- ✅ **ONLY** searches `search_stored_documents`
- ✅ Returns "Information not found in stored documents" if not found
- ❌ **NEVER** uses `duckduckgo_search_results`

### Web Queries:
- ✅ Only uses `duckduckgo_search_results` for explicit web/current events queries
- ✅ Examples remain for web search when appropriate

### Staged Queries:
- ✅ Stage 1: Search first entity in documents
- ✅ Stage 2: Search second entity in documents (if needed)
- ✅ Stage 3: Combine document results
- ❌ **NO** web search fallback

## Testing

After this fix, test with:
1. "What do you know about Don Tapscott and Anthony Williams?"
   - Should: Search documents only
   - Should NOT: Fall back to web search

2. "What is the relationship between Gensol and Go-Auto?"
   - Should: Search documents only (searches each entity separately if needed)
   - Should NOT: Fall back to web search

3. "How much did Anmol Singh pay for his DLF apartment via Capbridge?"
   - Should: Search documents only
   - Should NOT: Fall back to web search

## Files Modified

- `prompts/New_Decision_Prompt.txt` - Updated search strategy and examples

## Next Steps

1. Restart agent to load new prompt
2. Test document queries - should only search documents
3. Verify web search is only used for explicit web queries

