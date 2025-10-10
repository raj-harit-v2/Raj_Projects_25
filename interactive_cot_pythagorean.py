"""
Interactive Chain of Thought Pythagorean Triple Finder
Works WITHOUT AI - uses MCP tools directly with user input
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel

console = Console()


async def interactive_menu():
    """Interactive menu system using COT tools"""
    
    server_params = StdioServerParameters(
        command="python",
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
                        
                        console.print(f"\n[green]Result:[/green] {result.content[0].text[:200]}...")
                        
                    except ValueError:
                        console.print("[red]Error: Please enter valid integers[/red]")
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                
                elif choice == "2":
                    # Find triples
                    try:
                        max_c = int(input("\n[yellow]Enter maximum hypotenuse value (c_max):[/yellow] "))
                        
                        if max_c < 3:
                            console.print("[red]Error: Please enter a value >= 3[/red]")
                            continue
                        
                        console.print(f"\n[cyan]Finding all Pythagorean triples with c <= {max_c}...[/cyan]")
                        
                        result = await session.call_tool(
                            "find_triples",
                            arguments={"max_c": max_c}
                        )
                        
                        # The result is displayed by the MCP tool in stderr
                        console.print(f"\n[green]Search complete![/green]")
                        
                    except ValueError:
                        console.print("[red]Error: Please enter a valid integer[/red]")
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                
                elif choice == "3":
                    # Calculate GCD
                    try:
                        console.print("\n[yellow]Enter two positive integers:[/yellow]")
                        a = int(input("  First number:  "))
                        b = int(input("  Second number: "))
                        
                        if a <= 0 or b <= 0:
                            console.print("[red]Error: Both numbers must be positive[/red]")
                            continue
                        
                        console.print(f"\n[cyan]Calculating GCD({a}, {b}) using Euclidean algorithm...[/cyan]")
                        
                        result = await session.call_tool(
                            "calculate_gcd",
                            arguments={"a": a, "b": b}
                        )
                        
                        console.print(f"\n[green]Calculation complete![/green]")
                        
                    except ValueError:
                        console.print("[red]Error: Please enter valid integers[/red]")
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                
                elif choice == "4":
                    # Verify and classify
                    try:
                        console.print("\n[yellow]Enter three integers to verify:[/yellow]")
                        a = int(input("  First number (a):  "))
                        b = int(input("  Second number (b): "))
                        c = int(input("  Third number (c):  "))
                        
                        if a <= 0 or b <= 0 or c <= 0:
                            console.print("[red]Error: All numbers must be positive[/red]")
                            continue
                        
                        console.print(f"\n[cyan]Performing complete analysis of ({a}, {b}, {c})...[/cyan]")
                        
                        result = await session.call_tool(
                            "verify_and_classify",
                            arguments={"a": a, "b": b, "c": c}
                        )
                        
                        console.print(f"\n[green]Analysis complete![/green]")
                        
                    except ValueError:
                        console.print("[red]Error: Please enter valid integers[/red]")
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                
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

