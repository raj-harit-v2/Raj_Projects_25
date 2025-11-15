# Final Fixes Applied - Document Query Issue

## 🔧 **Issue Identified & Resolved**

**Problem:** Document query "How much did Anmol Singh pay for his DLF apartment via Capbridge?" failed with JSON parsing error.

**Root Causes:**
1. ❌ Perception selected "math" server instead of "documents" server
2. ❌ LLM generated code using wrong tool (convert_webpage_url_into_markdown instead of search_stored_documents)
3. ❌ Code tried to parse document result as JSON (incorrect format)

---

## ✅ **Fixes Applied**

### Fix 1: Enhanced Perception Prompt
**File:** `prompts/perception_prompt.txt`

**Changes:**
- ✅ Removed all Unicode emojis for Windows compatibility
- ✅ Added clear selection rules:
  - Document searches → "documents" server
  - Calculations → "math" server
  - Web searches → "websearch" server
- ✅ Added 4 concrete examples showing correct server selection
- ✅ Emphasized: "If query mentions searching PDFs or documents: select 'documents'"

**Example Added:**
```
Query: "How much did someone pay for apartment?"
→ selected_servers: ["documents"]
```

### Fix 2: Improved Document Example in Decision Prompt
**File:** `prompts/New_Decision_Prompt.txt`

**Changes:**
- ✅ Better example showing correct `search_stored_documents` usage
- ✅ Clarified that result is a **list** (not JSON to parse)
- ✅ Shows how to iterate through chunks
- ✅ Demonstrates FURTHER_PROCESSING_REQUIRED for document content
- ✅ Fixed template brace escaping

**New Example:**
```python
async def solve():
    # Search documents
    result = await mcp.call_tool('search_stored_documents', {{
        "input": {{"query": "Anmol Singh DLF Capbridge payment"}}
    }})
    
    # result is a list of text chunks - no json.loads needed!
    chunks = result if isinstance(result, list) else []
    
    for chunk in chunks:
        chunk_text = str(chunk)
        if "Capbridge" in chunk_text and "paid" in chunk_text:
            return f"FURTHER_PROCESSING_REQUIRED: Found: {{chunk_text[:500]}}"
    
    return "FINAL_ANSWER: No information found"
```

---

## 🎯 **Why This Matters**

### **Correct Flow for Document Queries:**

```
User: "How much did Anmol Singh pay..."
  ↓
Heuristics: Query Type = "document", Topic = "finance"
  ↓
Perception: selected_servers = ["documents"]
  ↓
Planning: Use search_stored_documents tool
  ↓
Execution: Search FAISS index for "Anmol Singh DLF Capbridge"
  ↓
Result: Return matching chunks from DLF_BRSR.pdf
  ↓
Processing: Extract amount from text
  ↓
Final Answer: "Anmol Singh paid ₹XXX via Capbridge"
```

---

## 🧪 **Testing Instructions**

### **Test 1: Simple Document Search**
```
Search documents for DLF
```

**Expected:**
- Perception: selected_servers = ["documents"]
- Tool: search_stored_documents
- Result: Chunks from DLF documents

### **Test 2: Payment Query (Original Issue)**
```
How much did Anmol Singh pay for his DLF apartment via Capbridge?
```

**Expected:**
- Preprocessing: Query Type = "document" or "hybrid", Topic = "finance"
- Perception: selected_servers = ["documents"]
- Tool: search_stored_documents with query "Anmol Singh DLF Capbridge payment"
- Result: FURTHER_PROCESSING_REQUIRED with document chunks
- Step 2: Extract amount from chunks
- Final: Payment amount

### **Test 3: Verify Cache Works**
Run the same query twice:

**First run:** Full processing  
**Second run:** `[CACHE HIT]` instant result

---

## 📊 **Expected Behavior After Fixes**

### For "How much did Anmol Singh pay...":

**Step 1: Heuristics**
```
[heuristics] Preprocessing query...
[heuristics] Query Type: document  (or hybrid)
[heuristics] Topic: finance
[heuristics] Query Hash: abc123...
```

**Step 2: Perception**
```
[perception] selected_servers=['documents']
```
✅ Should select "documents" now (not "math")

**Step 3: Planning**
```
[plan] Generated solve() using search_stored_documents
```
✅ Should use search_stored_documents (not convert_webpage)

**Step 4: Execution**
```
[action] Searching FAISS index...
Result: List of document chunks mentioning Anmol Singh, DLF, Capbridge
```

**Step 5: Processing**
```
FURTHER_PROCESSING_REQUIRED: Found information in chunk...
```
Then in next step, extract the amount

**Step 6: Final**
```
[FINAL ANSWER] Anmol Singh paid ₹XXX million via Capbridge
[heuristics] Confidence: 0.XX
```

---

## 🔍 **Diagnostic: Check Perception**

If perception still selects wrong server, check:

```python
# Test perception directly
python -c "
from modules.perception import extract_perception

result = await extract_perception(
    'How much did Anmol Singh pay?',
    {{'math': {'description': 'Math tools'}, 
      'documents': {'description': 'Document search tools'}}}
)
print(result.selected_servers)
"
```

Should output: `['documents']`

---

## 💡 **Key Insights**

### **Document Tools Don't Return JSON**
The `search_stored_documents` tool returns a **list of strings** (text chunks), not JSON.

**Correct handling:**
```python
result = await mcp.call_tool('search_stored_documents', {{"input": {{"query": "..."}}}})
chunks = result  # Already a list!
for chunk in chunks:
    chunk_text = str(chunk)
    # Search in chunk_text
```

**Incorrect (causes error):**
```python
# DON'T DO THIS:
result = await mcp.call_tool('search_stored_documents', ...)
data = json.loads(result.content[0].text)  # ERROR! Not JSON format
```

### **Web Tools Return MarkdownOutput**
The `convert_webpage_url_into_markdown` tool returns a MarkdownOutput object with a `.markdown` field.

**Correct handling:**
```python
result = await mcp.call_tool('convert_webpage_url_into_markdown', {{"input": {{"url": "..."}}}})
markdown = json.loads(result.content[0].text)["markdown"]
```

---

## 🚀 **Ready to Test Again**

```bash
python agent.py
```

**Test Query:**
```
How much did Anmol Singh pay for his DLF apartment via Capbridge?
```

**What to Watch For:**
1. ✅ Perception should select ["documents"]
2. ✅ Plan should use search_stored_documents
3. ✅ Should search FAISS index
4. ✅ Should return document chunks
5. ✅ May need FURTHER_PROCESSING to extract exact amount

---

## 📝 **If Still Not Working**

### Option 1: Check FAISS Index Content
```python
python -c "
import json
meta = json.load(open('faiss_index/metadata.json'))
dlf_chunks = [m for m in meta if 'DLF' in m['doc']]
print(f'DLF chunks: {{len(dlf_chunks)}}')
for c in dlf_chunks[:2]:
    print(c['chunk'][:200])
"
```

This shows if DLF payment info is actually in the index.

### Option 2: Direct Tool Test
Test the search tool directly to see what it returns:

```python
# Create test_search.py
import asyncio
from core.session import MultiMCP

async def test():
    multi_mcp = MultiMCP(server_configs=[{{
        "id": "documents",
        "script": "mcp_server_2.py",
        "cwd": "."
    }}])
    await multi_mcp.initialize()
    
    result = await multi_mcp.call_tool('search_stored_documents', {{
        "input": {{"query": "Anmol Singh DLF Capbridge payment"}}
    }})
    
    print(f"Type: {{type(result)}}")
    print(f"Content: {{result}}")

asyncio.run(test())
```

---

## ✅ **Fixes Summary**

| Issue | File | Fix | Status |
|-------|------|-----|--------|
| Unicode emojis | perception_prompt.txt | Removed | ✅ |
| Wrong server selection | perception_prompt.txt | Better examples | ✅ |
| Wrong tool usage | New_Decision_Prompt.txt | Better document example | ✅ |
| JSON parsing error | New_Decision_Prompt.txt | Clarified result format | ✅ |
| Template escaping | New_Decision_Prompt.txt | Double braces | ✅ |

---

## 🎯 **Expected Outcome**

After these fixes, the document query should:
1. ✅ Route to "documents" server
2. ✅ Use search_stored_documents tool
3. ✅ Return list of relevant chunks
4. ✅ Process chunks to extract payment information
5. ✅ Return final answer with confidence score

---

**Status:** ✅ Fixes Applied  
**Test:** Ready for retry  
**Expected:** Should work correctly now

**Try the query again!** 🚀

