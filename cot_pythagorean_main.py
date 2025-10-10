"""
Chain of Thought Pythagorean Triple Finder - Main Program
Uses AI (Gemini) to analyze Pythagorean triples with step-by-step reasoning
"""

import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
import asyncio
from rich.console import Console
from rich.panel import Panel

console = Console()

# Load environment variables and setup Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        return response.text.strip()
    except asyncio.TimeoutError:
        return None
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None

async def main():
    try:
        console.print(Panel("AI-Powered Pythagorean Triple Analyzer", border_style="cyan"))

        server_params = StdioServerParameters(
            command="python",
            args=["cot_pythagorean_finder.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                system_prompt = """You are a mathematical reasoning agent specialized in Pythagorean triples.
You have access to these tools:
- show_reasoning(steps: list) - Show your step-by-step reasoning
- check_triple(a, b, c) - Check if three numbers form a Pythagorean triple
- find_triples(max_c) - Find all triples up to max_c
- calculate_gcd(a, b) - Calculate GCD with steps
- verify_and_classify(a, b, c) - Complete analysis of a triple

First show your reasoning, then use the appropriate tools.

Respond with EXACTLY ONE line in one of these formats:
1. FUNCTION_CALL: function_name|param1|param2|...
2. FINAL_ANSWER: [answer]

Example:
User: Analyze the triple (3, 4, 5)
Assistant: FUNCTION_CALL: show_reasoning|["1. Check if 3² + 4² = 5²", "2. Calculate GCD(3,4)", "3. Classify as primitive or non-primitive"]
User: Next step?
Assistant: FUNCTION_CALL: verify_and_classify|3|4|5
User: Analysis complete.
Assistant: FINAL_ANSWER: [(3,4,5) is a valid PRIMITIVE Pythagorean triple]
"""

                # Example problems
                problems = [
                    "Verify and classify the triple (8, 15, 17)",
                    "Is (6, 8, 10) a Pythagorean triple? What type?",
                    "Find all Pythagorean triples where c ≤ 15"
                ]

                for problem in problems:
                    console.print(f"\n{'='*70}")
                    console.print(Panel(f"Problem: {problem}", border_style="yellow"))
                    console.print(f"{'='*70}\n")

                    prompt = f"{system_prompt}\n\nUser: {problem}\nAssistant:"
                    conversation_history = []

                    for iteration in range(10):  # Max 10 reasoning steps
                        result = await generate_with_timeout(client, prompt, timeout=10)
                        
                        if not result:
                            console.print("[red]No response from AI[/red]")
                            break

                        console.print(f"\nAssistant: {result}")

                        if result.startswith("FUNCTION_CALL:"):
                            # Parse and execute function call
                            parts = result.replace("FUNCTION_CALL:", "").strip().split("|")
                            func_name = parts[0].strip()
                            
                            # Parse arguments
                            args = {}
                            if len(parts) > 1:
                                if func_name == "show_reasoning":
                                    import json
                                    args["steps"] = json.loads(parts[1])
                                elif func_name == "check_triple":
                                    args["a"] = int(parts[1])
                                    args["b"] = int(parts[2])
                                    args["c"] = int(parts[3])
                                elif func_name == "find_triples":
                                    args["max_c"] = int(parts[1])
                                elif func_name == "calculate_gcd":
                                    args["a"] = int(parts[1])
                                    args["b"] = int(parts[2])
                                elif func_name == "verify_and_classify":
                                    args["a"] = int(parts[1])
                                    args["b"] = int(parts[2])
                                    args["c"] = int(parts[3])

                            # Execute tool
                            tool_result = await session.call_tool(func_name, arguments=args)
                            conversation_history.append({
                                "function": func_name,
                                "args": args,
                                "result": tool_result
                            })
                            prompt += f"\nUser: Tool executed. Next step?\nAssistant:"
                            
                        elif result.startswith("FINAL_ANSWER:"):
                            console.print("\n[green]Analysis completed![/green]")
                            break
                        
                        prompt += f"\nAssistant: {result}"

                console.print("\n[green]All analyses completed![/green]")
                
                # Give time for cleanup
                await asyncio.sleep(0.1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except* Exception as eg:
        # Suppress TaskGroup cleanup errors from MCP
        for exc in eg.exceptions:
            if "TaskGroup" not in str(type(exc).__name__):
                raise

