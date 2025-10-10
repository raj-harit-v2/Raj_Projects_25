# Interactive Chain of Thought Pythagorean Triple Finder

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![MCP](https://img.shields.io/badge/MCP-1.16.0-green)
![Status](https://img.shields.io/badge/status-active-success)

## 📖 Overview

An interactive tool that uses **Model Context Protocol (MCP)** to analyze Pythagorean triples with step-by-step reasoning. The system provides structured JSON reviews of reasoning quality for each operation.

### What is a Pythagorean Triple?

A **Pythagorean triple** consists of three positive integers `(a, b, c)` that satisfy the equation:

```
a² + b² = c²
```

**Examples:**
- ✅ **(3, 4, 5)** is a Pythagorean triple: 3² + 4² = 9 + 16 = 25 = 5²
- ✅ **(5, 12, 13)** is a Pythagorean triple: 5² + 12² = 25 + 144 = 169 = 13²
- ✅ **(6, 8, 10)** is a Pythagorean triple: 6² + 8² = 36 + 64 = 100 = 10²

**NOT Pythagorean Triples:**
- ❌ **(1, 2, 3)** - Does not satisfy: 1² + 2² = 5 ≠ 9 = 3²
- ❌ **(2, 3, 4)** - Does not satisfy: 2² + 3² = 13 ≠ 16 = 4²
- ❌ **(4, 5, 6)** - Does not satisfy: 4² + 5² = 41 ≠ 36 = 6²

### Types of Pythagorean Triples

- **Primitive**: GCD(a, b) = 1 (e.g., 3, 4, 5 - no common divisor)
- **Non-Primitive**: GCD(a, b) > 1 (e.g., 6, 8, 10 - all divisible by 2)

## ✨ Key Features

### Interactive Menu Options
1. **Check Triple** - Verify if three numbers form a Pythagorean triple
2. **Find Triples** - Generate all triples up to a maximum value
3. **Calculate GCD** - Compute Greatest Common Divisor with Euclidean algorithm steps
4. **Verify & Classify** - Complete analysis with primitive/non-primitive classification
5. **Exit** - Clean shutdown

### Structured Output
- ✅ **True/False Status Display** - Clear color-coded validity indicators (Green=True, Red=False)
- ✅ **Detailed Analysis** - Full breakdown of calculations and reasoning
- ✅ **JSON Reasoning Reviews** - Quality assessment for every operation

## 🔧 MCP Configuration

### MCP Status: **ACTIVE** ✅

### MCP API Calls
The system makes **4 types of MCP tool calls**:

| Tool Name | Purpose | Returns |
|-----------|---------|---------|
| `check_triple` | Validates if (a, b, c) is Pythagorean | Validity, classification, GCD |
| `find_triples` | Finds all triples where c ≤ max_c | List of primitive & non-primitive triples |
| `calculate_gcd` | Computes GCD(a, b) | Step-by-step Euclidean algorithm |
| `verify_and_classify` | Complete triple analysis | Validation, GCD, classification |

### MCP Server Details
- **Server Script:** `cot_pythagorean_finder.py`
- **Protocol:** stdio (Standard Input/Output)
- **Communication:** JSON-RPC over stdin/stdout
- **Session Management:** Async context managers

### API Call Pattern
```python
result = await session.call_tool(
    "check_triple",
    arguments={"a": 3, "b": 4, "c": 5}
)
```

## 📊 JSON Reasoning Review

Every operation returns a **structured reasoning quality review**:

```json
{
  "explicit_reasoning": true,
  "structured_output": true,
  "tool_separation": true,
  "conversation_loop": true,
  "instructional_framing": true,
  "internal_self_checks": true,
  "reasoning_type_awareness": true,
  "fallbacks": true,
  "overall_clarity": "Excellent: Direct validation with clear classification and GCD computation."
}
```

### Review Criteria

| Criterion | Description |
|-----------|-------------|
| `explicit_reasoning` | Whether reasoning steps are shown |
| `structured_output` | Output is well-formatted |
| `tool_separation` | Clear separation of tool concerns |
| `conversation_loop` | Interactive flow management |
| `instructional_framing` | Clear instructions provided |
| `internal_self_checks` | Validation and error checking |
| `reasoning_type_awareness` | Awareness of reasoning process |
| `fallbacks` | Error handling mechanisms |
| `overall_clarity` | Tool-specific quality assessment |

## 📁 Project Structure

```
my_project_05_prompts_clean/
├── interactive_cot_pythagorean.py  # Main interactive interface (269 lines)
├── cot_pythagorean_finder.py       # MCP server with tools
├── cot_pythagorean_main.py         # AI-powered version with Gemini
├── demo_pythagorean.py             # Automated demo
├── test_cot_pythagorean.py         # Unit tests
├── pythagorean_finder.py           # Core logic
├── pyproject.toml                  # Dependencies
├── uv.lock                         # Locked dependencies
└── README.md                       # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.13+
- `uv` package manager

### Setup
```bash
# Clone or navigate to project directory
cd my_project_05_prompts_clean

# Install dependencies
uv sync

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### Dependencies
```toml
fastmcp>=2.12.4
google-genai>=1.42.0
matplotlib>=3.10.7
mcp>=1.16.0
numpy>=2.2.0
python-dotenv>=1.0.0
rich>=14.1.0
```

## 💻 Usage

### Run Interactive Interface
```bash
python interactive_cot_pythagorean.py
```

### Example Session
```
======================================================================
MENU OPTIONS:
----------------------------------------------------------------------
  [1] Check if numbers form a Pythagorean triple
  [2] Find all triples up to max value
  [3] Calculate GCD (with steps)
  [4] Verify and Classify a triple (complete analysis)
  [5] Exit
----------------------------------------------------------------------

Enter your choice (1-5): 1

Enter three integers:
  First number (a):  3
  Second number (b): 4
  Third number (c):  5

Checking if (3, 4, 5) is a Pythagorean triple...

Valid Pythagorean Triple: True

Analysis: {'valid': True, 'triple': '(3, 4, 5)', 'equation': '3^2 + 4^2 = 5^2', 
'calculation': '9 + 16 = 25', 'primitive': True, 'gcd': 1, 'classification': 
'PRIMITIVE'}...

======================================================================
                    Reasoning Quality Review
======================================================================
{
  "explicit_reasoning": true,
  "structured_output": true,
  ...
}
======================================================================
```

## 📝 Logging & Output

### Console Output Channels
- **stdout**: User interaction and menu display
- **stderr**: MCP server logs and tool execution details

### Log Format
```
[10/10/25 01:48:21] INFO Processing request of type CallToolRequest
FUNCTION CALL: check_triple(3, 4, 5)
+---------------------------- Verification Result ----------------------------+
| Valid Pythagorean Triple!                                                   |
| Triple: (3, 4, 5)                                                           |
+-----------------------------------------------------------------------------+
```

### LLM Log Path
For AI-powered version (`cot_pythagorean_main.py`):
- Logs are not persisted to file by default
- Runtime logs output to stderr
- Gemini API interactions logged in real-time
- Environment variable: `GEMINI_API_KEY` required

To enable file logging, modify:
```python
import logging
logging.basicConfig(
    filename='llm_interactions.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🔍 Important Facts

### 1. **No AI Required for Main Interface**
- `interactive_cot_pythagorean.py` works WITHOUT AI/LLM
- Uses MCP tools directly with user input
- Instant responses, no API calls to external services

### 2. **Subprocess Architecture**
- Main script spawns MCP server as subprocess
- Server runs in separate Python process
- Communication via stdio protocol
- Auto-cleanup on exit

### 3. **Error Handling**
- Comprehensive try-catch blocks
- Input validation for all user entries
- Graceful fallbacks for invalid data
- TaskGroup error suppression for clean exit

### 4. **Color-Coded Output**
- **Green**: Valid triples, success states
- **Red**: Invalid triples, errors
- **Cyan**: Instructions, headers
- **Yellow**: User prompts
- **Magenta**: Reasoning review panels

### 5. **Validation Rules**
- All numbers must be positive integers
- Max_c must be ≥ 3 for triple finding
- Proper Pythagorean check: a² + b² = c²
- GCD-based primitive classification

### 6. **Performance**
- Triples up to c=25: ~0.1 seconds
- GCD calculation: instantaneous
- No external API latency (except AI version)

### 7. **Terminal Compatibility**
- Works in PowerShell, CMD, Bash
- UTF-8 encoding for special characters
- Rich library for cross-platform formatting
- ANSI color support required

## 🧪 Testing

Run tests:
```bash
python test_cot_pythagorean.py
```

Run demo:
```bash
python demo_pythagorean.py
```

## 📚 Documentation Files

- `QUICK_START.md` - Getting started guide
- `INTERACTIVE_COT_GUIDE.md` - Interactive usage tutorial
- `COT_PYTHAGOREAN_README.md` - Chain-of-Thought details
- `PYTHAGOREAN_IMPLEMENTATION_GUIDE.md` - Implementation reference
- `IMPLEMENTATION_SUMMARY.md` - Architecture overview
- `PROMPTS_USED.md` - AI prompts documentation
- `HOW_TO_ADD_TO_GITHUB.md` - Git workflow

## 🛠️ Technical Details

### MCP Session Lifecycle
```python
1. Initialize server parameters (stdio)
2. Create stdio_client connection
3. Open ClientSession context
4. Call session.initialize()
5. Make tool calls as needed
6. Auto-cleanup on context exit
```

### Tool Response Format
All tools return `TextContent` with structured data:
- Dictionary format with consistent keys
- Success/failure indication
- Detailed calculation steps
- Classification metadata

### Async Architecture
- Built on `asyncio` event loop
- Non-blocking I/O for MCP communication
- Concurrent tool execution support
- Clean shutdown handling

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'mcp'"
```bash
uv sync
```

### "Error: unhandled errors in a TaskGroup"
- Normal on Windows during shutdown
- Suppressed by exception handler
- Does not affect functionality

### UTF-8 Encoding Issues
```bash
$env:PYTHONIOENCODING='utf-8'  # Windows
export PYTHONIOENCODING='utf-8'  # Linux/Mac
```

## 🤝 Contributing

This is an educational project demonstrating MCP integration with Chain-of-Thought reasoning.

## 📄 License

Educational/Research Use

## 🔗 Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Rich Terminal](https://github.com/Textualize/rich)

---

**Last Updated:** October 10, 2025  
**Python Version:** 3.13+  
**MCP Version:** 1.16.0  
**Status:** ✅ Production Ready

