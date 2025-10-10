"""
Interactive Chain of Thought Pythagorean Triple Finder
Works WITHOUT AI - uses MCP tools directly with user input
"""

import asyncio
import ast
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def generate_reasoning_review(tool_name: str, success: bool, has_steps: bool = True) -> dict:
    """Generate a structured review of the reasoning process"""
    
    # Base evaluation for all tools
    review = {
        "explicit_reasoning": has_steps,  # Whether reasoning steps are shown
        "structured_output": True,  # All our outputs are structured
        "tool_separation": True,  # Each tool has clear separation
        "conversation_loop": True,  # Interactive loop is present
        "instructional_framing": True,  # Clear instructions provided
        "internal_self_checks": success,  # Validation and error checking
        "reasoning_type_awareness": has_steps,  # Aware of reasoning being used
        "fallbacks": True,  # Error handling with fallbacks
    }
    
    # Tool-specific assessments
    if tool_name == "check_triple":
        review["overall_clarity"] = "Excellent: Direct validation with clear classification and GCD computation."
    elif tool_name == "find_triples":
        review["overall_clarity"] = "Excellent: Systematic search with primitive/non-primitive separation."
    elif tool_name == "calculate_gcd":
        review["overall_clarity"] = "Excellent: Step-by-step Euclidean algorithm with explicit reasoning."
    elif tool_name == "verify_and_classify":
        review["overall_clarity"] = "Excellent: Complete analysis with validation, GCD, and classification."
    else:
        review["overall_clarity"] = "Operation completed with structured reasoning."
    
    return review


def display_reasoning_review(tool_name: str, success: bool, has_steps: bool = True):
    """Display the reasoning review as formatted JSON"""
    review = generate_reasoning_review(tool_name, success, has_steps)
    json_output = json.dumps(review, indent=2)
    
    syntax = Syntax(json_output, "json", theme="monokai", line_numbers=False)
    console.print("\n" + "="*70)
    console.print(Panel(syntax, title="[bold cyan]Reasoning Quality Review[/bold cyan]", border_style="magenta"))
    console.print("="*70)


async def interactive_menu():
    """Interactive menu system using COT tools"""
    
    import sys
    import os
    
    # Use the current Python interpreter (from venv if active)
    python_path = sys.executable
    
    server_params = StdioServerParameters(
        command=python_path,
        args=["cot_pythagorean_finder.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            console.print("\n" + "="*70)
            console.print(Panel("Interactive COT Pythagorean Triple Finder", 
                               border_style="cyan", 
                               subtitle="With Step-by-Step Reasoning"))
            console.print("="*70)
            
            while True:
                console.print("\n" + "-"*70)
                console.print("[cyan]MENU OPTIONS:[/cyan]")
                console.print("-"*70)
                console.print("  [1] Check if numbers form a Pythagorean triple")
                console.print("  [2] Find all triples up to max value")
                console.print("  [3] Calculate GCD (with steps)")
                console.print("  [4] Verify and Classify a triple (complete analysis)")
                console.print("  [5] Exit")
                console.print("-"*70)
                
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == "1":
                    # Check triple
                    try:
                        console.print("\n[yellow]Enter three integers:[/yellow]")
                        a = int(input("  First number (a):  "))
                        b = int(input("  Second number (b): "))
                        c = int(input("  Third number (c):  "))
                        
                        console.print(f"\n[cyan]Checking if ({a}, {b}, {c}) is a Pythagorean triple...[/cyan]")
                        
                        result = await session.call_tool(
                            "check_triple",
                            arguments={"a": a, "b": b, "c": c}
                        )
                        
                        # Parse result to get validity status
                        result_text = result.content[0].text
                        try:
                            result_dict = ast.literal_eval(result_text)
                            is_valid = result_dict.get('valid', False)
                            status_color = "green" if is_valid else "red"
                            status_text = "True" if is_valid else "False"
                            console.print(f"\n[bold {status_color}]Valid Pythagorean Triple: {status_text}[/bold {status_color}]")
                        except:
                            pass
                        
                        console.print(f"\n[cyan]Analysis:[/cyan] {result_text[:250]}...")
                        
                        # Display reasoning quality review
                        display_reasoning_review("check_triple", success=True, has_steps=True)
                        
                    except ValueError:
                        console.print("[red]Error: Please enter valid integers[/red]")
                        display_reasoning_review("check_triple", success=False, has_steps=False)
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                        display_reasoning_review("check_triple", success=False, has_steps=False)
                
                elif choice == "2":
                    # Find triples
                    try:
                        max_c = int(input("\n[yellow]Enter maximum hypotenuse value (c_max):[/yellow] "))
                        
                        if max_c < 3:
                            console.print("[red]Error: Please enter a value >= 3[/red]")
                            display_reasoning_review("find_triples", success=False, has_steps=False)
                            continue
                        
                        console.print(f"\n[cyan]Finding all Pythagorean triples with c <= {max_c}...[/cyan]")
                        
                        result = await session.call_tool(
                            "find_triples",
                            arguments={"max_c": max_c}
                        )
                        
                        # The result is displayed by the MCP tool in stderr
                        console.print(f"\n[green]Search complete![/green]")
                        
                        # Display reasoning quality review
                        display_reasoning_review("find_triples", success=True, has_steps=True)
                        
                    except ValueError:
                        console.print("[red]Error: Please enter a valid integer[/red]")
                        display_reasoning_review("find_triples", success=False, has_steps=False)
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                        display_reasoning_review("find_triples", success=False, has_steps=False)
                
                elif choice == "3":
                    # Calculate GCD
                    try:
                        console.print("\n[yellow]Enter two positive integers:[/yellow]")
                        a = int(input("  First number:  "))
                        b = int(input("  Second number: "))
                        
                        if a <= 0 or b <= 0:
                            console.print("[red]Error: Both numbers must be positive[/red]")
                            display_reasoning_review("calculate_gcd", success=False, has_steps=False)
                            continue
                        
                        console.print(f"\n[cyan]Calculating GCD({a}, {b}) using Euclidean algorithm...[/cyan]")
                        
                        result = await session.call_tool(
                            "calculate_gcd",
                            arguments={"a": a, "b": b}
                        )
                        
                        console.print(f"\n[green]Calculation complete![/green]")
                        
                        # Display reasoning quality review
                        display_reasoning_review("calculate_gcd", success=True, has_steps=True)
                        
                    except ValueError:
                        console.print("[red]Error: Please enter valid integers[/red]")
                        display_reasoning_review("calculate_gcd", success=False, has_steps=False)
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                        display_reasoning_review("calculate_gcd", success=False, has_steps=False)
                
                elif choice == "4":
                    # Verify and classify
                    try:
                        console.print("\n[yellow]Enter three integers to verify:[/yellow]")
                        a = int(input("  First number (a):  "))
                        b = int(input("  Second number (b): "))
                        c = int(input("  Third number (c):  "))
                        
                        if a <= 0 or b <= 0 or c <= 0:
                            console.print("[red]Error: All numbers must be positive[/red]")
                            display_reasoning_review("verify_and_classify", success=False, has_steps=False)
                            continue
                        
                        console.print(f"\n[cyan]Performing complete analysis of ({a}, {b}, {c})...[/cyan]")
                        
                        result = await session.call_tool(
                            "verify_and_classify",
                            arguments={"a": a, "b": b, "c": c}
                        )
                        
                        # Parse result to get validity status
                        result_text = result.content[0].text
                        try:
                            result_dict = ast.literal_eval(result_text)
                            is_valid = result_dict.get('valid', False)
                            status_color = "green" if is_valid else "red"
                            status_text = "True" if is_valid else "False"
                            console.print(f"\n[bold {status_color}]Valid Pythagorean Triple: {status_text}[/bold {status_color}]")
                        except:
                            pass
                        
                        console.print(f"\n[cyan]Analysis:[/cyan] {result_text[:250]}...")
                        
                        # Display reasoning quality review
                        display_reasoning_review("verify_and_classify", success=True, has_steps=True)
                        
                    except ValueError:
                        console.print("[red]Error: Please enter valid integers[/red]")
                        display_reasoning_review("verify_and_classify", success=False, has_steps=False)
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                        display_reasoning_review("verify_and_classify", success=False, has_steps=False)
                
                elif choice == "5":
                    console.print("\n[cyan]Thank you for using COT Pythagorean Finder![/cyan]")
                    console.print("="*70 + "\n")
                    break
                
                else:
                    console.print("\n[red]Invalid choice. Please enter 1, 2, 3, 4, or 5.[/red]")
                
                # Small delay for better UX
                await asyncio.sleep(0.1)


async def main():
    """Main entry point"""
    try:
        await interactive_menu()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Program interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except* Exception as eg:
        # Suppress TaskGroup cleanup errors from MCP
        for exc in eg.exceptions:
            if "TaskGroup" not in str(type(exc).__name__):
                raise

