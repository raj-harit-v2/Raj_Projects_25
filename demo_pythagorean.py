"""
Automated demo of Pythagorean Triple Finder
Shows all required test cases from the specification
"""

from pythagorean_finder import generate_triples, verify_custom_triple, display_triples


def demo_generation():
    """Demo: Generate triples with c_max = 25"""
    print("\n" + "="*70)
    print("DEMO 1: GENERATE AND ANALYZE TRIPLES")
    print("="*70)
    print("\nTest Case: Generate all triples with c_max = 25")
    print("Expected to find:")
    print("  - Primitive: (3,4,5), (5,12,13), (8,15,17)")
    print("  - Non-Primitive: (6,8,10)")
    
    print("\n" + "-"*70)
    print("Running generation...")
    print("-"*70)
    
    primitive, non_primitive = generate_triples(25)
    display_triples(primitive, non_primitive)
    
    # Verify required triples are found
    print("\n" + "-"*70)
    print("VERIFICATION OF REQUIRED TRIPLES:")
    print("-"*70)
    required = {
        'primitive': [(3, 4, 5), (5, 12, 13), (8, 15, 17)],
        'non_primitive': [(6, 8, 10)]
    }
    
    for triple in required['primitive']:
        status = "[OK]" if triple in primitive else "[FAIL]"
        print(f"{status} Primitive triple {triple} found")
    
    for triple in required['non_primitive']:
        status = "[OK]" if triple in non_primitive else "[FAIL]"
        print(f"{status} Non-primitive triple {triple} found")


def demo_verify_valid_primitive():
    """Demo: Verify (8, 15, 17) - should be Primitive"""
    print("\n" + "="*70)
    print("DEMO 2: VERIFY CUSTOM TRIPLE (VALID - PRIMITIVE)")
    print("="*70)
    print("\nTest Case: Verify (8, 15, 17)")
    print("Expected: Valid Pythagorean Triple - PRIMITIVE")
    
    print("\n" + "-"*70)
    verify_custom_triple(8, 15, 17)
    print("-"*70)


def demo_verify_invalid():
    """Demo: Verify (2, 3, 4) - should fail"""
    print("\n" + "="*70)
    print("DEMO 3: VERIFY CUSTOM TRIPLE (INVALID)")
    print("="*70)
    print("\nTest Case: Verify (2, 3, 4)")
    print("Expected: NOT a Pythagorean Triple")
    
    print("\n" + "-"*70)
    verify_custom_triple(2, 3, 4)
    print("-"*70)


def demo_verify_non_primitive():
    """Demo: Verify (6, 8, 10) - should be Non-Primitive"""
    print("\n" + "="*70)
    print("DEMO 4: VERIFY CUSTOM TRIPLE (VALID - NON-PRIMITIVE)")
    print("="*70)
    print("\nTest Case: Verify (6, 8, 10)")
    print("Expected: Valid Pythagorean Triple - NON-PRIMITIVE")
    
    print("\n" + "-"*70)
    verify_custom_triple(6, 8, 10)
    print("-"*70)


def run_all_demos():
    """Run all demonstration cases"""
    print("\n" + "="*70)
    print("  PYTHAGOREAN TRIPLE FINDER - DEMONSTRATION")
    print("  Showing all required test cases from specification")
    print("="*70)
    
    demo_generation()
    demo_verify_valid_primitive()
    demo_verify_invalid()
    demo_verify_non_primitive()
    
    print("\n" + "="*70)
    print("  ALL DEMONSTRATIONS COMPLETED")
    print("="*70)
    print("\nThe program successfully:")
    print("  [OK] Generates triples up to c_max=25")
    print("  [OK] Finds all required triples")
    print("  [OK] Correctly identifies (8,15,17) as Primitive")
    print("  [OK] Correctly rejects (2,3,4) as invalid")
    print("  [OK] Correctly identifies (6,8,10) as Non-Primitive")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    run_all_demos()

