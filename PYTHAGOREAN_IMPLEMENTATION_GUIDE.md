# Pythagorean Triple Finder - Implementation Guide 📐

## Project Overview

This guide shows you how to implement and test the Pythagorean Triple Finder based on the requirements in `The Pythagorean Triple Finder.md`.

## File Structure

```
my_project_05/
├── pythagorean_finder.py      ← MAIN IMPLEMENTATION (TODO items)
├── test_pythagorean.py        ← TEST SUITE (ready to run)
├── The Pythagorean Triple Finder.md  ← PROJECT REQUIREMENTS
├── PYTHAGOREAN_IMPLEMENTATION_GUIDE.md  ← THIS FILE
├── cot_main.py                ← Separate project (calculator)
├── cot_tools.py               ← Separate project (calculator tools)
├── .env                       ← API keys (secure)
└── pyproject.toml             ← Dependencies
```

---

## Implementation Steps

### Step 1: Implement Helper Functions (30 mins)

**Location:** `pythagorean_finder.py`

#### 1.1 Implement `gcd(a, b)` function
```python
def gcd(a: int, b: int) -> int:
    """Euclidean algorithm for GCD"""
    while b:
        a, b = b, a % b
    return a
```

**Test:** Run `uv run python test_pythagorean.py` - TEST 1 should pass

---

#### 1.2 Implement `is_pythagorean_triple(x, y, z)` function
```python
def is_pythagorean_triple(x: int, y: int, z: int) -> bool:
    """Check if x² + y² = z² (or any permutation)"""
    # Sort to find largest value (hypotenuse candidate)
    sides = sorted([x, y, z])
    a, b, c = sides[0], sides[1], sides[2]
    return a*a + b*b == c*c
```

**Test:** Run tests - TEST 2 should pass

---

#### 1.3 Implement `is_primitive(a, b)` function
```python
def is_primitive(a: int, b: int) -> bool:
    """Check if GCD(a, b) = 1"""
    return gcd(a, b) == 1
```

**Test:** Run tests - TEST 3 should pass

---

### Step 2: Implement Core Features (45 mins)

#### 2.1 Implement `generate_triples(max_c)` function

**Algorithm:**
1. Use nested loops: `for a in range(1, max_c)` and `for b in range(a, max_c)`
2. Calculate `c = sqrt(a² + b²)`
3. If c is an integer and c ≤ max_c, it's a triple
4. Check if primitive using `is_primitive(a, b)`
5. Add to appropriate list

**Pseudo-code:**
```python
def generate_triples(max_c: int):
    primitive = []
    non_primitive = []
    
    for a in range(1, max_c):
        for b in range(a, max_c):
            c_squared = a*a + b*b
            c = int(math.sqrt(c_squared))
            
            # Check if c is exact integer and within limit
            if c*c == c_squared and c <= max_c:
                triple = (a, b, c)
                
                if is_primitive(a, b):
                    primitive.append(triple)
                else:
                    non_primitive.append(triple)
    
    return primitive, non_primitive
```

**Test:** Run tests - TEST 4 should pass

---

#### 2.2 Implement `verify_custom_triple(x, y, z)` function

**Logic:**
1. Check if it's a valid triple using `is_pythagorean_triple()`
2. If NO: Print "Not a Pythagorean Triple"
3. If YES: 
   - Sort the values
   - Check if primitive using `is_primitive()`
   - Display results

**Example:**
```python
def verify_custom_triple(x: int, y: int, z: int):
    print(f"\nANALYZING TRIPLE: ({x}, {y}, {z})")
    print("="*60)
    
    if not is_pythagorean_triple(x, y, z):
        print("❌ NOT a Pythagorean Triple")
        return
    
    print("✓ Valid Pythagorean Triple!")
    
    # Sort to get a, b, c format
    sides = sorted([x, y, z])
    a, b = sides[0], sides[1]
    
    if is_primitive(a, b):
        print(f"📐 Classification: PRIMITIVE (GCD = 1)")
    else:
        g = gcd(a, b)
        print(f"📊 Classification: NON-PRIMITIVE (GCD = {g})")
```

---

### Step 3: Implement Menu System (15 mins)

#### 3.1 Complete `main()` function

Fill in the TODO sections:

```python
def main():
    # ... menu display code already there ...
    
    if choice == "1":
        try:
            max_c = int(input("\nEnter maximum hypotenuse value: "))
            if max_c < 3:
                print("❌ Please enter a value ≥ 3")
                continue
            
            print(f"\n🔍 Searching for triples with c ≤ {max_c}...")
            primitive, non_primitive = generate_triples(max_c)
            display_triples(primitive, non_primitive)
            
        except ValueError:
            print("❌ Please enter a valid integer")
    
    elif choice == "2":
        try:
            print("\nEnter three positive integers:")
            x = int(input("  First number:  "))
            y = int(input("  Second number: "))
            z = int(input("  Third number:  "))
            
            if x <= 0 or y <= 0 or z <= 0:
                print("❌ All numbers must be positive")
                continue
            
            verify_custom_triple(x, y, z)
            
        except ValueError:
            print("❌ Please enter valid integers")
```

---

## Testing Your Implementation

### Step 1: Run Unit Tests
```bash
uv run python test_pythagorean.py
```

**Expected Output:**
- ✓ All GCD tests pass
- ✓ All triple verification tests pass
- ✓ All primitive classification tests pass
- ✓ Generation finds (3,4,5), (5,12,13), (6,8,10)

---

### Step 2: Run Manual Tests

```bash
uv run python pythagorean_finder.py
```

#### Test Case 1: Generate Triples (c_max = 25)
```
Menu > 1
Enter maximum hypotenuse value: 25

Expected to find:
- Primitive: (3,4,5), (5,12,13), (8,15,17), etc.
- Non-Primitive: (6,8,10), (9,12,15), etc.
```

#### Test Case 2: Verify (8, 15, 17) - Should be Primitive
```
Menu > 2
First number: 8
Second number: 15
Third number: 17

Expected: "Valid Pythagorean Triple - PRIMITIVE"
```

#### Test Case 3: Verify (2, 3, 4) - Should FAIL
```
Menu > 2
First number: 2
Second number: 3
Third number: 4

Expected: "NOT a Pythagorean Triple"
```

---

## Prompt to Use for AI Code Generation

If you want an AI assistant to implement this, use this prompt:

```
I have a file called pythagorean_finder.py with TODO sections.
Please implement all the TODO items following these requirements:

1. gcd(a, b): Use Euclidean algorithm (while b: a, b = b, a % b)

2. is_pythagorean_triple(x, y, z): 
   - Sort the three numbers
   - Check if a² + b² = c² where c is the largest

3. is_primitive(a, b):
   - Return True if gcd(a, b) == 1

4. generate_triples(max_c):
   - Use nested loops for a and b
   - Calculate c = sqrt(a² + b²)
   - Check if c is integer and c ≤ max_c
   - Classify as primitive or non-primitive
   - Return both lists

5. verify_custom_triple(x, y, z):
   - Check if valid triple
   - If no: print error
   - If yes: check if primitive and display result

6. main() - menu system:
   - Option 1: Get max_c, generate triples, display results
   - Option 2: Get x, y, z, verify and analyze
   - Validate all inputs (positive integers, sensible ranges)

The code must pass all tests in test_pythagorean.py
```

---

## Success Criteria ✓

Your implementation is complete when:

- [x] File `pythagorean_finder.py` created with template
- [x] File `test_pythagorean.py` created with tests
- [ ] All TODO items in `pythagorean_finder.py` implemented
- [ ] Running `test_pythagorean.py` shows all tests PASS
- [ ] Manual test 1: c_max=25 finds required triples
- [ ] Manual test 2: (8,15,17) → "Primitive"
- [ ] Manual test 3: (2,3,4) → "Not a triple"
- [ ] Input validation works (handles errors gracefully)
- [ ] Output is formatted and readable

---

## Next Steps

1. **Implement:** Fill in all TODO sections in `pythagorean_finder.py`
2. **Test:** Run `uv run python test_pythagorean.py`
3. **Debug:** Fix any failing tests
4. **Manual Test:** Run the program and test with real inputs
5. **Enhance:** Add more features (export to file, visualization, etc.)

Good luck! 🚀

