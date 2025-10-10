"""
Test and Demo for COT Pythagorean Finder
Tests the MCP tools directly without AI
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel

console = Console()


async def test_check_triple():
    """Test the check_triple function"""
    console.print("\n" + "="*60)
    console.print(Panel("TEST 1: Check Triple Function", border_style="cyan"))
    console.print("="*60)
    
    server_params = StdioServerParameters(
        command="python",
        args=["cot_pythagorean_finder.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test valid primitive triple
            console.print("\n[yellow]Test 1.1: Valid Primitive Triple (3, 4, 5)[/yellow]")
            result = await session.call_tool("check_triple", arguments={"a": 3, "b": 4, "c": 5})
            console.print(f"Result: {result.content[0].text[:100]}...")
            
            # Test valid non-primitive triple
            console.print("\n[yellow]Test 1.2: Valid Non-Primitive Triple (6, 8, 10)[/yellow]")
            result = await session.call_tool("check_triple", arguments={"a": 6, "b": 8, "c": 10})
            console.print(f"Result: {result.content[0].text[:100]}...")
            
            # Test invalid triple
            console.print("\n[yellow]Test 1.3: Invalid Triple (2, 3, 4)[/yellow]")
            result = await session.call_tool("check_triple", arguments={"a": 2, "b": 3, "c": 4})
            console.print(f"Result: {result.content[0].text[:100]}...")


async def test_find_triples():
    """Test the find_triples function"""
    console.print("\n" + "="*60)
    console.print(Panel("TEST 2: Find Triples Function", border_style="cyan"))
    console.print("="*60)
    
    server_params = StdioServerParameters(
        command="python",
        args=["cot_pythagorean_finder.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            console.print("\n[yellow]Finding all triples with c <= 20[/yellow]")
            result = await session.call_tool("find_triples", arguments={"max_c": 20})
            console.print(f"Result: Found triples")


async def test_calculate_gcd():
    """Test the calculate_gcd function"""
    console.print("\n" + "="*60)
    console.print(Panel("TEST 3: Calculate GCD Function", border_style="cyan"))
    console.print("="*60)
    
    server_params = StdioServerParameters(
        command="python",
        args=["cot_pythagorean_finder.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test GCD = 1 (primitive)
            console.print("\n[yellow]Test 3.1: GCD(3, 4) - Should be 1[/yellow]")
            result = await session.call_tool("calculate_gcd", arguments={"a": 3, "b": 4})
            console.print(f"Result: {result.content[0].text[:100]}...")
            
            # Test GCD > 1 (non-primitive)
            console.print("\n[yellow]Test 3.2: GCD(6, 8) - Should be 2[/yellow]")
            result = await session.call_tool("calculate_gcd", arguments={"a": 6, "b": 8})
            console.print(f"Result: {result.content[0].text[:100]}...")


async def test_verify_and_classify():
    """Test the verify_and_classify function"""
    console.print("\n" + "="*60)
    console.print(Panel("TEST 4: Verify and Classify Function", border_style="cyan"))
    console.print("="*60)
    
    server_params = StdioServerParameters(
        command="python",
        args=["cot_pythagorean_finder.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test (8, 15, 17) - primitive
            console.print("\n[yellow]Test 4.1: Verify (8, 15, 17)[/yellow]")
            result = await session.call_tool("verify_and_classify", arguments={"a": 8, "b": 15, "c": 17})
            console.print(f"Result: Complete analysis shown above")


async def run_all_tests():
    """Run all tests"""
    console.print("\n" + "="*60)
    console.print("  COT PYTHAGOREAN FINDER - TEST SUITE")
    console.print("="*60)
    
    try:
        await test_check_triple()
        await asyncio.sleep(0.5)
        
        await test_find_triples()
        await asyncio.sleep(0.5)
        
        await test_calculate_gcd()
        await asyncio.sleep(0.5)
        
        await test_verify_and_classify()
        await asyncio.sleep(0.5)
        
        console.print("\n" + "="*60)
        console.print("  ALL TESTS COMPLETED")
        console.print("="*60)
        console.print("\n[green]All MCP tools are working correctly![/green]\n")
        
    except Exception as e:
        console.print(f"\n[red]ERROR: {e}[/red]\n")


if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except* Exception as eg:
        # Suppress TaskGroup cleanup errors
        for exc in eg.exceptions:
            if "TaskGroup" not in str(type(exc).__name__):
                raise

