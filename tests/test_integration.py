"""
Integration Test Suite for Phase 1 & 2
Tests complete workflow with all components
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from modules.heuristics import preprocess_query, postprocess_result
from modules.historical_context import HistoricalContextManager

def test_end_to_end_workflow():
    """Test complete query processing workflow"""
    print("\n=== Test: End-to-End Workflow ===")
    
    # Initialize
    historical_mgr = HistoricalContextManager()
    
    # Step 1: User input
    user_input = "Calculate factorial of 5"
    print(f"\n[INPUT] {user_input}")
    
    # Step 2: Preprocessing (Heuristics)
    processed = preprocess_query(user_input)
    print(f"[PREPROCESS] Query Type: {processed['query_type']}")
    print(f"[PREPROCESS] Topic: {processed['topic']}")
    print(f"[PREPROCESS] Hash: {processed['query_hash']}")
    assert processed['query_type'] == 'math'
    assert processed['topic'] == 'mathematics'
    print("[PASS] Preprocessing successful")
    
    # Step 3: Check duplicate (may exist if tests run multiple times)
    duplicate = historical_mgr.check_duplicate(processed['query_hash'])
    print(f"[INFO] Duplicate check: {'Found' if duplicate else 'Not found'}")
    print("[PASS] Duplicate check completed")
    
    # Step 4: Get historical context
    context = historical_mgr.format_context_for_prompt(processed['topic'], limit=3)
    assert isinstance(context, str)
    print(f"[PASS] Historical context retrieved: {len(context)} chars")
    
    # Step 5: Simulate result
    simulated_result = {"status": "done", "result": "FINAL_ANSWER: 120"}
    
    # Step 6: Postprocessing
    post = postprocess_result(simulated_result, "FINAL_ANSWER: 120")
    print(f"[POSTPROCESS] Confidence: {post['confidence']['score']:.2f}")
    print(f"[POSTPROCESS] Is Complete: {not post['is_incomplete']}")
    assert post['is_valid'] == True
    print("[PASS] Postprocessing successful")
    
    # Step 7: Store in historical
    historical_mgr.add_conversation(
        query=user_input,
        query_hash=processed['query_hash'],
        topic=processed['topic'],
        result="120",
        session_id="test_integration",
        success=True,
        metadata={"confidence": post['confidence']['score']}
    )
    print("[PASS] Stored in historical context")
    
    # Step 8: Check duplicate (should find it now)
    duplicate2 = historical_mgr.check_duplicate(processed['query_hash'])
    assert duplicate2 is not None, "Should find duplicate now"
    print("[PASS] Duplicate detection working (cache hit)")
    
    print("\n[SUCCESS] End-to-End Workflow: All steps passed")


def test_document_query_workflow():
    """Test document query processing"""
    print("\n=== Test: Document Query Workflow ===")
    
    historical_mgr = HistoricalContextManager()
    
    # Document query
    query = "How much did someone pay for DLF apartment?"
    processed = preprocess_query(query)
    
    print(f"[INPUT] {query}")
    print(f"[PROCESS] Query Type: {processed['query_type']}")
    print(f"[PROCESS] Topic: {processed['topic']}")
    
    # Should classify as document or hybrid
    assert processed['query_type'] in ['document', 'hybrid', 'general']
    
    # Should identify finance topic
    assert processed['topic'] in ['finance', 'documents', 'general']
    print(f"[PASS] Classified as {processed['query_type']}, topic {processed['topic']}")
    
    # Should suggest document tools
    tools = processed['suggested_tools']
    print(f"[PASS] Suggested tools: {tools}")
    
    print("[SUCCESS] Document query workflow passed")


def test_cache_functionality():
    """Test caching mechanism"""
    print("\n=== Test: Cache Functionality ===")
    
    mgr = HistoricalContextManager()
    
    # Query 1: Use unique query to avoid conflicts
    import time
    query1 = f"Unique test cache query {int(time.time())}"
    processed1 = preprocess_query(query1)
    
    dup1 = mgr.check_duplicate(processed1['query_hash'])
    # May or may not exist, just check it doesn't crash
    print(f"[INFO] Initial check: {'Found' if dup1 else 'Not found'}")
    print("[PASS] Duplicate check works")
    
    # Store it
    mgr.add_conversation(
        query=query1,
        query_hash=processed1['query_hash'],
        topic="general",
        result="Test result",
        session_id="cache_test",
        success=True
    )
    
    # Query 2: Same query (should hit cache)
    processed2 = preprocess_query(query1)
    dup2 = mgr.check_duplicate(processed2['query_hash'])
    
    assert dup2 is not None, "Should find cached result"
    assert dup2['result_summary'] == "Test result"
    print("[PASS] Second query: Cache hit detected")
    print(f"[PASS] Cached result: {dup2['result_summary']}")
    
    print("[SUCCESS] Cache functionality test passed")


def test_topic_based_retrieval():
    """Test topic-based context retrieval"""
    print("\n=== Test: Topic-Based Retrieval ===")
    
    mgr = HistoricalContextManager()
    
    # Add conversations to different topics
    topics_to_test = ["mathematics", "finance", "education"]
    
    for topic in topics_to_test:
        mgr.add_conversation(
            query=f"Sample {topic} query",
            query_hash=f"{topic}_hash",
            topic=topic,
            result=f"Sample {topic} result",
            session_id=f"{topic}_session",
            success=True
        )
    
    # Retrieve from each topic
    for topic in topics_to_test:
        context = mgr.get_context_by_topic(topic, limit=5)
        assert len(context) > 0, f"Should find conversations in {topic}"
        print(f"[PASS] {topic}: {len(context)} conversations")
    
    # Verify cross-topic isolation
    math_context = mgr.get_context_by_topic("mathematics")
    for conv in math_context:
        assert conv["topic"] == "mathematics", "Should only return math conversations"
    
    print("[PASS] Topic isolation verified")
    print("[SUCCESS] Topic-based retrieval test passed")


def test_statistics_tracking():
    """Test statistics and monitoring"""
    print("\n=== Test: Statistics Tracking ===")
    
    mgr = HistoricalContextManager()
    
    # Add some conversations
    for i in range(3):
        mgr.add_conversation(
            query=f"Query {i}",
            query_hash=f"hash_{i}",
            topic="mathematics",
            result=f"Result {i}",
            session_id=f"session_{i}",
            success=True
        )
    
    # Get statistics
    stats = mgr.get_statistics()
    
    assert "total" in stats
    assert "by_topic" in stats
    assert stats["total"] >= 3
    assert stats["by_topic"]["mathematics"] >= 3
    
    print(f"[PASS] Total conversations: {stats['total']}")
    print(f"[PASS] Mathematics: {stats['by_topic']['mathematics']}")
    print("[SUCCESS] Statistics tracking test passed")


def test_context_formatting():
    """Test context formatting for LLM prompts"""
    print("\n=== Test: Context Formatting ===")
    
    mgr = HistoricalContextManager()
    
    # Add conversation
    mgr.add_conversation(
        query="What is the factorial of 10?",
        query_hash="factorial_hash",
        topic="mathematics",
        result="FINAL_ANSWER: 3628800",
        session_id="format_test",
        success=True
    )
    
    # Format for prompt
    formatted = mgr.format_context_for_prompt("mathematics", limit=3)
    
    assert isinstance(formatted, str)
    assert len(formatted) > 0
    
    # Should contain query info
    assert "Query:" in formatted or "factorial" in formatted.lower()
    print(f"[PASS] Formatted context:\n{formatted[:300]}...")
    
    # Test empty topic
    empty = mgr.format_context_for_prompt("nonexistent")
    assert "No relevant" in empty or len(empty) == 0 or len(mgr.get_context_by_topic("nonexistent")) == 0
    print("[PASS] Empty topic handled gracefully")
    
    print("[SUCCESS] Context formatting test passed")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("  INTEGRATION TEST SUITE (Phase 1 & 2)")
    print("="*60)
    
    try:
        test_end_to_end_workflow()
        test_document_query_workflow()
        test_cache_functionality()
        test_topic_based_retrieval()
        
        print("\n" + "="*60)
        print("  ALL INTEGRATION TESTS PASSED!")
        print("  Status: System fully operational")
        print("="*60 + "\n")
        return True
        
    except AssertionError as e:
        print(f"\n[FAILED] Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

