"""
Pythagorean Triple Finder and Analyzer
Generates, analyzes, and verifies Pythagorean Triples
"""

import math
from typing import List, Tuple


def gcd(a: int, b: int) -> int:
    """
    Calculate Greatest Common Divisor using Euclidean algorithm
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        GCD of a and b
    """
    while b:
        a, b = b, a % b
    return a


def is_pythagorean_triple(x: int, y: int, z: int) -> bool:
    """
    Check if three numbers form a Pythagorean Triple
    
    Args:
        x, y, z: Three positive integers
    
    Returns:
        True if they form a Pythagorean Triple, False otherwise
    """
    # Sort to find largest value (hypotenuse candidate)
    sides = sorted([x, y, z])
    a, b, c = sides[0], sides[1], sides[2]
    return a*a + b*b == c*c


def is_primitive(a: int, b: int) -> bool:
    """
    Check if a triple is primitive (GCD = 1)
    
    Args:
        a, b: Two sides of the triple
    
    Returns:
        True if primitive, False otherwise
    """
    return gcd(a, b) == 1


def generate_triples(max_c: int) -> Tuple[List[Tuple[int, int, int]], List[Tuple[int, int, int]]]:
    """
    Generate all Pythagorean triples up to max_c
    
    Args:
        max_c: Maximum value for hypotenuse
    
    Returns:
        Tuple of (primitive_triples, non_primitive_triples)
    """
    primitive = []
    non_primitive = []
    
    # Use nested loops to find all triples where a² + b² = c²
    for a in range(1, max_c):
        for b in range(a, max_c):  # Start from a to avoid duplicates
            c_squared = a*a + b*b
            c = int(math.sqrt(c_squared))
            
            # Check if c is exact integer and within limit
            if c*c == c_squared and c <= max_c:
                triple = (a, b, c)
                
                # Check if it's primitive using GCD
                if is_primitive(a, b):
                    primitive.append(triple)
                else:
                    non_primitive.append(triple)
    
    return primitive, non_primitive


def display_triples(primitive: List[Tuple[int, int, int]], non_primitive: List[Tuple[int, int, int]]):
    """
    Display the found triples in a formatted way
    
    Args:
        primitive: List of primitive triples
        non_primitive: List of non-primitive triples
    """
    print("\n" + "="*60)
    print("PYTHAGOREAN TRIPLES FOUND")
    print("="*60)
    
    print("\n[PRIMITIVE] PRIMITIVE TRIPLES (GCD = 1):")
    print("-" * 60)
    for triple in primitive:
        a, b, c = triple
        print(f"  ({a:3d}, {b:3d}, {c:3d})  -->  {a}^2 + {b}^2 = {c}^2  -->  {a**2} + {b**2} = {c**2}")
    
    print(f"\nTotal Primitive: {len(primitive)}")
    
    print("\n[NON-PRIMITIVE] NON-PRIMITIVE TRIPLES (GCD > 1):")
    print("-" * 60)
    for triple in non_primitive:
        a, b, c = triple
        g = gcd(a, b)
        print(f"  ({a:3d}, {b:3d}, {c:3d})  -->  GCD({a}, {b}) = {g}")
    
    print(f"\nTotal Non-Primitive: {len(non_primitive)}")
    print("="*60)


def verify_custom_triple(x: int, y: int, z: int):
    """
    Verify and analyze a custom triple
    
    Args:
        x, y, z: Three integers provided by user
    """
    print("\n" + "="*60)
    print(f"ANALYZING TRIPLE: ({x}, {y}, {z})")
    print("="*60)
    
    # Check if it's a valid Pythagorean Triple
    if not is_pythagorean_triple(x, y, z):
        print("\n[X] NOT a Pythagorean Triple")
        print(f"   {x}^2 + {y}^2 != {z}^2 (or any valid permutation)")
        return
    
    print("\n[OK] Valid Pythagorean Triple!")
    
    # Sort to get a, b, c format
    sides = sorted([x, y, z])
    a, b, c = sides[0], sides[1], sides[2]
    print(f"   {a}^2 + {b}^2 = {c}^2")
    print(f"   {a*a} + {b*b} = {c*c}")
    
    # Check if it's primitive
    if is_primitive(a, b):
        print(f"\n[PRIMITIVE] Classification: PRIMITIVE")
        print(f"   GCD({a}, {b}) = 1")
    else:
        g = gcd(a, b)
        print(f"\n[NON-PRIMITIVE] Classification: NON-PRIMITIVE")
        print(f"   GCD({a}, {b}) = {g}")
    
    print("="*60)


def main():
    """Main program with menu system"""
    print("\n" + "="*60)
    print("  PYTHAGOREAN TRIPLE FINDER AND ANALYZER  📐")
    print("="*60)
    
    while True:
        print("\n" + "-"*60)
        print("MENU OPTIONS:")
        print("-"*60)
        print("  [1] Generate and Analyze Triples")
        print("  [2] Verify and Analyze a Custom Triple")
        print("  [3] Exit")
        print("-"*60)
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Generate and Analyze Triples
            try:
                max_c = int(input("\nEnter maximum hypotenuse value (c_max): "))
                if max_c < 3:
                    print("[ERROR] Please enter a value >= 3")
                    continue
                
                print(f"\n[SEARCHING] Finding Pythagorean Triples with c <= {max_c}...")
                primitive, non_primitive = generate_triples(max_c)
                display_triples(primitive, non_primitive)
                
            except ValueError:
                print("[ERROR] Please enter a valid integer")
            
        elif choice == "2":
            # Verify and Analyze a Custom Triple
            try:
                print("\nEnter three positive integers:")
                x = int(input("  First number:  "))
                y = int(input("  Second number: "))
                z = int(input("  Third number:  "))
                
                if x <= 0 or y <= 0 or z <= 0:
                    print("[ERROR] All numbers must be positive")
                    continue
                
                verify_custom_triple(x, y, z)
                
            except ValueError:
                print("[ERROR] Please enter valid integers")
            
        elif choice == "3":
            print("\n[EXIT] Thank you for using Pythagorean Triple Finder!")
            break
            
        else:
            print("\n[ERROR] Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()

