# Index Usage During Querying

## Answer: YES, Indexes Are Used During Querying

There are **TWO types of indexes** used in the system:

---

## 1. FAISS Index (Document Search) ✅

### When is it used?
**Every time `search_stored_documents` is called** - which happens for document queries.

### How it works:
```python
# In mcp_server_2.py, search_stored_documents():
1. Load FAISS index: index = faiss.read_index("faiss_index/index.bin")
2. Load metadata: metadata = json.loads("faiss_index/metadata.json")
3. Get query embedding: query_vec = get_embedding(query)
4. Search index: D, I = index.search(query_vec, k=10)
5. Return top 10 most relevant chunks
```

### Details:
- **Location**: `faiss_index/index.bin` (vector index) + `faiss_index/metadata.json` (chunk data)
- **Purpose**: Fast semantic similarity search
- **Method**: Vector embeddings (nomic-embed-text model)
- **Returns**: Top k=10 most relevant document chunks
- **Speed**: Very fast (milliseconds) compared to scanning all documents

### Example Flow:
```
User Query: "What is the relationship between Gensol and Go-Auto?"
  ↓
Agent calls: search_stored_documents({"query": "Gensol Go-Auto relationship"})
  ↓
FAISS Index Search:
  1. Convert query to embedding vector
  2. Search FAISS index for similar vectors
  3. Get top 10 chunk IDs
  4. Retrieve chunk text from metadata.json
  5. Return chunks to agent
```

---

## 2. Historical Context Index (Query Cache) ✅

### When is it used?
**Before processing every query** - to check for duplicates and retrieve context.

### How it works:
```python
# In agent.py:
1. Preprocess query → get query_hash
2. Check duplicate: historical_mgr.check_duplicate(query_hash)
   - Searches: historical_conversation_store.json["index"]["by_hash"]
3. If duplicate found (within 1 hour) → return cached answer
4. If not duplicate → get historical context for topic
   - Searches: historical_conversation_store.json["topics"][topic]
```

### Details:
- **Location**: `historical_conversation_store.json`
- **Structure**:
  ```json
  {
    "index": {
      "by_hash": { "query_hash": {...} },
      "by_date": [...],
      "recent_topics": [...]
    },
    "topics": {
      "mathematics": {"conversations": [...]},
      "documents": {"conversations": [...]},
      ...
    }
  }
  ```
- **Purpose**: 
  - Avoid re-processing same queries (cache)
  - Provide context from similar past queries
- **Speed**: Instant (in-memory JSON lookup)

### Example Flow:
```
User Query: "What do you know about Don Tapscott?"
  ↓
Generate query_hash: "70677266da6d2400"
  ↓
Check index["by_hash"]["70677266da6d2400"]
  ↓
If found (within 1 hour) → Return cached answer
If not found → Process query, then store in index
```

---

## Index Usage Summary

| Index Type | Used For | Location | When Used |
|------------|----------|----------|-----------|
| **FAISS Index** | Document search | `faiss_index/index.bin` | Every `search_stored_documents` call |
| **Historical Index** | Query cache/context | `historical_conversation_store.json` | Before every query |

---

## Performance Impact

### Without Indexes:
- Document search: Would need to scan all documents linearly (slow)
- Query cache: Would need to check all past queries (slow)

### With Indexes:
- Document search: **FAISS** - Fast vector similarity search (milliseconds)
- Query cache: **Hash lookup** - Instant O(1) lookup

---

## Fix Applied

**Issue**: After clearing cache, `historical_conversation_store.json` was `{}` (empty), causing `KeyError: 'index'`

**Fix**: Added validation in `_load_store()` to:
- Check if loaded structure has required keys
- Auto-initialize missing structure
- Handle corrupted/empty files gracefully

**Result**: Agent now handles empty/corrupted cache files without errors.

