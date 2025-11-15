# Cortex-R Agent: Architectural Flow Documentation

## Overview
Cortex-R is a **reasoning-driven AI agent** designed to solve complex tasks by combining perception, planning, and action execution. It uses a **modular architecture** with external tool servers (MCP) and maintains session memory for multi-step reasoning.

---

## 🎯 Core Architectural Pattern

The system follows a **Cognitive Loop Architecture** inspired by the Observe-Orient-Decide-Act (OODA) loop:

```
User Input → Perception → Planning/Decision → Action/Execution → Memory Update → [Loop]
```

---

## 📦 Component Architecture

### 1. **Entry Point: agent.py**
**Purpose:** Main orchestrator and user interface

**Flow:**
1. Load configuration from `config/profiles.yaml`
2. Initialize MultiMCP with all MCP server configs
3. Wait for user input in REPL loop
4. Create AgentContext for each query
5. Initialize and run AgentLoop
6. Display final answer to user
7. Support session continuity (can continue previous session or start new)

**Key Features:**
- Session management (new/continue)
- User interaction loop
- Exit handling

---

### 2. **Context Management: core/context.py**

**Components:**

#### A. **AgentProfile**
- Loads configuration from `profiles.yaml`
- Contains:
  - Agent metadata (name, id, description)
  - Strategy configuration (planning mode, exploration mode, max steps, lifelines)
  - Memory configuration
  - LLM configuration
  - Persona settings

#### B. **AgentContext**
- Central state container for each agent execution
- Contains:
  - User input (current and override for re-processing)
  - Session ID (auto-generated with timestamp)
  - AgentProfile instance
  - MemoryManager instance
  - MultiMCP dispatcher reference
  - MCP server descriptions
  - Current step number
  - Task progress tracker
  - Final answer

**Key Methods:**
- `add_memory()` - Add memory items
- `log_subtask()` - Log tool execution start
- `update_subtask_status()` - Update tool execution status

---

### 3. **Session Management: core/session.py**

**Components:**

#### A. **MCP (Single Server Client)**
- Lightweight wrapper for single MCP server
- Uses stdio transport
- Each call creates fresh subprocess connection
- Methods:
  - `list_tools()` - Get available tools from server
  - `call_tool()` - Execute a tool

#### B. **MultiMCP (Multi-Server Manager)**
- Manages multiple MCP servers
- Tool discovery and routing
- Maintains tool-to-server mapping

**Initialization Flow:**
1. For each server config:
   - Create stdio connection
   - Initialize MCP session
   - List all tools from server
   - Build tool_map (tool_name → server config + tool object)
   - Build server_tools (server_id → list of tools)
2. Close temporary connections (stateless design)

**Tool Execution Flow:**
1. Lookup tool in tool_map
2. Get associated server config
3. Create fresh stdio connection to that server
4. Initialize session
5. Call the tool
6. Return result
7. Close connection

---

### 4. **Agent Loop: core/loop.py**

**Purpose:** Main execution orchestrator implementing the cognitive loop

**Configuration:**
- Max steps (e.g., 3) - maximum reasoning iterations
- Max lifelines per step (e.g., 3) - retry attempts per step

**Execution Flow:**

```
FOR each step (1 to max_steps):
    SET lifelines = max_lifelines_per_step
    
    WHILE lifelines >= 0:
        
        ┌─────────────────────────────────────┐
        │ PHASE 1: PERCEPTION                 │
        └─────────────────────────────────────┘
        - Call run_perception() with context
        - Get perception result with selected_servers
        - Retrieve tools from selected servers
        - If no tools available → abort step
        
        ┌─────────────────────────────────────┐
        │ PHASE 2: PLANNING                   │
        └─────────────────────────────────────┘
        - Summarize available tools
        - Select decision prompt based on strategy
        - Call generate_plan() with:
            * User input
            * Perception result
            * Memory items
            * Tool descriptions
            * Prompt path
            * Step number
        - Receive Python code with solve() function
        
        ┌─────────────────────────────────────┐
        │ PHASE 3: EXECUTION                  │
        └─────────────────────────────────────┘
        - Validate plan contains solve() function
        - If valid:
            * Run in Python sandbox (run_python_sandbox)
            * Execute solve() function
            * Parse result:
                - FINAL_ANSWER: → Success, exit
                - FURTHER_PROCESSING_REQUIRED: → Set override input, continue
                - Error → Decrement lifeline, retry
        - If invalid:
            * Decrement lifeline, retry
        
        ┌─────────────────────────────────────┐
        │ PHASE 4: MEMORY UPDATE              │
        └─────────────────────────────────────┘
        - Log tool execution
        - Store results in memory
        - Update task progress
    
    IF final_answer found → RETURN
    
IF max_steps reached → RETURN default answer
```

**Result Handling:**
- **FINAL_ANSWER:** - Task complete, return to user
- **FURTHER_PROCESSING_REQUIRED:** - Create override input with context, continue loop
- **Error/Invalid** - Retry with lifeline, if exhausted move to next step

---

### 5. **Perception Module: modules/perception.py**

**Purpose:** Understand user intent and select relevant MCP servers

**Input:**
- User query
- MCP server descriptions (from profiles.yaml)

**Process:**
1. Format server list with descriptions
2. Create perception prompt with:
   - Available servers
   - User input
3. Call LLM (via ModelManager)
4. Parse JSON response

**Output: PerceptionResult**
```python
{
    "intent": str,              # What user wants to do
    "entities": [str],          # Key entities mentioned
    "tool_hint": str,           # Suggested tool category
    "tags": [str],              # Classification tags
    "selected_servers": [str]   # MCP servers to use
}
```

**Fallback:** If parsing fails, select all servers

---

### 6. **Decision/Planning Module: modules/decision.py**

**Purpose:** Generate executable Python plan (solve function)

**Input:**
- User input
- Perception result
- Memory items (past interactions)
- Tool descriptions (filtered by perception)
- Prompt path (based on strategy)
- Step number and max steps

**Process:**
1. Load decision prompt template
2. Inject tool descriptions and user input
3. Call LLM to generate solve() function
4. Validate output contains async/sync def solve()
5. Remove code fence markers if present

**Output:**
- Python code string containing solve() function
- Function can call MCP tools via `mcp.call_tool()`
- Must return FINAL_ANSWER: or FURTHER_PROCESSING_REQUIRED:

**Example Generated Plan:**
```python
async def solve():
    # Step 1: Extract ASCII values
    result = await mcp.call_tool('strings_to_chars_to_int', {
        "input": {"string": "INDIA"}
    })
    ascii_values = result.content[0].text
    
    # Step 2: Calculate exponential sum
    result = await mcp.call_tool('int_list_to_exponential_sum', {
        "input": {"numbers": ascii_values}
    })
    
    return f"FINAL_ANSWER: {result.content[0].text}"
```

---

### 7. **Strategy Selection: core/strategy.py**

**Purpose:** Select appropriate decision prompt based on agent strategy

**Strategies:**

#### A. **Conservative Mode**
- Plan one tool call at a time
- Safer, more predictable
- Prompt: `prompts/decision_prompt_conservative.txt`

#### B. **Exploratory Mode**
- Can plan multiple tool calls
- Two sub-modes:
  - **Parallel:** Execute tools simultaneously
    - Prompt: `prompts/decision_prompt_exploratory_parallel.txt`
  - **Sequential:** Execute tools in sequence
    - Prompt: `prompts/decision_prompt_exploratory_sequential.txt`

**Memory Fallback:**
- If tool discovery fails and memory_fallback_enabled=true
- Look for recently successful tools in memory
- Use those tools for planning

**Functions:**
- `select_decision_prompt_path()` - Choose correct prompt
- `conservative_plan()` - Single tool planning
- `exploratory_plan()` - Multi-tool planning with fallback
- `generate_plan()` - LLM call to create solve()
- `find_recent_successful_tools()` - Memory-based tool discovery

---

### 8. **Action/Execution Module: modules/action.py**

**Purpose:** Execute generated Python code in isolated sandbox

**Safety Features:**
- Isolated module scope (types.ModuleType)
- Limited built-ins (json, re)
- Tool call counter (max 5 per plan)

**Process:**
1. Create sandbox module
2. Inject SandboxMCP class with real dispatcher
3. Compile and execute the plan code
4. Extract solve() function from sandbox namespace
5. Check if async or sync
6. Execute solve()
7. Parse and format result

**SandboxMCP:**
- Wraps real MultiMCP dispatcher
- Counts tool calls (max: MAX_TOOL_CALLS_PER_PLAN = 5)
- Prevents infinite loops
- Real tool execution (not mocked)

**Result Formatting:**
- Dict with "result" key → extract result
- List → join as string
- String → return as-is
- Exception → return error message

---

### 9. **Memory Module: modules/memory.py**

**Components:**

#### A. **MemoryItem (Pydantic Model)**
```python
{
    "timestamp": float,
    "type": str,  # run_metadata, tool_call, tool_output, final_answer
    "text": str,
    "tool_name": Optional[str],
    "tool_args": Optional[dict],
    "tool_result": Optional[dict],
    "final_answer": Optional[str],
    "tags": Optional[List[str]],
    "success": Optional[bool],
    "metadata": Optional[dict]
}
```

#### B. **MemoryManager**
**Purpose:** Session memory persistence

**Storage Structure:**
```
memory/
  └── YYYY/
      └── MM/
          └── DD/
              └── session-{timestamp}-{uid}.json
```

**Methods:**
- `load()` - Load session from disk
- `save()` - Persist to disk
- `add()` - Add memory item
- `add_tool_call()` - Log tool invocation
- `add_tool_output()` - Log tool result with success flag
- `add_final_answer()` - Log final answer
- `find_recent_successes()` - Get recent successful tools
- `get_session_items()` - Get all items for session

---

### 10. **Model Manager: modules/model_manager.py**

**Purpose:** Unified LLM interface

**Configuration:**
- Loads from `config/models.json` and `config/profiles.yaml`
- Supports multiple backends

**Supported Models:**

#### A. **Gemini (Google)**
- Uses google.genai.Client
- API key from .env (GEMINI_API_KEY)
- Model: gemini-2.0-flash-exp (or configured)

#### B. **Ollama (Local)**
- HTTP API to localhost:11434
- Models: phi4, gemma3:12b, qwen2.5:32b-instruct-q4_0

**Method:**
- `generate_text(prompt: str) -> str`
  - Abstracts model-specific API calls
  - Returns plain text response

---

### 11. **MCP Servers (Tool Providers)**

**Architecture:** Each server is a standalone FastMCP application

#### A. **mcp_server_1.py (Math Server)**
**Tools:**
- Basic arithmetic: add, subtract, multiply, divide
- Advanced math: power, cbrt, factorial, remainder
- Trigonometry: sin, cos, tan
- String operations: strings_to_chars_to_int
- List operations: int_list_to_exponential_sum, fibonacci_numbers
- Image: create_thumbnail
- Execution: run_python_sandbox, run_shell_command, run_sql_query

#### B. **mcp_server_2.py (Documents Server)**
**Tools:**
- search_stored_documents (FAISS vector search)
- convert_webpage_url_into_markdown (Trafilatura)
- extract_pdf (PyMuPDF4LLM)
- Chunking and embedding with Ollama

**Features:**
- RAG (Retrieval Augmented Generation)
- Document indexing with FAISS
- Semantic search
- LLM-based chunk merging

#### C. **mcp_server_3.py (Web Search Server)**
**Tools:**
- duckduckgo_search_results
- download_raw_html_from_url

**Communication Protocol:**
- FastMCP framework
- Stdio transport (stdin/stdout)
- JSON-RPC messages
- Pydantic models for type safety

---

### 12. **Configuration System**

#### A. **config/profiles.yaml**
```yaml
agent:
  name: Cortex-R
  id: cortex_r_002
  description: Reasoning-driven AI agent

strategy:
  planning_mode: conservative  # or exploratory
  exploration_mode: parallel   # or sequential
  memory_fallback_enabled: true
  max_steps: 3
  max_lifelines_per_step: 3

memory:
  memory_service: true
  summarize_tool_results: true
  tag_interactions: true

llm:
  text_generation: gemini  # or phi4, gemma3:12b
  embedding: nomic

mcp_servers:
  - id: math
    script: mcp_server_1.py
    cwd: /path/to/project
    description: Math and computation tools
    capabilities: [add, subtract, ...]
    
  - id: documents
    script: mcp_server_2.py
    ...
```

#### B. **config/models.json**
```json
{
  "models": {
    "gemini": {
      "type": "gemini",
      "model": "gemini-2.0-flash-exp"
    },
    "phi4": {
      "type": "ollama",
      "model": "phi4:latest",
      "url": {
        "generate": "http://localhost:11434/api/generate"
      }
    }
  }
}
```

---

### 13. **Utility Modules**

#### A. **modules/tools.py**
- `extract_json_block()` - Parse JSON from LLM response
- `summarize_tools()` - Format tool list for prompts
- `filter_tools_by_hint()` - Filter tools by perception hint
- `load_prompt()` - Load prompt templates

---

## 🔄 Complete End-to-End Flow

### Example: "Find the ASCII values of characters in INDIA and return sum of exponentials"

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                                    │
└─────────────────────────────────────────────────────────────────┘
User enters query in agent.py REPL

┌─────────────────────────────────────────────────────────────────┐
│ 2. INITIALIZATION (agent.py)                                    │
└─────────────────────────────────────────────────────────────────┘
- Load profiles.yaml
- Initialize MultiMCP with all servers
- Discover tools from all servers
- Create AgentContext with:
    * user_input
    * session_id (auto-generated)
    * MultiMCP dispatcher
    * MCP server descriptions

┌─────────────────────────────────────────────────────────────────┐
│ 3. AGENT LOOP START (core/loop.py)                             │
└─────────────────────────────────────────────────────────────────┘
Step 1 of 3, Lifelines: 3

┌─────────────────────────────────────────────────────────────────┐
│ 4. PERCEPTION (modules/perception.py)                          │
└─────────────────────────────────────────────────────────────────┘
Input: User query + MCP server descriptions
Process:
  - Format prompt with available servers
  - Call LLM via ModelManager
  - Parse response
Output: PerceptionResult
  {
    "intent": "string manipulation and math",
    "entities": ["INDIA", "ASCII", "exponential"],
    "tool_hint": "string_math",
    "tags": ["computation"],
    "selected_servers": ["math"]
  }

Get tools from "math" server

┌─────────────────────────────────────────────────────────────────┐
│ 5. PLANNING (modules/decision.py)                              │
└─────────────────────────────────────────────────────────────────┘
Input:
  - User input
  - Perception result
  - Memory items (empty for first run)
  - Tool descriptions from math server
  - Prompt: prompts/decision_prompt_conservative.txt

Process:
  - Load prompt template
  - Inject tool descriptions
  - Call LLM to generate Python code

Output: Python code with solve()
```python
async def solve():
    # Convert string to ASCII integers
    result1 = await mcp.call_tool('strings_to_chars_to_int', {
        "input": {"string": "INDIA"}
    })
    ascii_values = json.loads(result1.content[0].text)["result"]
    
    # Calculate exponential sum
    result2 = await mcp.call_tool('int_list_to_exponential_sum', {
        "input": {"numbers": ascii_values}
    })
    exp_sum = json.loads(result2.content[0].text)["result"]
    
    return f"FINAL_ANSWER: {exp_sum}"
```

┌─────────────────────────────────────────────────────────────────┐
│ 6. EXECUTION (modules/action.py)                               │
└─────────────────────────────────────────────────────────────────┘
Process:
  - Create sandbox module
  - Inject SandboxMCP with real dispatcher
  - Compile and exec() the code
  - Extract solve() function
  - Execute: result = await solve()

Internal Flow:
  1. Call strings_to_chars_to_int via MultiMCP
     → MultiMCP routes to math server
     → Server executes tool
     → Returns: {"result": [73, 78, 68, 73, 65]}
  
  2. Call int_list_to_exponential_sum via MultiMCP
     → Server calculates: e^73 + e^78 + e^68 + e^73 + e^65
     → Returns: {"result": 8.9e33}
  
  3. solve() returns: "FINAL_ANSWER: 8.9e33"

┌─────────────────────────────────────────────────────────────────┐
│ 7. RESULT HANDLING (core/loop.py)                              │
└─────────────────────────────────────────────────────────────────┘
- Detect "FINAL_ANSWER:" prefix
- Log to memory as tool_output (success=True)
- Update context.final_answer
- Return {"status": "done", "result": "FINAL_ANSWER: 8.9e33"}

┌─────────────────────────────────────────────────────────────────┐
│ 8. MEMORY PERSISTENCE (modules/memory.py)                      │
└─────────────────────────────────────────────────────────────────┘
Save to: memory/2025/11/12/session-{timestamp}-{uid}.json
Content:
  [
    {
      "timestamp": ...,
      "type": "run_metadata",
      "text": "Started session...",
      "tags": ["run_start"]
    },
    {
      "timestamp": ...,
      "type": "tool_output",
      "text": "Output of solve_sandbox: ...",
      "tool_name": "solve_sandbox",
      "tool_result": {"result": "FINAL_ANSWER: 8.9e33"},
      "success": true,
      "tags": ["sandbox"]
    }
  ]

┌─────────────────────────────────────────────────────────────────┐
│ 9. OUTPUT TO USER (agent.py)                                   │
└─────────────────────────────────────────────────────────────────┘
Display: 💡 Final Answer: 8.9e33

┌─────────────────────────────────────────────────────────────────┐
│ 10. READY FOR NEXT QUERY                                       │
└─────────────────────────────────────────────────────────────────┘
- Session persists (can reference in next query)
- User can continue or type 'new' for fresh session
```

---

## 🎨 Key Design Patterns

### 1. **Cognitive Loop (OODA)**
- **Observe:** Perception module analyzes user intent
- **Orient:** Context and memory provide situational awareness
- **Decide:** Planning module generates action plan
- **Act:** Action module executes plan with tools

### 2. **Modular Tool Architecture**
- Tools are external processes (MCP servers)
- Stateless connections (reconnect per call)
- Language/framework agnostic
- Easily extensible

### 3. **Strategy Pattern**
- Different planning modes (conservative/exploratory)
- Runtime prompt selection
- Configurable behavior via profiles.yaml

### 4. **Sandbox Execution**
- Generated code runs in isolated scope
- Real tool calls but controlled environment
- Call limits prevent infinite loops

### 5. **Memory-Augmented Reasoning**
- Persistent session memory
- Success/failure tracking
- Memory-based fallback for tool discovery

---

## 🛡️ Error Handling & Resilience

### 1. **Lifeline System**
- Each step has multiple retry attempts
- Decrements on failure
- Allows recovery from transient errors

### 2. **Fallback Mechanisms**
- Perception failure → select all servers
- Planning failure → default prompt
- Tool discovery failure → memory fallback
- Max steps reached → graceful exit

### 3. **Validation Layers**
- Perception: JSON parsing with fallback
- Planning: Validate solve() function exists
- Execution: Exception catching and error reporting

---

## 📊 Data Flow Diagram (Text Representation)

```
[User] 
  ↓
[agent.py] → Load config → [profiles.yaml]
  ↓
[MultiMCP.initialize()] → Discover tools → [mcp_server_1, 2, 3]
  ↓
[AgentContext] → Create session → [MemoryManager]
  ↓
[AgentLoop]
  ↓
  ├→ [Perception] → [ModelManager] → [LLM]
  │     ↓
  │   [PerceptionResult: selected_servers]
  │     ↓
  ├→ [Strategy] → Select prompt
  │     ↓
  ├→ [Planning] → [ModelManager] → [LLM]
  │     ↓
  │   [Python code with solve()]
  │     ↓
  ├→ [Action]
  │     ├→ Create sandbox
  │     ├→ Inject SandboxMCP
  │     ├→ Execute solve()
  │     │    ↓
  │     │  [mcp.call_tool()] → [MultiMCP] → [Specific MCP Server]
  │     │    ↓
  │     │  [Tool Result]
  │     ↓
  │   [Result: FINAL_ANSWER or FURTHER_PROCESSING_REQUIRED]
  │     ↓
  └→ [Memory] → Save to disk
       ↓
[agent.py] → Display to user
```

---

## 🔧 Technology Stack

### Core Framework
- **Language:** Python 3.10+
- **Async:** asyncio for concurrent operations
- **Type Safety:** Pydantic models
- **Config:** YAML (profiles.yaml), JSON (models.json)

### MCP (Model Context Protocol)
- **Framework:** FastMCP
- **Transport:** stdio (stdin/stdout)
- **Protocol:** JSON-RPC

### LLM Integration
- **Google Gemini:** google.genai SDK
- **Ollama:** HTTP API (localhost:11434)
- Models: phi4, gemma3:12b, qwen2.5:32b

### Document Processing
- **Web scraping:** Trafilatura
- **PDF extraction:** PyMuPDF4LLM
- **Markdown conversion:** MarkItDown
- **Vector search:** FAISS
- **Embeddings:** Ollama (nomic-embed-text)

### Other Libraries
- PIL/Pillow: Image processing
- NumPy: Numerical operations
- Requests: HTTP calls
- SQLite3: SQL execution support

---

## 📈 Scalability Considerations

### Current Architecture
- Stateless MCP connections (reconnect per call)
- Sequential tool execution in sandbox
- Single-user REPL interface

### Potential Enhancements
1. **Persistent MCP Sessions:** Keep connections alive for better performance
2. **Parallel Tool Execution:** Execute independent tools concurrently
3. **Multi-user Support:** Add session isolation and API server
4. **Distributed Tools:** MCP servers on remote machines
5. **Caching Layer:** Cache LLM responses for identical queries
6. **Tool Versioning:** Manage multiple versions of same tool

---

## 🎯 Use Cases

### 1. **Multi-step Reasoning**
- Complex calculations requiring multiple operations
- Document analysis with follow-up queries

### 2. **RAG (Retrieval Augmented Generation)**
- Search documents, extract relevant info
- Answer questions based on local knowledge

### 3. **Web Research**
- Search internet, extract content
- Synthesize information from multiple sources

### 4. **Code Execution**
- Run Python code snippets
- Execute shell commands (with caution)

### 5. **Data Analysis**
- SQL queries on databases
- Mathematical computations

---

## 🚀 Execution Modes

### Conservative Mode
- **Strategy:** One tool at a time
- **Safety:** High (predictable)
- **Speed:** Moderate (sequential)
- **Best for:** Critical tasks, production

### Exploratory Mode (Parallel)
- **Strategy:** Multiple tools simultaneously
- **Safety:** Medium (complex coordination)
- **Speed:** Fast (parallel execution)
- **Best for:** Research, exploration

### Exploratory Mode (Sequential)
- **Strategy:** Multiple tools in sequence
- **Safety:** Medium (chained dependencies)
- **Speed:** Moderate (sequential but planned ahead)
- **Best for:** Multi-step analysis

---

## 🔐 Security Considerations

### Current Measures
1. **Sandboxed Execution:** Limited built-ins, isolated scope
2. **Tool Call Limits:** Max 5 calls per plan
3. **No Direct File System Access:** Tools handle I/O
4. **Local LLM Option:** Ollama runs locally (no data leaves machine)

### Recommendations
1. Add tool permission system
2. Audit generated code before execution
3. Rate limit tool calls
4. Implement user authentication for multi-user deployments

---

## 📝 Configuration Guide

### Setting Up a New Tool Server

1. Create new MCP server file (e.g., `mcp_server_4.py`)
2. Define tools with FastMCP decorators
3. Use Pydantic models from `models.py`
4. Add to `config/profiles.yaml`:
```yaml
mcp_servers:
  - id: my_server
    script: mcp_server_4.py
    cwd: /path/to/project
    description: "My custom tools"
    capabilities: ["tool1", "tool2"]
```
5. Restart agent

### Changing LLM Model

Edit `config/profiles.yaml`:
```yaml
llm:
  text_generation: phi4  # or gemini, gemma3:12b, qwen2.5:32b
```

Ensure model is available (Ollama) or API key set (.env)

### Adjusting Strategy

```yaml
strategy:
  planning_mode: exploratory  # conservative or exploratory
  exploration_mode: parallel  # parallel or sequential
  max_steps: 5               # increase for complex tasks
  max_lifelines_per_step: 2  # reduce for faster failures
```

---

## 🧪 Testing & Debugging

### Logging
- Timestamped logs for each stage: [HH:MM:SS] [stage] message
- Stages: loop, perception, plan, action, sandbox, memory

### Memory Inspection
- Session files stored in: `memory/YYYY/MM/DD/session-{id}.json`
- Contains full execution trace
- Can replay or analyze past sessions

### Debug Flow
1. Check perception output → Is intent correct?
2. Check plan output → Is solve() valid?
3. Check sandbox execution → Are tools called correctly?
4. Check memory → Are results persisted?

---

## 📚 Glossary

- **MCP:** Model Context Protocol - standard for tool servers
- **Perception:** Understanding user intent and selecting tools
- **Planning:** Generating executable code plan
- **Action:** Executing plan with real tools
- **Sandbox:** Isolated Python execution environment
- **Lifeline:** Retry attempt for failed operations
- **Session:** Continuous conversation with memory
- **Context:** State container for agent execution
- **Strategy:** Approach to planning (conservative/exploratory)
- **FAISS:** Facebook AI Similarity Search (vector database)
- **RAG:** Retrieval Augmented Generation

---

## 🎓 Summary for Diagramming

### Key Components (Boxes)
1. User Interface (agent.py)
2. Agent Loop (core/loop.py)
3. Perception Module (modules/perception.py)
4. Decision/Planning Module (modules/decision.py)
5. Action/Execution Module (modules/action.py)
6. Memory Manager (modules/memory.py)
7. Model Manager (modules/model_manager.py)
8. MultiMCP Dispatcher (core/session.py)
9. MCP Server 1 (Math)
10. MCP Server 2 (Documents)
11. MCP Server 3 (Web Search)
12. Configuration (profiles.yaml, models.json)
13. LLM (Gemini/Ollama)

### Key Flows (Arrows)
1. User → Agent → Context
2. Agent → Loop → Perception → LLM
3. Perception → Planning → LLM
4. Planning → Action → Sandbox
5. Sandbox → MultiMCP → MCP Servers
6. MCP Servers → Tools → Results
7. Results → Memory → Disk
8. Memory → Agent → User

### Decision Points (Diamonds)
1. Valid solve()? → Yes/No
2. FINAL_ANSWER? → Yes/No
3. Lifelines remaining? → Yes/No
4. Max steps reached? → Yes/No

---

## 🏗️ Architecture Diagram Layers

### Layer 1: User Interaction
- REPL Interface
- Input/Output

### Layer 2: Orchestration
- Agent Loop
- Context Management
- Strategy Selection

### Layer 3: Cognitive Processing
- Perception (Observe)
- Planning (Decide)
- Action (Act)

### Layer 4: Execution
- Python Sandbox
- Tool Dispatcher (MultiMCP)

### Layer 5: Tools
- MCP Server 1 (Math)
- MCP Server 2 (Documents)
- MCP Server 3 (Web)

### Layer 6: Infrastructure
- LLM (Gemini/Ollama)
- Memory Storage
- Configuration

---

## 🎯 Key Takeaways

1. **Modular Design:** Each component has clear responsibility
2. **Extensible:** Easy to add new tools via MCP servers
3. **Resilient:** Multiple retry mechanisms and fallbacks
4. **Stateful:** Session memory enables multi-turn reasoning
5. **Safe:** Sandboxed execution with limits
6. **Flexible:** Configurable strategies and models
7. **Observable:** Comprehensive logging and memory traces

---

**Document Version:** 1.0  
**Last Updated:** November 12, 2025  
**Author:** Rajeev (via Cortex-R Analysis)
