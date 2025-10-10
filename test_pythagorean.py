"""
Test cases for Pythagorean Triple Finder
Run this to verify your implementation meets all requirements
"""

from pythagorean_finder import gcd, is_pythagorean_triple, is_primitive, generate_triples


def test_gcd():
    """Test GCD function"""
    print("\n" + "="*60)
    print("TEST 1: GCD Function")
    print("="*60)
    
    test_cases = [
        (6, 8, 2),
        (5, 12, 1),
        (21, 14, 7),
        (17, 19, 1)
    ]
    
    for a, b, expected in test_cases:
        result = gcd(a, b)
        status = "[PASS]" if result == expected else "[FAIL]"
        print(f"{status}: GCD({a}, {b}) = {result} (expected {expected})")


def test_is_pythagorean_triple():
    """Test triple verification"""
    print("\n" + "="*60)
    print("TEST 2: Pythagorean Triple Verification")
    print("="*60)
    
    test_cases = [
        ((3, 4, 5), True),
        ((5, 12, 13), True),
        ((8, 15, 17), True),
        ((2, 3, 4), False),
        ((6, 8, 10), True),
    ]
    
    for (x, y, z), expected in test_cases:
        result = is_pythagorean_triple(x, y, z)
        status = "[PASS]" if result == expected else "[FAIL]"
        print(f"{status}: ({x}, {y}, {z}) is {'valid' if result else 'invalid'} (expected {'valid' if expected else 'invalid'})")


def test_is_primitive():
    """Test primitive classification"""
    print("\n" + "="*60)
    print("TEST 3: Primitive Classification")
    print("="*60)
    
    test_cases = [
        ((3, 4), True),   # GCD = 1 → Primitive
        ((5, 12), True),  # GCD = 1 → Primitive
        ((6, 8), False),  # GCD = 2 → Non-Primitive
        ((9, 12), False), # GCD = 3 → Non-Primitive
    ]
    
    for (a, b), expected in test_cases:
        result = is_primitive(a, b)
        status = "[PASS]" if result == expected else "[FAIL]"
        classification = "Primitive" if result else "Non-Primitive"
        expected_class = "Primitive" if expected else "Non-Primitive"
        print(f"{status}: ({a}, {b}) is {classification} (expected {expected_class})")


def test_generate_triples():
    """Test triple generation"""
    print("\n" + "="*60)
    print("TEST 4: Generate Triples (c_max = 25)")
    print("="*60)
    
    primitive, non_primitive = generate_triples(25)
    
    # Required triples that must be found
    required_primitive = [(3, 4, 5), (5, 12, 13), (8, 15, 17)]
    required_non_primitive = [(6, 8, 10)]
    
    print(f"\nFound {len(primitive)} primitive triples")
    print(f"Found {len(non_primitive)} non-primitive triples")
    
    print("\nChecking required primitive triples:")
    for triple in required_primitive:
        found = triple in primitive
        status = "[PASS]" if found else "[FAIL]"
        print(f"{status}: {triple} {'found' if found else 'NOT FOUND'}")
    
    print("\nChecking required non-primitive triples:")
    for triple in required_non_primitive:
        found = triple in non_primitive
        status = "[PASS]" if found else "[FAIL]"
        print(f"{status}: {triple} {'found' if found else 'NOT FOUND'}")


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("  PYTHAGOREAN TRIPLE FINDER - TEST SUITE  ")
    print("="*60)
    
    try:
        test_gcd()
        test_is_pythagorean_triple()
        test_is_primitive()
        test_generate_triples()
        
        print("\n" + "="*60)
        print("  ALL TESTS COMPLETED  ")
        print("="*60)
        print("\n[OK] If all tests show PASS, your implementation is correct!")
        print("[!!] If any tests show FAIL, review the corresponding function.\n")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("Some functions may not be implemented yet.\n")


if __name__ == "__main__":
    run_all_tests()
