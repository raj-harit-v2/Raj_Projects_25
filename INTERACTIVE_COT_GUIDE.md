# Interactive COT Pythagorean Finder - User Guide

## 🔄 Program Comparison

### **❌ `cot_pythagorean_main.py` (NOT Interactive)**
- Runs predefined problems automatically
- Requires AI (Gemini API)
- No user input during execution
- Limited by API rate limits (10 requests/min free tier)
- **When you ran it:** It processed 3 problems automatically then stopped

### **✅ `interactive_cot_pythagorean.py` (Interactive)**
- **Menu-driven interface** - YOU choose what to do
- **No AI required** - uses MCP tools directly
- **No API limits** - works offline
- Shows step-by-step reasoning and calculations
- Similar to original `pythagorean_finder.py` but with COT features

---

## 🚀 How to Run the Interactive Version

```bash
uv run python interactive_cot_pythagorean.py
```

---

## 📋 Interactive Menu

When you run it, you'll see:

```
====================================================================
╭──────────────────────────────────────────────────────────────╮
│ Interactive COT Pythagorean Triple Finder                     │
│ With Step-by-Step Reasoning                                   │
╰──────────────────────────────────────────────────────────────╯
====================================================================

--------------------------------------------------------------------
MENU OPTIONS:
--------------------------------------------------------------------
  [1] Check if numbers form a Pythagorean triple
  [2] Find all triples up to max value
  [3] Calculate GCD (with steps)
  [4] Verify and Classify a triple (complete analysis)
  [5] Exit
--------------------------------------------------------------------

Enter your choice (1-5):
```

---

## 🎯 Example Usage

### **Option 1: Check Triple**

```
Enter your choice (1-5): 1

Enter three integers:
  First number (a):  3
  Second number (b): 4
  Third number (c):  5

Checking if (3, 4, 5) is a Pythagorean triple...

[Displays verification with equation and result]

Result: Valid Pythagorean Triple - PRIMITIVE
```

---

### **Option 2: Find All Triples**

```
Enter your choice (1-5): 2

Enter maximum hypotenuse value (c_max): 20

Finding all Pythagorean triples with c <= 20...

[Displays table with all triples found]

Search complete!
```

---

### **Option 3: Calculate GCD**

```
Enter your choice (1-5): 3

Enter two positive integers:
  First number:  6
  Second number: 8

Calculating GCD(6, 8) using Euclidean algorithm...

[Shows step-by-step Euclidean algorithm]

Steps:
  6 = 8 × 0 + 6
  8 = 6 × 1 + 2
  6 = 2 × 3 + 0

Result: GCD(6, 8) = 2
Interpretation: NON-PRIMITIVE triple

Calculation complete!
```

---

### **Option 4: Complete Analysis**

```
Enter your choice (1-5): 4

Enter three integers to verify:
  First number (a):  8
  Second number (b): 15
  Third number (c):  17

Performing complete analysis of (8, 15, 17)...

[Displays detailed table with:]
  - Triple verification
  - Equation check
  - GCD calculation
  - Primitive classification

Analysis complete!
```

---

### **Option 5: Exit**

```
Enter your choice (1-5): 5

Thank you for using COT Pythagorean Finder!
```

---

## 🆚 Comparison with Original

| Feature | `pythagorean_finder.py` | `interactive_cot_pythagorean.py` |
|---------|------------------------|----------------------------------|
| **Interface** | Menu-driven | Menu-driven |
| **GCD Display** | Result only | Shows algorithm steps |
| **Triple Check** | Basic validation | Detailed analysis with equation |
| **Find Triples** | Simple list | Formatted table with colors |
| **Classification** | Text output | Rich formatted panels |
| **Reasoning** | Direct | Step-by-step COT approach |

---

## 🔧 Technical Details

### **How It Works:**

1. **Starts MCP Server:** Launches `cot_pythagorean_finder.py` as a subprocess
2. **User Input:** Gets your menu choice and parameters
3. **Calls MCP Tool:** Executes the appropriate tool (check_triple, find_triples, etc.)
4. **Displays Results:** Shows formatted output with reasoning steps
5. **Loops:** Returns to menu for next action

### **No AI Required:**

- ✅ Works offline
- ✅ No API key needed
- ✅ No rate limits
- ✅ Instant responses
- ✅ Deterministic results

### **MCP Tools Used:**

All 5 tools from `cot_pythagorean_finder.py`:
1. `check_triple(a, b, c)`
2. `find_triples(max_c)`
3. `calculate_gcd(a, b)`
4. `verify_and_classify(a, b, c)`
5. `show_reasoning(steps)` (used internally)

---

## 📊 When to Use Each Program

### **Use `pythagorean_finder.py`:**
- ✅ Simple, straightforward verification
- ✅ No dependencies beyond standard library
- ✅ Educational/teaching purposes
- ✅ Quick batch generation

### **Use `interactive_cot_pythagorean.py`:**
- ✅ Want to see algorithm steps (GCD, etc.)
- ✅ Learning how Pythagorean verification works
- ✅ Beautiful formatted output with colors
- ✅ Step-by-step reasoning display

### **Use `cot_pythagorean_main.py` (AI-powered):**
- ✅ Want AI to explain reasoning
- ✅ Natural language questions
- ✅ Complex problem-solving with explanations
- ⚠️ Requires API key and has rate limits

### **Use `test_cot_pythagorean.py`:**
- ✅ Testing MCP tools
- ✅ Verifying functionality
- ✅ Running automated checks

---

## 🎓 Example Interactive Session

```bash
$ uv run python interactive_cot_pythagorean.py

====================================================================
Interactive COT Pythagorean Triple Finder
====================================================================

Enter your choice (1-5): 4

Enter three integers to verify:
  First number (a):  8
  Second number (b): 15
  Third number (c):  17

Performing complete analysis of (8, 15, 17)...

╭────────────────────────────────────────────────────────────────╮
│                 Pythagorean Triple Analysis                     │
├────────────────────────────────────────────────────────────────┤
│ Property       │ Value                                          │
├────────────────────────────────────────────────────────────────┤
│ Triple         │ (8, 15, 17)                                    │
│ Equation       │ 8² + 15² = 17²                                 │
│ Verification   │ 64 + 225 = 289                                 │
│ Valid          │ YES                                            │
│ GCD(a, b)      │ 1                                              │
│ Classification │ PRIMITIVE                                      │
╰────────────────────────────────────────────────────────────────╯

Analysis complete!

Enter your choice (1-5): 5

Thank you for using COT Pythagorean Finder!
```

---

## 💡 Tips

1. **Exit anytime:** Press Ctrl+C or choose option 5
2. **Invalid input:** Program will ask you to try again
3. **See MCP output:** The detailed tables/panels appear in the terminal
4. **Try all options:** Each shows different aspects of analysis

---

## 🐛 Troubleshooting

### **Issue: Nothing displays when running `cot_pythagorean_main.py`**
- ✅ **Solution:** That program is NOT interactive, use `interactive_cot_pythagorean.py` instead

### **Issue: "API rate limit exceeded"**
- ❌ Don't use `cot_pythagorean_main.py` - it needs AI
- ✅ Use `interactive_cot_pythagorean.py` - no API needed

### **Issue: "Module not found"**
```bash
uv sync  # Install dependencies
```

---

## ✅ Summary

**For Interactive Use:**
```bash
# Use THIS for interactive menu:
uv run python interactive_cot_pythagorean.py
```

**For Testing:**
```bash
# Use THIS to test MCP tools:
uv run python test_cot_pythagorean.py
```

**For AI-Powered Analysis:**
```bash
# Use THIS only if you want AI reasoning (requires API key):
uv run python cot_pythagorean_main.py
```

---

**Created:** October 9, 2025  
**Purpose:** Explain the difference between programs and how to use the interactive version  
**Status:** Ready to use! ✅

