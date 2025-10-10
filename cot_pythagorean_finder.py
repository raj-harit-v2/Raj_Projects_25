"""
Chain of Thought Pythagorean Triple Finder
Combines AI-powered reasoning with Pythagorean triple analysis
Uses MCP tools similar to cot_tools_consistency.py
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import math
import sys

# Use stderr for console output to avoid interfering with MCP JSON-RPC on stdout
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console(file=sys.stderr)
mcp = FastMCP("PythagoreanCoT")


def gcd(a: int, b: int) -> int:
    """Calculate Greatest Common Divisor using Euclidean algorithm"""
    while b:
        a, b = b, a % b
    return a


def is_pythagorean_triple(x: int, y: int, z: int) -> bool:
    """Check if three numbers form a Pythagorean Triple"""
    sides = sorted([x, y, z])
    a, b, c = sides[0], sides[1], sides[2]
    return a*a + b*b == c*c


def is_primitive(a: int, b: int) -> bool:
    """Check if a triple is primitive (GCD = 1)"""
    return gcd(a, b) == 1


@mcp.tool()
def show_reasoning(steps: list) -> TextContent:
    """Show the step-by-step reasoning process for Pythagorean analysis"""
    console.print("[blue]FUNCTION CALL:[/blue] show_reasoning()")
    for i, step in enumerate(steps, 1):
        console.print(Panel(
            f"{step}",
            title=f"Step {i}",
            border_style="cyan"
        ))
    return TextContent(
        type="text",
        text="Reasoning shown"
    )


@mcp.tool()
def check_triple(a: int, b: int, c: int) -> TextContent:
    """
    Check if three numbers form a Pythagorean triple
    Returns: JSON string with verification result
    """
    console.print(f"[blue]FUNCTION CALL:[/blue] check_triple({a}, {b}, {c})")
    
    is_valid = is_pythagorean_triple(a, b, c)
    
    if is_valid:
        # Sort to get proper order
        sides = sorted([a, b, c])
        x, y, z = sides[0], sides[1], sides[2]
        
        # Check if primitive
        primitive = is_primitive(x, y)
        gcd_value = gcd(x, y)
        
        result = {
            "valid": True,
            "triple": f"({x}, {y}, {z})",
            "equation": f"{x}^2 + {y}^2 = {z}^2",
            "calculation": f"{x*x} + {y*y} = {z*z}",
            "primitive": primitive,
            "gcd": gcd_value,
            "classification": "PRIMITIVE" if primitive else "NON-PRIMITIVE"
        }
        
        console.print(Panel(
            f"[green]Valid Pythagorean Triple![/green]\n"
            f"Triple: {result['triple']}\n"
            f"Equation: {result['equation']}\n"
            f"Verification: {result['calculation']}\n"
            f"Classification: {result['classification']}\n"
            f"GCD: {gcd_value}",
            title="Verification Result",
            border_style="green"
        ))
    else:
        result = {
            "valid": False,
            "message": f"({a}, {b}, {c}) is NOT a Pythagorean Triple",
            "reason": f"Does not satisfy a^2 + b^2 = c^2 for any permutation"
        }
        
        console.print(Panel(
            f"[red]Not a Pythagorean Triple[/red]\n"
            f"{result['message']}\n"
            f"{result['reason']}",
            title="Verification Result",
            border_style="red"
        ))
    
    return TextContent(
        type="text",
        text=str(result)
    )


@mcp.tool()
def find_triples(max_c: int) -> TextContent:
    """
    Generate all Pythagorean triples up to max_c
    Returns: JSON string with primitive and non-primitive triples
    """
    console.print(f"[blue]FUNCTION CALL:[/blue] find_triples(max_c={max_c})")
    
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
    
    # Display results
    table = Table(title=f"Pythagorean Triples (c <= {max_c})", box=box.ROUNDED)
    table.add_column("Type", style="cyan", justify="center")
    table.add_column("Triple", style="green")
    table.add_column("Verification", style="yellow")
    table.add_column("GCD", justify="center")
    
    for triple in primitive[:5]:  # Show first 5 of each
        a, b, c = triple
        table.add_row(
            "PRIMITIVE",
            f"({a}, {b}, {c})",
            f"{a}² + {b}² = {c}²",
            "1"
        )
    
    for triple in non_primitive[:5]:  # Show first 5 of each
        a, b, c = triple
        g = gcd(a, b)
        table.add_row(
            "NON-PRIM",
            f"({a}, {b}, {c})",
            f"{a}² + {b}² = {c}²",
            str(g)
        )
    
    console.print(table)
    console.print(f"\n[cyan]Total Found:[/cyan] {len(primitive)} primitive, {len(non_primitive)} non-primitive")
    
    result = {
        "max_c": max_c,
        "primitive_count": len(primitive),
        "non_primitive_count": len(non_primitive),
        "primitive_triples": [str(t) for t in primitive],
        "non_primitive_triples": [str(t) for t in non_primitive]
    }
    
    return TextContent(
        type="text",
        text=str(result)
    )


@mcp.tool()
def calculate_gcd(a: int, b: int) -> TextContent:
    """
    Calculate the Greatest Common Divisor of two numbers
    Uses Euclidean algorithm with step-by-step explanation
    """
    console.print(f"[blue]FUNCTION CALL:[/blue] calculate_gcd({a}, {b})")
    
    original_a, original_b = a, b
    steps = []
    
    while b:
        quotient = a // b
        remainder = a % b
        steps.append(f"{a} = {b} × {quotient} + {remainder}")
        a, b = b, remainder
    
    result_gcd = a
    
    # Display steps
    console.print(Panel(
        "\n".join(steps),
        title=f"Euclidean Algorithm: GCD({original_a}, {original_b})",
        border_style="blue"
    ))
    console.print(f"[green]Result:[/green] GCD({original_a}, {original_b}) = {result_gcd}")
    
    result = {
        "a": original_a,
        "b": original_b,
        "gcd": result_gcd,
        "steps": steps,
        "interpretation": "PRIMITIVE triple" if result_gcd == 1 else "NON-PRIMITIVE triple"
    }
    
    return TextContent(
        type="text",
        text=str(result)
    )


@mcp.tool()
def verify_and_classify(a: int, b: int, c: int) -> TextContent:
    """
    Complete verification and classification of a potential Pythagorean triple
    Includes: validation, GCD calculation, primitive check, and detailed analysis
    """
    console.print(f"[blue]FUNCTION CALL:[/blue] verify_and_classify({a}, {b}, {c})")
    
    # Step 1: Check if valid triple
    is_valid = is_pythagorean_triple(a, b, c)
    
    if not is_valid:
        console.print(Panel(
            f"[red]INVALID TRIPLE[/red]\n"
            f"({a}, {b}, {c}) does not satisfy the Pythagorean theorem",
            border_style="red"
        ))
        return TextContent(
            type="text",
            text=f"INVALID: ({a}, {b}, {c}) is not a Pythagorean triple"
        )
    
    # Step 2: Sort and verify
    sides = sorted([a, b, c])
    x, y, z = sides[0], sides[1], sides[2]
    
    # Step 3: Calculate GCD
    gcd_value = gcd(x, y)
    primitive = is_primitive(x, y)
    
    # Step 4: Create detailed analysis
    table = Table(title="Pythagorean Triple Analysis", box=box.DOUBLE)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Triple", f"({x}, {y}, {z})")
    table.add_row("Equation", f"{x}² + {y}² = {z}²")
    table.add_row("Verification", f"{x*x} + {y*y} = {z*z}")
    table.add_row("Valid", "[green]YES[/green]")
    table.add_row("GCD(a, b)", str(gcd_value))
    table.add_row("Classification", "[yellow]PRIMITIVE[/yellow]" if primitive else "[blue]NON-PRIMITIVE[/blue]")
    
    console.print(table)
    
    result = {
        "valid": True,
        "triple": (x, y, z),
        "equation": f"{x}^2 + {y}^2 = {z}^2",
        "verification": f"{x*x} + {y*y} = {z*z}",
        "gcd": gcd_value,
        "primitive": primitive,
        "classification": "PRIMITIVE" if primitive else "NON-PRIMITIVE"
    }
    
    return TextContent(
        type="text",
        text=str(result)
    )


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

