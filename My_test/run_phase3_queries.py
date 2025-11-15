"""
Phase 3: Step 5 - Execute 3 Brand-New Unique Queries
Captures full Query > Perception > Decision > Action > Result logs
"""

import asyncio
import yaml
import json
from datetime import datetime
from pathlib import Path
from core.loop import AgentLoop
from core.session import MultiMCP
from core.context import MemoryItem, AgentContext
from modules.heuristics import preprocess_query, postprocess_result
from modules.historical_context import HistoricalContextManager

# Logging setup
log_buffer = []

def log(stage: str, msg: str):
    """Timestamped logger that also captures to buffer"""
    now = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{now}] [{stage}] {msg}"
    print(log_entry)
    log_buffer.append(log_entry)

async def run_query_with_logging(query: str, query_num: int):
    """Run a single query and capture all logs"""
    global log_buffer
    log_buffer = []
    
    log("PHASE3", f"=== QUERY {query_num}: {query} ===")
    log("PHASE3", f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize
    historical_mgr = HistoricalContextManager()
    
    with open("config/profiles.yaml", "r") as f:
        profile = yaml.safe_load(f)
        mcp_servers_list = profile.get("mcp_servers", [])
        mcp_servers = {server["id"]: server for server in mcp_servers_list}
    
    multi_mcp = MultiMCP(server_configs=list(mcp_servers.values()))
    await multi_mcp.initialize()
    
    try:
        # Preprocessing
        log("PHASE3", "--- STEP 1: QUERY PREPROCESSING ---")
        processed_query = preprocess_query(query)
        log("HEURISTICS", f"Canonical Query: {processed_query['canonical']}")
        log("HEURISTICS", f"Query Type: {processed_query['query_type']}")
        log("HEURISTICS", f"Topic: {processed_query['topic']}")
        log("HEURISTICS", f"Entities: {processed_query['entities']}")
        log("HEURISTICS", f"Query Hash: {processed_query['query_hash']}")
        
        # Cache check
        log("PHASE3", "--- STEP 2: CACHE CHECK ---")
        duplicate = historical_mgr.check_duplicate(processed_query['query_hash'])
        if duplicate:
            log("HISTORICAL", "[CACHE HIT] Found recent similar query")
            log("HISTORICAL", f"Cached Result: {duplicate['result_summary'][:200]}...")
        else:
            log("HISTORICAL", "[CACHE MISS] Proceeding with fresh execution")
        
        # Historical context
        log("PHASE3", "--- STEP 3: HISTORICAL CONTEXT RETRIEVAL ---")
        historical_context = historical_mgr.format_context_for_prompt(
            processed_query['topic'],
            limit=3
        )
        log("HISTORICAL", f"Retrieved context length: {len(historical_context)} chars")
        if len(historical_context) > 200:
            log("HISTORICAL", f"Context preview: {historical_context[:200]}...")
        
        # Create context
        canonical_input = processed_query['canonical']
        context = AgentContext(
            user_input=canonical_input,
            session_id=None,
            dispatcher=multi_mcp,
            mcp_server_descriptions=mcp_servers,
        )
        context.processed_query = processed_query
        context.historical_context = historical_context
        
        # Run agent loop
        log("PHASE3", "--- STEP 4: AGENT LOOP EXECUTION ---")
        agent = AgentLoop(context)
        
        result = await agent.run()
        
        # Extract answer
        if isinstance(result, dict):
            answer = result["result"]
            
            # Postprocessing
            log("PHASE3", "--- STEP 5: RESULT POSTPROCESSING ---")
            post_result = postprocess_result(result, answer)
            log("HEURISTICS", f"Confidence Score: {post_result['confidence']['score']:.2f}")
            log("HEURISTICS", f"Is Incomplete: {post_result['is_incomplete']}")
            log("HEURISTICS", f"Sanitized Output: {post_result['sanitized_output'][:200]}...")
            
            # Extract final answer
            if "FINAL_ANSWER:" in answer:
                final_answer = answer.split('FINAL_ANSWER:')[1].strip()
                log("PHASE3", "--- STEP 6: FINAL ANSWER ---")
                log("RESULT", f"FINAL_ANSWER: {final_answer}")
                
                # Store in historical context
                is_error = (
                    "error" in final_answer.lower() or 
                    "ERROR" in final_answer or
                    "An error occurred" in final_answer
                )
                
                if not is_error:
                    historical_mgr.add_conversation(
                        query=query,
                        query_hash=processed_query['query_hash'],
                        topic=processed_query['topic'],
                        result=final_answer,
                        session_id=context.session_id,
                        success=True,
                        metadata={
                            "query_type": processed_query['query_type'],
                            "confidence": post_result['confidence']['score'],
                            "entities": processed_query['entities']
                        }
                    )
                    log("HISTORICAL", "Conversation stored successfully")
            else:
                log("RESULT", f"Answer: {answer}")
        else:
            log("RESULT", f"Unexpected result format: {result}")
        
        log("PHASE3", f"=== QUERY {query_num} COMPLETE ===")
        
        return log_buffer
        
    except Exception as e:
        log("ERROR", f"Exception occurred: {str(e)}")
        import traceback
        log("ERROR", f"Traceback: {traceback.format_exc()}")
        return log_buffer

async def main():
    """Run 3 brand-new unique queries"""
    
    # 3 brand-new queries (not in original agent.py)
    queries = [
        "What is the relationship between Tesla Motors and open innovation according to the documents?",
        "Calculate the factorial of 7 and then find the square root of that result",
        "Summarize the key points about Canvas LMS from the stored documents"
    ]
    
    print("\n" + "="*70)
    print("PHASE 3: STEP 5 - EXECUTING 3 BRAND-NEW UNIQUE QUERIES")
    print("="*70)
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"QUERY {i}/3: {query}")
        print(f"{'='*70}\n")
        
        log_entries = await run_query_with_logging(query, i)
        
        # Save log to file
        log_file = logs_dir / f"Phase3_Query_{i}_Log.md"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"# Phase 3: Query {i} - Complete Log\n\n")
            f.write(f"**Query:** {query}\n\n")
            f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write("## Complete Execution Log\n\n")
            f.write("```\n")
            f.write("\n".join(log_entries))
            f.write("\n```\n")
        
        print(f"\n[SUCCESS] Log saved to: {log_file}")
    
    print(f"\n{'='*70}")
    print("PHASE 3: STEP 5 COMPLETE")
    print(f"{'='*70}")
    print(f"\nGenerated log files:")
    for i in range(1, 4):
        log_file = logs_dir / f"Phase3_Query_{i}_Log.md"
        if log_file.exists():
            print(f"  ✓ {log_file}")
    
    print(f"\nAll logs saved to: {logs_dir.absolute()}")

if __name__ == "__main__":
    asyncio.run(main())

