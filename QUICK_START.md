# Quick Start Guide - Which Program to Run?

## 🎯 TL;DR - Just Want to Use It?

### **INTERACTIVE Programs (Choose from menu, enter your data):**

```bash
# Original simple version:
uv run python pythagorean_finder.py

# NEW: COT version with detailed reasoning:
uv run python interactive_cot_pythagorean.py
```

---

## 📚 All Programs Explained

### **1. Interactive Programs** ✅ USER-FRIENDLY

#### `pythagorean_finder.py` - Original Version
```bash
uv run python pythagorean_finder.py
```
- ✅ Menu-driven interface
- ✅ Generate triples
- ✅ Verify custom triples
- ✅ Shows GCD results
- ⚡ Fast, simple output

#### `interactive_cot_pythagorean.py` - NEW COT Version
```bash
uv run python interactive_cot_pythagorean.py
```
- ✅ Menu-driven interface
- ✅ Generate triples with formatted tables
- ✅ Verify custom triples with detailed analysis
- ✅ Shows GCD calculation steps
- ✅ Step-by-step reasoning display
- 🎨 Beautiful colored output

---

### **2. Test Programs** ✅ RUN TO VERIFY

#### `test_pythagorean.py` - Test Original Version
```bash
uv run python test_pythagorean.py
```
- Runs automated tests
- Shows PASS/FAIL results
- Tests: GCD, verification, generation

#### `test_cot_pythagorean.py` - Test COT Version
```bash
uv run python test_cot_pythagorean.py
```
- Tests MCP tools
- Shows detailed output
- Tests: check_triple, find_triples, calculate_gcd, verify_and_classify

---

### **3. Demo Programs** ✅ RUN TO SEE EXAMPLES

#### `demo_pythagorean.py` - Original Demo
```bash
uv run python demo_pythagorean.py
```
- Runs predefined examples
- Shows all features
- No user input needed

---

### **4. Backend Services** ❌ DON'T RUN DIRECTLY

#### `cot_pythagorean_finder.py` - MCP Server
```bash
# DON'T RUN THIS DIRECTLY - it's a backend service
# Used by: interactive_cot_pythagorean.py and test_cot_pythagorean.py
```
- Provides MCP tools
- Runs in background
- No user interface

#### `cot_tools.py` - COT Calculator MCP Server
```bash
# DON'T RUN THIS DIRECTLY
# Used by: cot_main.py
```
- Backend for COT calculator
- No user interface

#### `cot_tools_consistency.py` - COT with Consistency
```bash
# DON'T RUN THIS DIRECTLY
```
- Backend service
- No user interface

---

### **5. AI-Powered Programs** ⚠️ NOT INTERACTIVE (Requires API Key)

#### `cot_pythagorean_main.py` - AI Analysis
```bash
uv run python cot_pythagorean_main.py
```
- ⚠️ NOT interactive
- Runs predefined problems
- Requires GEMINI_API_KEY
- Has rate limits (10 requests/min free tier)

#### `cot_main.py` - COT Calculator with AI
```bash
uv run python cot_main.py
```
- ⚠️ NOT interactive
- Calculates predefined math problems
- Requires GEMINI_API_KEY

---

## 🆚 Comparison: Which Should I Use?

| If you want... | Use This | Command |
|----------------|----------|---------|
| Simple interactive finder | `pythagorean_finder.py` | `uv run python pythagorean_finder.py` |
| **Detailed step-by-step analysis** | **`interactive_cot_pythagorean.py`** | `uv run python interactive_cot_pythagorean.py` |
| Test everything works | `test_pythagorean.py` | `uv run python test_pythagorean.py` |
| Test COT tools | `test_cot_pythagorean.py` | `uv run python test_cot_pythagorean.py` |
| See examples | `demo_pythagorean.py` | `uv run python demo_pythagorean.py` |
| AI explanations | `cot_pythagorean_main.py` | Needs API key, not interactive |

---

## ⚡ Recommended: Start Here

### **First Time User:**
```bash
# Run the test to verify everything works:
uv run python test_pythagorean.py

# Then try the interactive version:
uv run python interactive_cot_pythagorean.py
```

### **Want to See It in Action:**
```bash
# See automated demo:
uv run python demo_pythagorean.py

# Or test COT features:
uv run python test_cot_pythagorean.py
```

---

## 🎓 Learning Path

1. **Start:** `uv run python test_pythagorean.py` - Verify it works
2. **Basic:** `uv run python pythagorean_finder.py` - Try simple version
3. **Advanced:** `uv run python interactive_cot_pythagorean.py` - See detailed reasoning
4. **Demo:** `uv run python demo_pythagorean.py` - See all features

---

## 🔧 Why Some Programs Don't Show Output

### Files ending in `_finder.py` or `_tools.py`:
- These are **MCP servers** (backend services)
- They start and wait for MCP protocol messages
- No user interface shown
- Used by other programs

### How they work together:
```
interactive_cot_pythagorean.py  (Frontend - what you run)
        ↓ calls
cot_pythagorean_finder.py      (Backend - MCP server)
        ↓ provides
Tools: check_triple, find_triples, etc.
```

---

## ✅ Summary

**For Interactive Use:**
- ✅ `pythagorean_finder.py` - Simple
- ✅ `interactive_cot_pythagorean.py` - Detailed (RECOMMENDED)

**For Testing:**
- ✅ `test_pythagorean.py`
- ✅ `test_cot_pythagorean.py`

**DON'T Run Directly:**
- ❌ `cot_pythagorean_finder.py` (backend)
- ❌ `cot_tools.py` (backend)
- ❌ `cot_tools_consistency.py` (backend)

---

**Last Updated:** October 9, 2025  
**Status:** Ready to use! 🚀

