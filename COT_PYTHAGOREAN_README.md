# Chain of Thought Pythagorean Triple Finder 🤖📐

An AI-powered Pythagorean triple analyzer that combines the functionality of `cot_tools_consistency.py` (Chain of Thought reasoning) with `pythagorean_finder.py` (Pythagorean triple logic).

---

## 📋 Overview

This project extends the original Pythagorean Triple Finder by adding **AI-powered step-by-step reasoning** using Google's Gemini model through the Model Context Protocol (MCP).

### **What's New:**

| Original (`pythagorean_finder.py`) | New (`cot_pythagorean_finder.py`) |
|-----------------------------------|----------------------------------|
| Manual menu-driven interface | AI-powered natural language interface |
| Direct calculations | Step-by-step reasoning with explanations |
| Simple verification | Detailed analysis with GCD steps |
| Standalone Python | MCP tools + AI integration |

---

## 🗂️ Files

### **Core Files:**

1. **`cot_pythagorean_finder.py`** - MCP tools (5 functions)
   - `show_reasoning(steps)` - Display reasoning steps
   - `check_triple(a, b, c)` - Verify if numbers form a triple
   - `find_triples(max_c)` - Find all triples up to max_c
   - `calculate_gcd(a, b)` - Calculate GCD with steps
   - `verify_and_classify(a, b, c)` - Complete analysis

2. **`cot_pythagorean_main.py`** - AI-powered main program
   - Uses Gemini to reason about Pythagorean problems
   - Executes MCP tools based on AI decisions

3. **`test_cot_pythagorean.py`** - Test suite
   - Tests all MCP tools without AI
   - Verifies functionality

### **Original Files (Still Available):**

- `pythagorean_finder.py` - Original implementation
- `test_pythagorean.py` - Original tests
- `demo_pythagorean.py` - Original demo

---

## 🚀 Quick Start

### **Prerequisites:**

1. ✅ Python 3.13
2. ✅ Dependencies installed (`uv sync`)
3. ✅ `.env` file with `GEMINI_API_KEY`

### **Run Tests (No AI Required):**

```bash
uv run python test_cot_pythagorean.py
```

**Expected Output:**
- ✅ TEST 1: Check Triple Function
- ✅ TEST 2: Find Triples Function
- ✅ TEST 3: Calculate GCD Function
- ✅ TEST 4: Verify and Classify Function

### **Run AI-Powered Analysis (Requires API Key):**

```bash
uv run python cot_pythagorean_main.py
```

**What It Does:**
- Analyzes example problems with AI reasoning
- Uses MCP tools to perform calculations
- Shows step-by-step thinking process

---

## 🔧 How It Works

### **Architecture:**

```
User Question
    ↓
Gemini AI (reasons about the problem)
    ↓
Generates FUNCTION_CALL commands
    ↓
MCP Tools (cot_pythagorean_finder.py)
    ↓
Execute calculations & analysis
    ↓
Return results to AI
    ↓
AI interprets & explains to user
```

### **Example Workflow:**

**User:** "Is (8, 15, 17) a Pythagorean triple?"

**AI Reasoning:**
1. "I need to check if 8² + 15² = 17²"
2. "I should also calculate GCD to determine if it's primitive"
3. "Let me verify and classify this triple"

**AI Action:** `FUNCTION_CALL: verify_and_classify|8|15|17`

**MCP Tool Executes:**
- ✓ Verifies: 8² + 15² = 17² → 64 + 225 = 289 ✓
- ✓ Calculates: GCD(8, 15) = 1
- ✓ Classifies: PRIMITIVE triple

**Result:** "(8, 15, 17) is a valid PRIMITIVE Pythagorean triple"

---

## 📚 MCP Tools Reference

### **1. show_reasoning(steps: list)**
Display step-by-step reasoning process

**Example:**
```python
show_reasoning([
    "1. Check if a² + b² = c²",
    "2. Calculate GCD(a, b)",
    "3. Classify as primitive or non-primitive"
])
```

---

### **2. check_triple(a: int, b: int, c: int)**
Verify if three numbers form a Pythagorean triple

**Example:**
```python
check_triple(3, 4, 5)
# Returns: {valid: True, triple: "(3,4,5)", primitive: True, ...}

check_triple(2, 3, 4)
# Returns: {valid: False, message: "NOT a Pythagorean Triple"}
```

---

### **3. find_triples(max_c: int)**
Find all Pythagorean triples where c ≤ max_c

**Example:**
```python
find_triples(15)
# Returns: {primitive: [(3,4,5), (5,12,13), ...], non_primitive: [(6,8,10), ...]}
```

---

### **4. calculate_gcd(a: int, b: int)**
Calculate GCD using Euclidean algorithm with steps

**Example:**
```python
calculate_gcd(6, 8)
# Shows steps:
# 6 = 8 × 0 + 6
# 8 = 6 × 1 + 2
# 6 = 2 × 3 + 0
# Result: GCD = 2
```

---

### **5. verify_and_classify(a: int, b: int, c: int)**
Complete analysis including validation, GCD, and classification

**Example:**
```python
verify_and_classify(8, 15, 17)
# Returns: {
#   valid: True,
#   triple: (8, 15, 17),
#   equation: "8^2 + 15^2 = 17^2",
#   gcd: 1,
#   classification: "PRIMITIVE"
# }
```

---

## 🎯 Use Cases

### **Original Pythagorean Finder (`pythagorean_finder.py`):**
- ✅ Educational tool for learning
- ✅ Quick manual verification
- ✅ Batch generation of triples
- ✅ No API key needed

### **COT Pythagorean Finder (`cot_pythagorean_finder.py`):**
- ✅ AI-powered explanations
- ✅ Natural language queries
- ✅ Step-by-step reasoning
- ✅ Detailed mathematical analysis
- ✅ Interactive problem solving

---

## 📊 Comparison: Original vs COT Version

| Feature | Original | COT Version |
|---------|----------|-------------|
| **Interface** | Menu-driven | Natural language |
| **Reasoning** | Direct calculation | Step-by-step AI reasoning |
| **Explanation** | Basic output | Detailed explanations |
| **GCD Calculation** | Result only | Shows algorithm steps |
| **Dependencies** | Standard library | MCP + Gemini API |
| **Use Case** | Quick verification | Learning & understanding |
| **API Required** | ❌ No | ✅ Yes (Gemini) |

---

## 🧪 Testing

### **Test MCP Tools (No AI):**
```bash
uv run python test_cot_pythagorean.py
```

### **Test Original Version:**
```bash
uv run python test_pythagorean.py
```

### **Run Original Demo:**
```bash
uv run python demo_pythagorean.py
```

### **Run Original Interactive Program:**
```bash
uv run python pythagorean_finder.py
```

---

## 🔑 Setup Requirements

### **1. Environment Variables:**

Create/update `.env` file:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your API key at: https://aistudio.google.com/app/apikey

### **2. Dependencies:**

All dependencies are in `pyproject.toml`:
- `python-dotenv` - Environment variables
- `google-genai` - Gemini AI
- `mcp` - Model Context Protocol
- `rich` - Beautiful terminal output

### **3. Sync Dependencies:**
```bash
uv sync
```

---

## 📖 Example Usage

### **Test the MCP Tools:**

```bash
$ uv run python test_cot_pythagorean.py

TEST 1: Check Triple Function
✓ (3, 4, 5) - Valid PRIMITIVE
✓ (6, 8, 10) - Valid NON-PRIMITIVE (GCD=2)
✓ (2, 3, 4) - INVALID

TEST 2: Find Triples
✓ Found 3 primitive triples (c ≤ 20)
✓ Found 2 non-primitive triples (c ≤ 20)

TEST 3: Calculate GCD
✓ GCD(3, 4) = 1 (PRIMITIVE)
✓ GCD(6, 8) = 2 (NON-PRIMITIVE)

TEST 4: Verify and Classify
✓ (8, 15, 17) - Complete analysis shown

ALL TESTS PASSED!
```

### **Run AI-Powered Analysis:**

```bash
$ uv run python cot_pythagorean_main.py

Problem: Verify and classify the triple (8, 15, 17)

AI Reasoning:
Step 1: Check if 8² + 15² = 17²
Step 2: Calculate GCD(8, 15)
Step 3: Classify as primitive or non-primitive

[Executing: verify_and_classify(8, 15, 17)]

Results:
✓ Valid Pythagorean Triple
✓ 8² + 15² = 17²
✓ 64 + 225 = 289
✓ GCD(8, 15) = 1
✓ Classification: PRIMITIVE

FINAL ANSWER: (8, 15, 17) is a valid PRIMITIVE Pythagorean triple
```

---

## 🎓 Educational Value

### **What You Learn:**

1. **Pythagorean Theorem:** Understanding a² + b² = c²
2. **Euclidean Algorithm:** GCD calculation steps
3. **Number Theory:** Primitive vs non-primitive triples
4. **AI Integration:** How AI can reason about mathematics
5. **MCP Protocol:** Tool-based AI interactions

---

## 🚧 Troubleshooting

### **Issue: "ModuleNotFoundError: No module named 'mcp'"**
```bash
uv sync  # Install all dependencies
```

### **Issue: "ValueError: Missing key inputs argument!"**
- ❌ Your `.env` file is missing or `GEMINI_API_KEY` is not set
- ✅ Create `.env` with your API key

### **Issue: "Failed to parse JSONRPC message"**
- ✅ This is already fixed in `cot_pythagorean_finder.py`
- ✅ Uses `stderr` for console output

### **Issue: "API key not valid"**
- ❌ Invalid or expired Gemini API key
- ✅ Get a new key from https://aistudio.google.com/app/apikey

---

## 📁 Project Structure

```
my_project_05/
├── cot_pythagorean_finder.py     ← NEW: MCP tools
├── cot_pythagorean_main.py       ← NEW: AI-powered main
├── test_cot_pythagorean.py       ← NEW: Test suite
├── COT_PYTHAGOREAN_README.md     ← NEW: This file
│
├── pythagorean_finder.py         ← Original implementation
├── test_pythagorean.py           ← Original tests
├── demo_pythagorean.py           ← Original demo
│
├── cot_main.py                   ← Original COT calculator
├── cot_tools.py                  ← Original COT tools
├── cot_tools_consistency.py      ← COT with consistency check
│
├── .env                          ← API keys (gitignored)
├── pyproject.toml                ← Dependencies
└── README.md                     ← Main project README
```

---

## ✅ Status

```
✓ COT Pythagorean Finder implemented
✓ All MCP tools working
✓ Tests passing
✓ Integrates with original pythagorean_finder.py logic
✓ Uses cot_tools_consistency.py approach
✓ Documentation complete
```

---

## 🔗 Related Files

- **Original Spec:** `The Pythagorean Triple Finder.md`
- **Implementation Guide:** `PYTHAGOREAN_IMPLEMENTATION_GUIDE.md`
- **Prompts Used:** `PROMPTS_USED.md`
- **Project Summary:** `IMPLEMENTATION_SUMMARY.md`

---

## 🎉 Summary

This COT Pythagorean Finder successfully combines:
- ✅ **Functionality** from `pythagorean_finder.py`
- ✅ **AI reasoning** from `cot_tools_consistency.py`
- ✅ **MCP protocol** for tool integration
- ✅ **Step-by-step explanations** for learning

**Result:** An AI-powered mathematical reasoning system for Pythagorean triples! 🚀

---

**Created:** October 9, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅

