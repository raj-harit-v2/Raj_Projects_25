# agent.py

import asyncio
import yaml
from core.loop import AgentLoop
from core.session import MultiMCP
from core.context import MemoryItem, AgentContext
from modules.heuristics import preprocess_query, postprocess_result
from modules.historical_context import HistoricalContextManager
import datetime
from pathlib import Path
import json
import re

def log(stage: str, msg: str):
    """Simple timestamped console logger."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")

async def main():
    print("*** Cortex-R Agent Ready (Enhanced with Heuristics & Historical Context) ***")
    current_session = None
    
    # Initialize historical context manager
    historical_mgr = HistoricalContextManager()

    with open("config/profiles.yaml", "r") as f:
        profile = yaml.safe_load(f)
        mcp_servers_list = profile.get("mcp_servers", [])
        mcp_servers = {server["id"]: server for server in mcp_servers_list}

    multi_mcp = MultiMCP(server_configs=list(mcp_servers.values()))
    await multi_mcp.initialize()

    try:
        force_fresh = False  # Flag to bypass cache
        while True:
            user_input = input("[USER] What do you want to solve today? -> ").strip()
            
            # Handle empty input - ask again
            if not user_input:
                print("[INFO] Please enter a query. (Type 'exit' to quit)")
                continue
            
            if user_input.lower() == 'exit':
                break
            
            # Handle "new" command - can be "new" or "new <query>"
            if user_input.lower().startswith('new'):
                current_session = None
                force_fresh = True
                # Extract query if provided after "new"
                if len(user_input) > 3:
                    user_input = user_input[3:].strip()
                else:
                    continue  # Just "new" without query, wait for next input

            # ===== PHASE 2: Apply Heuristics - Preprocessing =====
            log("heuristics", "Preprocessing query...")
            processed_query = preprocess_query(user_input)
            
            log("heuristics", f"Query Type: {processed_query['query_type']}")
            log("heuristics", f"Topic: {processed_query['topic']}")
            log("heuristics", f"Query Hash: {processed_query['query_hash']}")
            
            # Check for duplicate (cache hit) - skip if force_fresh is True
            if not force_fresh:
                duplicate = historical_mgr.check_duplicate(processed_query['query_hash'])
                if duplicate:
                    log("historical", "[CACHE HIT] Found recent similar query.")
                    print(f"\n[CACHED ANSWER] {duplicate['result_summary']}")
                    print("(Use 'new' to force fresh execution)")
                    continue
            else:
                force_fresh = False  # Reset flag after use
            
            # Get historical context for this topic
            historical_context = historical_mgr.format_context_for_prompt(
                processed_query['topic'],
                limit=3
            )
            log("historical", f"Retrieved {processed_query['topic']} context")

            # Use canonical query
            canonical_input = processed_query['canonical']

            while True:
                context = AgentContext(
                    user_input=canonical_input,
                    session_id=current_session,
                    dispatcher=multi_mcp,
                    mcp_server_descriptions=mcp_servers,
                )
                
                # Attach processed query info and historical context to context
                context.processed_query = processed_query
                context.historical_context = historical_context
                
                agent = AgentLoop(context)
                if not current_session:
                    current_session = context.session_id

                result = await agent.run()

                if isinstance(result, dict):
                    answer = result["result"]
                    
                    # ===== PHASE 2: Apply Heuristics - Postprocessing =====
                    post_result = postprocess_result(result, answer)
                    
                    log("heuristics", f"Confidence: {post_result['confidence']['score']:.2f}")
                    log("heuristics", f"Incomplete: {post_result['is_incomplete']}")
                    
                    if "FINAL_ANSWER:" in answer:
                        final_answer = answer.split('FINAL_ANSWER:')[1].strip()
                        sanitized_answer = post_result['sanitized_output']
                        
                        # Don't cache error results
                        is_error = (
                            "error" in final_answer.lower() or 
                            "ERROR" in final_answer or
                            "An error occurred" in final_answer or
                            "Expecting value" in final_answer or
                            "failed" in final_answer.lower()
                        )
                        
                        # Store in historical context (only if not an error)
                        if not is_error:
                            historical_mgr.add_conversation(
                                query=user_input,
                                query_hash=processed_query['query_hash'],
                                topic=processed_query['topic'],
                                result=final_answer,
                                session_id=current_session,
                                success=True,
                                metadata={
                                    "query_type": processed_query['query_type'],
                                    "confidence": post_result['confidence']['score'],
                                    "entities": processed_query['entities']
                                }
                            )
                        else:
                            log("historical", "[SKIP CACHE] Error result - not caching")
                        
                        print(f"\n[FINAL ANSWER] {sanitized_answer}")
                        break
                    elif "FURTHER_PROCESSING_REQUIRED:" in answer:
                        canonical_input = answer.split("FURTHER_PROCESSING_REQUIRED:")[1].strip()
                        print(f"\n[FURTHER PROCESSING] {canonical_input}")
                        continue  # Re-run agent with updated input
                    else:
                        print(f"\n[FINAL ANSWER] (raw): {answer}")
                        break
                else:
                    print(f"\n[FINAL ANSWER] (unexpected): {result}")
                    break
    except KeyboardInterrupt:
        print("\n[EXIT] Received exit signal. Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())



# Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.
# How much Anmol singh paid for his DLF apartment via Capbridge? 
# What do you know about Don Tapscott and Anthony Williams?
# What is the relationship between Gensol and Go-Auto?
# which course are we teaching on Canvas LMS? "H:\DownloadsH\How to use Canvas LMS.pdf"
# Summarize this page: https://theschoolof.ai/
# What is the log value of the amount that Anmol singh paid for his DLF apartment via Capbridge? 