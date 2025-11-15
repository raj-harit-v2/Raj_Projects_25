# modules/action.py

from typing import Dict, Any, Union
from pydantic import BaseModel
import asyncio
import types
import json


# Optional logging fallback
try:
    from agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")

class ToolCallResult(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Union[str, list, dict]
    raw_response: Any

MAX_TOOL_CALLS_PER_PLAN = 5

async def run_python_sandbox(code: str, dispatcher: Any) -> str:
    print("[action] [ENTERED] Entered run_python_sandbox()")

    # Create a fresh module scope
    sandbox = types.ModuleType("sandbox")

    try:
        # Patch MCP client with real dispatcher
        class SandboxMCP:
            def __init__(self, dispatcher):
                self.dispatcher = dispatcher
                self.call_count = 0

            async def call_tool(self, tool_name: str, input_dict: dict):
                self.call_count += 1
                if self.call_count > MAX_TOOL_CALLS_PER_PLAN:
                    raise RuntimeError(f"Exceeded max tool calls ({MAX_TOOL_CALLS_PER_PLAN}) in solve() plan.")
                # REAL tool call now
                result = await self.dispatcher.call_tool(tool_name, input_dict)
                
                # MCP returns CallToolResult with content array - extract the actual result
                # For search_stored_documents, FastMCP may serialize list[str] to JSON or return as separate TextContent items
                log("sandbox", f"[MCP_CALL] Tool '{tool_name}' returned type: {type(result)}")
                
                # Check if result has 'content' attribute (CallToolResult)
                if hasattr(result, 'content') and result.content:
                    log("sandbox", f"[MCP_CALL] Result has 'content' with {len(result.content)} items")
                    try:
                        import json
                        
                        extracted_result = None
                        
                        # Strategy 1: FastMCP returns list[str] as multiple TextContent items (one per list element)
                        # This is the most common case for search_stored_documents
                        if len(result.content) > 0:
                            log("sandbox", f"[MCP_CALL] Content array has {len(result.content)} items")
                            
                            # Extract text from all content items
                            extracted_list = []
                            for idx, item in enumerate(result.content):
                                text = None
                                if hasattr(item, 'text'):
                                    text = item.text
                                elif isinstance(item, str):
                                    text = item
                                elif isinstance(item, dict) and 'text' in item:
                                    text = item['text']
                                
                                if text is not None:
                                    extracted_list.append(text)
                            
                            if extracted_list:
                                log("sandbox", f"[MCP_CALL] SUCCESS (Strategy 1): Extracted {len(extracted_list)} items from TextContent array")
                                return extracted_list
                        
                        # Strategy 2: Single content item as JSON string (fallback for other tools)
                        if len(result.content) == 1:
                            content_item = result.content[0]
                            log("sandbox", f"[MCP_CALL] Single content item, type: {type(content_item)}")
                            
                            text = None
                            if hasattr(content_item, 'text'):
                                text = content_item.text
                            elif isinstance(content_item, str):
                                text = content_item
                            
                            if text is not None:
                                # Try parsing as JSON (for tools that return JSON)
                                try:
                                    parsed = json.loads(str(text))
                                    if isinstance(parsed, list):
                                        log("sandbox", f"[MCP_CALL] SUCCESS (Strategy 2): Parsed JSON list with {len(parsed)} items")
                                        return parsed
                                except json.JSONDecodeError:
                                    # Not JSON - return as single-item list
                                    log("sandbox", f"[MCP_CALL] SUCCESS (Strategy 2): Returning plain string as list")
                                    return [text]
                        
                        # If we get here, extraction failed
                        log("sandbox", f"[MCP_CALL] WARNING: Could not extract list from content")
                                
                    except Exception as e:
                        log("sandbox", f"[ERROR] Error extracting result: {e}")
                        import traceback
                        log("sandbox", f"[ERROR] Traceback: {traceback.format_exc()}")
                elif isinstance(result, list):
                    # Already a list - return directly
                    log("sandbox", f"[MCP_CALL] Result is already a list with {len(result)} items")
                    return result
                
                # Fallback: return result as-is (might already be the right format)
                log("sandbox", f"[MCP_CALL] WARNING: Returning result as-is (type: {type(result)})")
                return result

        sandbox.mcp = SandboxMCP(dispatcher)

        # Preload safe built-ins into the sandbox
        import json, re, math
        sandbox.__dict__["json"] = json
        sandbox.__dict__["re"] = re
        sandbox.__dict__["math"] = math

        # Execute solve fn dynamically
        exec(compile(code, "<solve_plan>", "exec"), sandbox.__dict__)

        solve_fn = sandbox.__dict__.get("solve")
        if solve_fn is None:
            raise ValueError("No solve() function found in plan.")

        if asyncio.iscoroutinefunction(solve_fn):
            result = await solve_fn()
        else:
            result = solve_fn()

        # Clean result formatting
        if isinstance(result, dict) and "result" in result:
            return f"{result['result']}"
        elif isinstance(result, dict):
            return f"{json.dumps(result)}"
        elif isinstance(result, list):
            return f"{' '.join(str(r) for r in result)}"
        else:
            return f"{result}"






    except Exception as e:
        log("sandbox", f"[ERROR] Execution error: {e}")
        return f"[sandbox error: {str(e)}]"
