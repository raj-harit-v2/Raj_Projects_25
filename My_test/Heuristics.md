# Heuristics Implementation for Cortex-R Agent

## Overview
This document describes the 10 heuristic rules implemented to improve query processing, result validation, and system reliability. It also explains how these heuristics integrate with the core project architecture and cognitive loop.

---

## Core Project Architecture

### Cognitive Loop (OODA Pattern)
The Cortex-R agent follows an **Observe-Orient-Decide-Act** (OODA) cognitive loop:

```
User Query
    ↓
[HEURISTICS PREPROCESSING] ← H-01 to H-05, H-10
    ↓
Cache Check (H-10 hash lookup)
    ├─ Hit → Return Cached Answer (instant)
    └─ Miss → Continue
         ↓
Historical Context Retrieval (by topic from H-04)
         ↓
[PERCEPTION] Observe - Intent extraction, server selection
         ↓
[DECISION] Orient/Decide - Plan generation with historical context
         ↓
[ACTION] Act - Sandbox execution, tool calls
         ↓
[HEURISTICS POSTPROCESSING] ← H-06 to H-09
         ↓
Historical Storage (Learning)
         ↓
Result to User
```

### System Components

1. **agent.py** - Main entry point, orchestrates the entire flow
2. **core/loop.py** - AgentLoop implements the OODA cycle
3. **core/context.py** - AgentContext holds state, AgentProfile holds config
4. **core/session.py** - MultiMCP dispatches tools to MCP servers
5. **modules/perception.py** - Extracts intent and selects servers
6. **modules/decision.py** - Generates solve() plan using LLM
7. **modules/action.py** - Executes plan in sandbox, calls tools
8. **modules/heuristics.py** - 10 heuristic functions (this module)
9. **modules/historical_context.py** - Smart indexing and retrieval
10. **modules/memory.py** - Session memory management
11. **modules/model_manager.py** - Unified LLM interface (Gemini/Ollama)

---

## Query Pre-processing Heuristics (H-01 to H-05)

### H-01: Query Canonicalization
**Function:** `canonicalize_query(query: str) -> str`

**Purpose:** Normalize query format for consistent processing

**Actions:**
- Remove excessive whitespace
- Standardize common abbreviations (pls→please, u→you, w/→with)
- Convert to consistent case handling

**Example:**
```python
Input:  "pls   calculate   sum  of   10 and 20"
Output: "please calculate sum of 10 and 20"
```

**Integration:** Applied first in `preprocess_query()` pipeline, used by H-10 for hashing

---

### H-02: Entity Extraction
**Function:** `extract_entities(query: str) -> Dict[str, List[str]]`

**Purpose:** Identify key entities for better tool selection

**Extracts:**
- **Numbers:** All numeric values (integers and floats)
- **Names:** Capitalized words (potential person/company names)
- **Dates:** Various date formats
- **URLs:** Web addresses

**Example:**
```python
Input: "How much did Anmol Singh pay on 01/15/2023?"
Output: {
    "numbers": [],
    "names": ["Anmol Singh"],
    "dates": ["01/15/2023"],
    "urls": []
}
```

**Integration:** 
- Entities stored in `processed_query['entities']`
- Passed to historical context metadata
- Used by perception module for better intent understanding

---

### H-03: Query Type Classification
**Function:** `classify_query_type(query: str) -> str`

**Purpose:** Categorize query to guide tool selection

**Categories:**
- **math:** Calculations, computations
- **document:** PDF/file searches
- **web:** Online research, URLs
- **code:** Python/shell/SQL execution
- **hybrid:** Multiple categories
- **general:** Uncategorized

**Method:** Keyword scoring across categories

**Example:**
```python
Input: "Calculate ASCII values and search documents for DLF"
Output: "hybrid"
```

**Integration:**
- Used by `suggest_tools()` (H-05) to filter relevant tools
- Stored in `processed_query['query_type']`
- Passed to historical context metadata
- Helps perception module select appropriate MCP servers

---

### H-04: Topic Triage
**Function:** `identify_topic(query: str) -> str`

**Purpose:** Map query to domain topic for historical context lookup

**Topics:**
- mathematics
- documents
- finance
- technology
- web_research
- education
- general

**Usage:** Enables smart historical context retrieval from topic-specific past conversations

**Example:**
```python
Input: "Which course are we teaching on Canvas LMS?"
Output: "education"
```

**Integration:**
- **Critical for Historical Context System:**
  - Used by `HistoricalContextManager.format_context_for_prompt(topic, limit=3)`
  - Retrieves past successful queries from same topic
  - Injected into LLM prompt for better planning
  - Stored in `processed_query['topic']` and conversation metadata

**Core Logic Flow:**
```python
# In agent.py:
topic = processed_query['topic']  # From H-04
historical_context = historical_mgr.format_context_for_prompt(topic, limit=3)
context.historical_context = historical_context  # Passed to decision module
```

---

### H-05: Tool Suggestion
**Function:** `suggest_tools(query: str, query_type: str) -> List[str]`

**Purpose:** Recommend likely tools based on query analysis

**Strategy:**
- Analyzes keywords in canonical query
- Maps to specific tool names
- Returns top 3 most relevant tools

**Example:**
```python
Input: "Find ASCII values of INDIA and sum exponentials"
Type: "math"
Output: ["strings_to_chars_to_int", "int_list_to_exponential_sum"]
```

**Integration:**
- Stored in `processed_query['suggested_tools']`
- Can be used by perception module as hints
- Helps LLM in decision module select appropriate tools

---

## Result Post-processing Heuristics (H-06 to H-09)

### H-06: JSON Validation
**Function:** `validate_json_response(result: Any) -> bool`

**Purpose:** Ensure tool responses are properly formatted

**Validates:**
- String results can be parsed as JSON
- Dict results are valid
- MCP result format has proper content structure

**Example:**
```python
Input: '{"result": 42}'
Output: True

Input: 'Invalid JSON{}'
Output: False
```

**Integration:**
- Used in `postprocess_result()` to check result validity
- Stored in `post_result['is_valid']`
- Can trigger error handling if invalid

---

### H-07: Confidence Scoring
**Function:** `extract_answer_confidence(result: str) -> Dict[str, Any]`

**Purpose:** Estimate reliability of the answer

**Indicators:**
- **High confidence:** "found", "calculated", "result is", "equals", precise numbers
- **Low confidence:** "not found", "no information", "unclear", "possibly"

**Scoring:** 0.0 (no confidence) to 1.0 (high confidence)

**Example:**
```python
Input: "Calculated result is 42.5678"
Output: {
    "score": 0.8,
    "indicators": ["definitive_answer", "precise_numeric"]
}
```

**Integration:**
- Stored in `post_result['confidence']`
- Logged in agent.py: `log("heuristics", f"Confidence: {post_result['confidence']['score']:.2f}")`
- Stored in historical context metadata for future reference
- Can be used for quality monitoring and improvement

---

### H-08: Incomplete Answer Detection
**Function:** `detect_incomplete_answer(result: str) -> bool`

**Purpose:** Identify when result needs further processing

**Detection Keywords:**
- "partial"
- "incomplete"
- "need more"
- "requires additional"
- "step 1 of"
- "first, we need"

**Usage:** Triggers FURTHER_PROCESSING_REQUIRED flow

**Example:**
```python
Input: "Step 1 of 3: Found document, need to extract amount"
Output: True
```

**Integration:**
- Stored in `post_result['is_incomplete']`
- Logged in agent.py
- Can trigger multi-step processing continuation

---

### H-09: Output Sanitization
**Function:** `sanitize_output(result: str) -> str`

**Purpose:** Clean result for safe and readable display

**Actions:**
- Remove script tags (XSS prevention)
- Normalize whitespace (max 2 consecutive newlines)
- Truncate if > 2000 characters
- Strip leading/trailing whitespace

**Example:**
```python
Input: "Result   is\n\n\n\n42    with    spaces"
Output: "Result is\n\n42 with spaces"
```

**Integration:**
- Applied to final answer before display
- Stored in `post_result['sanitized_output']`
- Used in agent.py: `print(f"\n[FINAL ANSWER] {sanitized_answer}")`
- Ensures safe output to user

---

### H-10: Query Hashing for Deduplication
**Function:** `generate_query_hash(query: str) -> str`

**Purpose:** Create unique identifier for caching and historical lookup

**Method:**
1. Canonicalize query (remove variations) - uses H-01
2. Convert to lowercase
3. Generate SHA-256 hash
4. Return first 16 characters

**Usage:**
- Check if query was recently answered (cache hit)
- Store in historical index
- Detect duplicate queries

**Example:**
```python
Input: "Calculate  2  +  2"
Canonical: "calculate 2 + 2"
Output: "a1b2c3d4e5f6g7h8"
```

**Integration:**
- **Critical for Caching System:**
  - Hash stored in `processed_query['query_hash']`
  - Used by `HistoricalContextManager.check_duplicate(hash)`
  - Enables 1-hour cache window for instant duplicate answers
  - Stored in `historical_conversation_store.json` index

**Core Logic Flow:**
```python
# In agent.py:
query_hash = processed_query['query_hash']  # From H-10
duplicate = historical_mgr.check_duplicate(query_hash)
if duplicate:
    return cached_answer  # Instant response, no processing
```

---

## Combined Pipelines

### Preprocessing Pipeline
**Function:** `preprocess_query(query: str) -> Dict[str, Any]`

**Combines:** H-01, H-02, H-03, H-04, H-05, H-10

**Returns:**
```python
{
    "original": "original query",
    "canonical": "normalized query",           # H-01
    "entities": {"numbers": [...], "names": [...]},  # H-02
    "query_type": "math",                     # H-03
    "topic": "mathematics",                   # H-04
    "query_hash": "abc123...",                # H-10
    "suggested_tools": ["tool1", "tool2"]     # H-05
}
```

**Integration in agent.py:**
```python
# Line 60: Preprocessing
processed_query = preprocess_query(user_input)

# Line 68: Cache check using hash
duplicate = historical_mgr.check_duplicate(processed_query['query_hash'])

# Line 78: Historical context using topic
historical_context = historical_mgr.format_context_for_prompt(
    processed_query['topic'],  # From H-04
    limit=3
)

# Line 96: Attach to context
context.processed_query = processed_query
context.historical_context = historical_context
```

---

### Postprocessing Pipeline
**Function:** `postprocess_result(result: Any, result_text: str) -> Dict[str, Any]`

**Combines:** H-06, H-07, H-08, H-09

**Returns:**
```python
{
    "is_valid": True,                         # H-06
    "confidence": {"score": 0.8, "indicators": [...]},  # H-07
    "is_incomplete": False,                   # H-08
    "sanitized_output": "cleaned result"      # H-09
}
```

**Integration in agent.py:**
```python
# Line 109: Postprocessing
post_result = postprocess_result(result, answer)

# Line 111-112: Logging
log("heuristics", f"Confidence: {post_result['confidence']['score']:.2f}")
log("heuristics", f"Incomplete: {post_result['is_incomplete']}")

# Line 116: Display sanitized output
sanitized_answer = post_result['sanitized_output']
print(f"\n[FINAL ANSWER] {sanitized_answer}")

# Line 138: Store confidence in metadata
metadata={
    "confidence": post_result['confidence']['score'],
    ...
}
```

---

## Integration with Core System

### 1. Agent Entry Point (agent.py)

**Flow:**
```python
async def main():
    # Initialize
    historical_mgr = HistoricalContextManager()
    multi_mcp = MultiMCP(...)
    
    while True:
        user_input = input("...")
        
        # === PREPROCESSING (Heuristics H-01 to H-05, H-10) ===
        processed_query = preprocess_query(user_input)
        
        # === CACHE CHECK (H-10 hash) ===
        duplicate = historical_mgr.check_duplicate(processed_query['query_hash'])
        if duplicate:
            return cached_answer
        
        # === HISTORICAL CONTEXT (H-04 topic) ===
        historical_context = historical_mgr.format_context_for_prompt(
            processed_query['topic'], limit=3
        )
        
        # === AGENT LOOP ===
        context = AgentContext(...)
        context.processed_query = processed_query
        context.historical_context = historical_context
        agent = AgentLoop(context)
        result = await agent.run()
        
        # === POSTPROCESSING (Heuristics H-06 to H-09) ===
        post_result = postprocess_result(result, answer)
        
        # === STORAGE ===
        historical_mgr.add_conversation(
            query=user_input,
            query_hash=processed_query['query_hash'],  # H-10
            topic=processed_query['topic'],            # H-04
            result=final_answer,
            metadata={
                "query_type": processed_query['query_type'],  # H-03
                "confidence": post_result['confidence']['score'],  # H-07
                "entities": processed_query['entities']  # H-02
            }
        )
```

---

### 2. Agent Loop (core/loop.py)

**OODA Cycle:**
```python
class AgentLoop:
    async def run(self):
        for step in range(max_steps):
            # === OBSERVE: Perception ===
            perception = await run_perception(context)
            # Uses: processed_query['suggested_tools'] (H-05) as hints
            
            # === ORIENT/DECIDE: Planning ===
            plan = await generate_plan(
                user_input=context.user_input,
                historical_context=context.historical_context,  # From H-04
                ...
            )
            # Historical context injected into prompt for better planning
            
            # === ACT: Execution ===
            result = await run_python_sandbox(plan, dispatcher=self.mcp)
            
            # Post-processing in loop.py (auto-summarization for long answers)
            if is_raw_chunk:
                summary = await model.generate_text(summarize_prompt)
                result = f"FINAL_ANSWER: {summary}"
```

---

### 3. Historical Context System (modules/historical_context.py)

**Topic-Based Storage:**
```python
class HistoricalContextManager:
    def add_conversation(self, query, query_hash, topic, result, ...):
        # Store by topic (from H-04)
        self.store["topics"][topic]["conversations"].append({
            "query": query,
            "query_hash": query_hash,  # From H-10
            "result": result,
            "metadata": {
                "query_type": ...,     # From H-03
                "confidence": ...,     # From H-07
                "entities": ...         # From H-02
            }
        })
        
        # Index by hash (for cache lookup)
        self.store["index"]["by_hash"][query_hash] = {
            "topic": topic,
            "timestamp": ...,
            "result_summary": ...
        }
    
    def format_context_for_prompt(self, topic, limit=3):
        # Retrieve past conversations from same topic (H-04)
        conversations = self.store["topics"][topic]["conversations"]
        # Format for LLM prompt injection
        return formatted_context
```

**Integration:**
- H-04 (Topic Triage) determines which topic's history to retrieve
- H-10 (Query Hash) enables duplicate detection
- H-03 (Query Type) and H-07 (Confidence) stored in metadata for analytics

---

### 4. MCP Tool Execution (modules/action.py)

**Sandbox Execution:**
```python
async def run_python_sandbox(code: str, dispatcher: Any) -> str:
    # Create sandbox
    sandbox = types.ModuleType("sandbox")
    sandbox.mcp = SandboxMCP(dispatcher)
    
    # Preload modules (json, re, math)
    sandbox.__dict__["json"] = json
    sandbox.__dict__["re"] = re
    sandbox.__dict__["math"] = math
    
    # Execute solve() function
    exec(compile(code, "<solve_plan>", "exec"), sandbox.__dict__)
    solve_fn = sandbox.__dict__.get("solve")
    result = await solve_fn()
    
    return result
```

**Tool Result Extraction:**
- Handles MCP `CallToolResult` objects
- Extracts list[str] from `TextContent` array
- Supports JSON parsing for structured results
- Logs all tool calls for debugging

---

## Complete Execution Flow

### Example: Math Query
```
User: "Calculate factorial of 7 and then find square root"

1. PREPROCESSING (heuristics.py):
   H-01: "calculate factorial of 7 and then find square root"
   H-02: entities = {"numbers": ["7"]}
   H-03: query_type = "math"
   H-04: topic = "mathematics"
   H-05: suggested_tools = ["factorial", "sqrt"]
   H-10: query_hash = "abc123..."

2. CACHE CHECK (historical_context.py):
   historical_mgr.check_duplicate("abc123...")
   → Cache miss, continue

3. HISTORICAL CONTEXT (historical_context.py):
   historical_mgr.format_context_for_prompt("mathematics", limit=3)
   → Returns past math queries for context

4. PERCEPTION (perception.py):
   Input: query + historical context
   Output: selected_servers = ["math"]
   Uses: suggested_tools (H-05) as hints

5. DECISION (decision.py):
   Input: query + historical context + tool descriptions
   Output: solve() function code
   Uses: historical context to learn from past similar queries

6. ACTION (action.py):
   Execute solve() in sandbox
   → Calls factorial(7) → 5040
   → Calls sqrt(5040) → 70.99...
   → Returns "FINAL_ANSWER: 70.99..."

7. POSTPROCESSING (heuristics.py):
   H-06: is_valid = True
   H-07: confidence = 0.8 (high - calculated result)
   H-08: is_incomplete = False
   H-09: sanitized_output = "70.99..."

8. STORAGE (historical_context.py):
   historical_mgr.add_conversation(
       query="...",
       query_hash="abc123...",  # H-10
       topic="mathematics",      # H-04
       result="70.99...",
       metadata={
           "query_type": "math",  # H-03
           "confidence": 0.8,     # H-07
           "entities": {"numbers": ["7"]}  # H-02
       }
   )

9. DISPLAY:
   [FINAL ANSWER] 70.99...
```

---

## Benefits

### 1. **Improved Reliability**
- Query normalization reduces ambiguity
- Entity extraction improves perception accuracy
- JSON validation catches malformed responses
- Confidence scoring provides quality metrics

### 2. **Better Performance**
- Cache hits avoid redundant processing (H-10)
- Tool suggestions reduce search space (H-05)
- Topic-based retrieval finds relevant context faster (H-04)
- Historical context improves LLM planning accuracy

### 3. **Enhanced User Experience**
- Sanitized output is cleaner and safer (H-09)
- Confidence scores build trust (H-07)
- Incomplete detection enables better feedback (H-08)
- Consistent query handling (H-01)

### 4. **Learning Over Time**
- Historical context improves with usage (H-04)
- Topic-based storage enables domain expertise
- Query hashing prevents duplicate work (H-10)
- Confidence tracking identifies improvement areas (H-07)

---

## Testing Scenarios

### Scenario 1: Math Query
```
Query: "Calculate ASCII of INDIA"
→ H-03: Classifies as "math"
→ H-04: Topic "mathematics"
→ H-05: Suggests ["strings_to_chars_to_int"]
→ H-10: Generates hash for deduplication
→ Historical: Retrieves past math queries
→ Result: Calculated value with high confidence
```

### Scenario 2: Document Query
```
Query: "What is relationship between Gensol and Go-Auto?"
→ H-02: Extracts names ["Gensol", "Go-Auto"]
→ H-03: Classifies as "document"
→ H-04: Topic "documents"
→ H-05: Suggests ["search_stored_documents"]
→ Historical: Retrieves past document searches
→ Result: Relationship information with confidence score
```

### Scenario 3: Hybrid Query
```
Query: "Find DLF payment amount and calculate its log value"
→ H-03: Classifies as "hybrid"
→ H-04: Topic "finance"
→ H-05: Suggests ["search_stored_documents", "logarithm"]
→ Multi-step processing with historical context
→ Result: Payment amount + log value with confidence
```

### Scenario 4: Cache Hit
```
Query: "Calculate factorial of 7" (run twice within 1 hour)
First run:
→ H-10: Generates hash "abc123..."
→ Cache miss → Full processing
→ Stores result with hash

Second run:
→ H-10: Generates same hash "abc123..."
→ Cache hit → Instant return
→ No processing needed
```

---

## Metrics and Monitoring

### Query Statistics
- Total queries processed
- Queries by type (H-03)
- Queries by topic (H-04)
- Cache hit rate (H-10)

### Quality Metrics
- Average confidence score (H-07)
- Incomplete answer rate (H-08)
- Success rate by topic
- Tool suggestion accuracy (H-05)

### Performance Metrics
- Cache hit time savings
- Historical context retrieval time
- Preprocessing overhead
- Postprocessing overhead

---

## Future Enhancements

1. **ML-Based Classification:** Replace keyword matching with trained models
2. **Dynamic Tool Learning:** Learn tool effectiveness from history
3. **Context Window Optimization:** Adaptive historical context sizing
4. **Feedback Loop:** User ratings to improve confidence scoring
5. **Cross-Topic Learning:** Identify related topics for better context
6. **Confidence Calibration:** Improve confidence scoring accuracy
7. **Entity Linking:** Connect extracted entities to knowledge base

---

## Summary

The 10 heuristics work together as a comprehensive quality assurance system integrated into the core Cortex-R agent architecture:

**Pre-processing (5):** Clean, classify, and enrich queries  
**Post-processing (5):** Validate, score, and sanitize results

**Core Integration:**
- **H-04 (Topic)** → Historical context retrieval
- **H-10 (Hash)** → Cache system
- **H-05 (Tools)** → Perception hints
- **H-07 (Confidence)** → Quality metrics
- **H-02 (Entities)** → Metadata storage

**Result:** More reliable, efficient, and user-friendly agent behavior with continuous learning from historical context.

---

**Implementation Status:** ✅ Complete  
**Version:** 2.0 Enhanced  
**Date:** November 15, 2025  
**Integration:** Fully integrated with Cortex-R agent architecture
