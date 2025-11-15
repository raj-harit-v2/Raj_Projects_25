"""
Phase 3 Query Execution Script
Executes 3 brand-new unique queries and captures detailed logs
"""

import asyncio
import sys
import datetime
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Add parent directory to path
sys.path.insert(0, '.')

from agent import main

# Three brand-new queries NOT in original agent.py
UNIQUE_QUERIES = [
    "Calculate the square root of 144 and then find its factorial value",
    "Search documents to find what Don Tapscott's book Wikinomics discusses about mass collaboration",
    "What is 25 multiplied by 4 and does this number appear in any document about policies?"
]

async def execute_query_with_logging(query, query_num):
    """Execute a single query and capture all output"""
    print(f"\n{'='*70}")
    print(f"  EXECUTING QUERY {query_num}/3")
    print('='*70)
    print(f"Query: {query}")
    print('='*70 + "\n")
    
    log_file = f"logs/Query_{query_num}_Detailed_Log.txt"
    
    # Capture stdout
    output = StringIO()
    
    try:
        # Note: This is a simplified capture - in practice, run agent.py
        # manually and copy the output
        print(f"[INFO] To capture full logs:")
        print(f"  1. Run: python agent.py")
        print(f"  2. Enter query: {query}")
        print(f"  3. Copy full console output")
        print(f"  4. Save to: {log_file}")
        print(f"\n[TEMPLATE] Use Query_Execution_Template.md structure")
        
    except Exception as e:
        print(f"[ERROR] {e}")

def create_log_template(query_num, query):
    """Create pre-filled log template for manual completion"""
    template = f"""# Query {query_num} Execution Log - Detailed

## Query Information
**Query:** {query}
**Timestamp:** {datetime.datetime.now().isoformat()}
**Query Number:** {query_num}/3
**Type:** Brand-New Unique Query (not in original agent.py)

---

## INSTRUCTIONS FOR COMPLETION:
1. Run: python agent.py
2. Type the query above when prompted
3. Copy the ENTIRE console output below
4. Fill in all sections with actual execution data

---

## Phase 1: Heuristics Preprocessing

### User Input:
```
[Copy from console: User typed query]
```

### Heuristics Analysis:
```
[Copy from console: All [heuristics] logs]
[heuristics] Preprocessing query...
[heuristics] Query Type: [type]
[heuristics] Topic: [topic]
[heuristics] Query Hash: [hash]
[heuristics] Entities: [entities]
[heuristics] Suggested Tools: [tools]
```

### Historical Context:
```
[Copy from console: [historical] logs]
[historical] Retrieved [topic] context
[historical] Cache check: [Hit/Miss]
```

---

## Phase 2: Perception

### Perception Output:
```
[Copy from console: [perception] logs]
[perception] Raw output: [JSON]
[perception] Intent: [intent]
[perception] Selected Servers: [servers]
```

### Tools Available:
```
[List tools that were available from selected servers]
```

---

## Phase 3: Planning/Decision

### Strategy:
```
[strategy] Planning mode: conservative
[strategy] Using prompt: New_Decision_Prompt.txt
```

### Generated Plan:
````
[Copy the COMPLETE solve() function that was generated]
[plan] Generated solve() function:

async def solve():
    [PASTE COMPLETE GENERATED CODE HERE]
````

---

## Phase 4: Execution

### Sandbox Entry:
```
[loop] Detected solve() plan - running sandboxed...
[action] Entered run_python_sandbox()
```

### Tool Executions:
```
[Copy all tool execution logs]
[tool] Call 1: [tool_name]
[tool] Arguments: [args]
[tool] Result: [result]

[tool] Call 2: [tool_name] (if applicable)
[tool] Arguments: [args]
[tool] Result: [result]
```

---

## Phase 5: Result & Postprocessing

### Heuristics Validation:
```
[heuristics] Postprocessing result...
[heuristics] Confidence: [score]
[heuristics] Incomplete: [true/false]
```

### Final Answer:
```
[FINAL ANSWER] [Copy the actual answer displayed to user]
```

Or if multi-step:
```
[FURTHER PROCESSING] [intermediate result]
[Then subsequent steps...]
```

---

## Phase 6: Historical Storage

### Storage Confirmation:
```
[storage] Stored conversation
[storage] Topic: [topic]
[storage] Query Hash: [hash]
```

---

## Complete Console Output

### Full Execution Trace:
````
[PASTE COMPLETE CONSOLE OUTPUT FROM START TO FINISH]
````

---

## Analysis & Observations

### What Worked Well:
- [Your observations]

### Heuristics Impact:
- Query Type Classification: [observation]
- Topic Triage: [observation]
- Confidence Scoring: [score and meaning]

### Historical Context:
- Was historical context used? [Yes/No]
- If yes, how did it help? [observation]

### Performance:
- Number of steps: [X]/5
- Tools called: [N]
- Approximate time: [X seconds]

### Learning Stored:
- Topic: [topic where it was stored]
- Will benefit: [future similar queries]

---

**Status:** [SUCCESS/PARTIAL/FAILED]
**Confidence:** [score]/1.0
**Logged:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    log_path = f"logs/Query_{query_num}_Log.md"
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"[CREATED] {log_path}")
    return log_path

def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("  PHASE 3: QUERY EXECUTION PREPARATION")
    print("="*70)
    
    # Create logs directory
    import os
    os.makedirs('logs', exist_ok=True)
    print("[INFO] Created logs/ directory")
    
    # Create templates for all 3 queries
    print("\n[INFO] Creating log templates for 3 unique queries...")
    for i, query in enumerate(UNIQUE_QUERIES, 1):
        log_path = create_log_template(i, query)
    
    print("\n" + "="*70)
    print("  READY TO EXECUTE QUERIES")
    print("="*70)
    print("\nNEXT STEPS:")
    print("1. Run: python agent.py")
    print("2. Execute each query manually")
    print("3. Copy full console output")
    print("4. Fill in the log templates")
    print("\nQUERIES TO RUN:")
    for i, query in enumerate(UNIQUE_QUERIES, 1):
        print(f"  {i}. {query}")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()

