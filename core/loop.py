# modules/loop.py

import asyncio
from modules.perception import run_perception
from modules.decision import generate_plan
from modules.action import run_python_sandbox
from modules.model_manager import ModelManager
from core.session import MultiMCP
from core.strategy import select_decision_prompt_path
from core.context import AgentContext
from modules.tools import summarize_tools
import re

try:
    from agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")

class AgentLoop:
    def __init__(self, context: AgentContext):
        self.context = context
        self.mcp = self.context.dispatcher
        self.model = ModelManager()

    async def run(self):
        max_steps = self.context.agent_profile.strategy.max_steps

        for step in range(max_steps):
            print(f"[STEP {step+1}/{max_steps}] Starting...")
            self.context.step = step
            lifelines_left = self.context.agent_profile.strategy.max_lifelines_per_step

            while lifelines_left >= 0:
                # === Perception ===
                user_input_override = getattr(self.context, "user_input_override", None)
                perception = await run_perception(context=self.context, user_input=user_input_override or self.context.user_input)

                print(f"[perception] {perception}")

                selected_servers = perception.selected_servers
                selected_tools = self.mcp.get_tools_from_servers(selected_servers)
                if not selected_tools:
                    log("loop", "[WARNING] No tools selected - aborting step.")
                    break

                # === Planning ===
                tool_descriptions = summarize_tools(selected_tools)
                prompt_path = select_decision_prompt_path(
                    planning_mode=self.context.agent_profile.strategy.planning_mode,
                    exploration_mode=self.context.agent_profile.strategy.exploration_mode,
                )

                # Get historical context if available
                historical_context = getattr(self.context, "historical_context", 
                                            "No relevant historical context available.")
                
                plan = await generate_plan(
                    user_input=self.context.user_input,
                    perception=perception,
                    memory_items=self.context.memory.get_session_items(),
                    tool_descriptions=tool_descriptions,
                    prompt_path=prompt_path,
                    step_num=step + 1,
                    max_steps=max_steps,
                    historical_context=historical_context,
                )
                print(f"[plan] {plan}")

                # === Execution ===
                if re.search(r"^\s*(async\s+)?def\s+solve\s*\(", plan, re.MULTILINE):
                    print("[loop] Detected solve() plan - running sandboxed...")

                    self.context.log_subtask(tool_name="solve_sandbox", status="pending")
                    result = await run_python_sandbox(plan, dispatcher=self.mcp)

                    success = False
                    if isinstance(result, str):
                        result = result.strip()
                        if result.startswith("FINAL_ANSWER:"):
                            # Post-process: Summarize if answer is too long (contains raw chunks)
                            answer_content = result.replace("FINAL_ANSWER:", "").strip()
                            
                            # Check if answer looks like raw chunks (long, contains references, etc.)
                            is_raw_chunk = (
                                len(answer_content) > 500 or  # Too long
                                "[Source:" in answer_content or  # Contains source references
                                answer_content.count("\n") > 3  # Multiple lines (likely chunks)
                            )
                            
                            if is_raw_chunk:
                                # Summarize using LLM
                                from modules.model_manager import ModelManager
                                model = ModelManager()
                                
                                summarize_prompt = f"""The following is a raw document search result. Extract the key information and provide a concise 1-3 sentence answer to the user's query.

User Query: {self.context.user_input}

Raw Search Results:
{answer_content[:2000]}

Provide a concise summary (1-3 sentences) that directly answers the user's query:"""
                                
                                try:
                                    summary = (await model.generate_text(summarize_prompt)).strip()
                                    # Clean up summary (remove markdown, etc.)
                                    if summary.startswith("```"):
                                        summary = summary.strip("`").strip()
                                        if summary.lower().startswith("python") or summary.lower().startswith("text"):
                                            summary = summary.split("\n", 1)[1] if "\n" in summary else summary
                                    result = f"FINAL_ANSWER: {summary}"
                                    log("loop", "[SUMMARIZED] Long answer summarized to concise response")
                                except Exception as e:
                                    log("loop", f"[WARNING] Summarization failed: {e}, using original answer")
                            
                            success = True
                            self.context.final_answer = result
                            self.context.update_subtask_status("solve_sandbox", "success")
                            self.context.memory.add_tool_output(
                                tool_name="solve_sandbox",
                                tool_args={"plan": plan},
                                tool_result={"result": result},
                                success=True,
                                tags=["sandbox"],
                            )
                            return {"status": "done", "result": self.context.final_answer}
                        elif result.startswith("FURTHER_PROCESSING_REQUIRED:"):
                            content = result.split("FURTHER_PROCESSING_REQUIRED:")[1].strip()
                            self.context.user_input_override  = (
                                f"Original user task: {self.context.user_input}\n\n"
                                f"Your last tool produced this result:\n\n"
                                f"{content}\n\n"
                                f"If this fully answers the task, return:\n"
                                f"FINAL_ANSWER: your answer\n\n"
                                f"Otherwise, return the next FUNCTION_CALL."
                            )
                            log("loop", f"[FORWARDING] Forwarding intermediate result to next step:\n{self.context.user_input_override}\n\n")
                            log("loop", f"[CONTINUE] Continuing based on FURTHER_PROCESSING_REQUIRED - Step {step+1} continues...")
                            break  # Step will continue
                        elif result.startswith("[sandbox error:"):
                            success = False
                            self.context.final_answer = "FINAL_ANSWER: [Execution failed]"
                        else:
                            success = True
                            self.context.final_answer = f"FINAL_ANSWER: {result}"
                    else:
                        self.context.final_answer = f"FINAL_ANSWER: {result}"

                    if success:
                        self.context.update_subtask_status("solve_sandbox", "success")
                    else:
                        self.context.update_subtask_status("solve_sandbox", "failure")

                    self.context.memory.add_tool_output(
                        tool_name="solve_sandbox",
                        tool_args={"plan": plan},
                        tool_result={"result": result},
                        success=success,
                        tags=["sandbox"],
                    )

                    if success and "FURTHER_PROCESSING_REQUIRED:" not in result:
                        return {"status": "done", "result": self.context.final_answer}
                    else:
                        lifelines_left -= 1
                        log("loop", f"[RETRY] Retrying... Lifelines left: {lifelines_left}")
                        continue
                else:
                    log("loop", f"[WARNING] Invalid plan detected - retrying... Lifelines left: {lifelines_left-1}")
                    lifelines_left -= 1
                    continue

        log("loop", "[WARNING] Max steps reached without finding final answer.")
        self.context.final_answer = "FINAL_ANSWER: [Max steps reached]"
        return {"status": "done", "result": self.context.final_answer}
