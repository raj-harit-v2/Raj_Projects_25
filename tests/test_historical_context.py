"""
Test Suite for Historical Context Module (Phase 2.2)
Tests smart historical indexing system
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import time
from modules.historical_context import HistoricalContextManager

def test_initialization():
    """Test Historical Context Manager Initialization"""
    print("\n=== Test: Initialization ===")
    
    mgr = HistoricalContextManager()
    
    # Verify structure
    assert "topics" in mgr.store
    assert "index" in mgr.store
    assert "metadata" in mgr.store
    
    # Verify 7 topics
    topics = mgr.store["topics"]
    expected_topics = ["mathematics", "documents", "finance", "technology", 
                      "web_research", "education", "general"]
    for topic in expected_topics:
        assert topic in topics, f"Missing topic: {topic}"
    
    print(f"[PASS] Initialized with {len(topics)} topics")
    print(f"[PASS] Topics: {list(topics.keys())}")
    print("[SUCCESS] Initialization test passed")


def test_add_conversation():
    """Test Adding Conversations"""
    print("\n=== Test: Add Conversation ===")
    
    mgr = HistoricalContextManager()
    initial_count = mgr.store["metadata"]["total_conversations"]
    
    # Add test conversation
    mgr.add_conversation(
        query="What is 2 + 2?",
        query_hash="test_hash_001",
        topic="mathematics",
        result="FINAL_ANSWER: 4",
        session_id="test_session_001",
        success=True,
        metadata={"test": True}
    )
    
    # Verify storage
    new_count = mgr.store["metadata"]["total_conversations"]
    assert new_count == initial_count + 1, "Count should increase"
    print(f"[PASS] Conversation added: {initial_count} -> {new_count}")
    
    # Verify in topic
    math_convos = mgr.store["topics"]["mathematics"]["conversations"]
    assert len(math_convos) > 0
    print(f"[PASS] Found in mathematics topic: {len(math_convos)} conversations")
    
    # Verify in hash index
    assert "test_hash_001" in mgr.store["index"]["by_hash"]
    print("[PASS] Added to hash index")
    
    print("[SUCCESS] Add conversation test passed")


def test_get_context_by_topic():
    """Test Context Retrieval"""
    print("\n=== Test: Get Context by Topic ===")
    
    mgr = HistoricalContextManager()
    
    # Add multiple test conversations
    for i in range(3):
        mgr.add_conversation(
            query=f"Math query {i}",
            query_hash=f"hash_{i}",
            topic="mathematics",
            result=f"Result {i}",
            session_id=f"session_{i}",
            success=True
        )
    
    # Retrieve context
    context = mgr.get_context_by_topic("mathematics", limit=2)
    
    assert len(context) >= 2, f"Expected at least 2, got {len(context)}"
    print(f"[PASS] Retrieved {len(context)} conversations")
    
    # Verify newest first
    if len(context) >= 2:
        assert context[0]["timestamp"] >= context[1]["timestamp"]
        print("[PASS] Sorted by timestamp (newest first)")
    
    print("[SUCCESS] Context retrieval test passed")


def test_check_duplicate():
    """Test Duplicate Detection (1-hour cache)"""
    print("\n=== Test: Duplicate Detection ===")
    
    mgr = HistoricalContextManager()
    
    # Add recent conversation
    recent_hash = "recent_query_hash"
    mgr.add_conversation(
        query="Recent test query",
        query_hash=recent_hash,
        topic="general",
        result="Test result",
        session_id="test_session",
        success=True
    )
    
    # Check for duplicate (should find it)
    duplicate = mgr.check_duplicate(recent_hash)
    assert duplicate is not None, "Should find recent query"
    print(f"[PASS] Found recent query: {duplicate['query']}")
    
    # Check for non-existent
    no_dup = mgr.check_duplicate("nonexistent_hash")
    assert no_dup is None, "Should not find non-existent query"
    print("[PASS] Non-existent query returns None")
    
    print("[SUCCESS] Duplicate detection test passed")


def test_format_context_for_prompt():
    """Test Context Formatting for LLM"""
    print("\n=== Test: Format Context for Prompt ===")
    
    mgr = HistoricalContextManager()
    
    # Add test conversations
    mgr.add_conversation(
        query="Math query for context",
        query_hash="ctx_hash_1",
        topic="mathematics",
        result="FINAL_ANSWER: 42",
        session_id="ctx_session",
        success=True
    )
    
    # Format context
    formatted = mgr.format_context_for_prompt("mathematics", limit=3)
    
    assert isinstance(formatted, str)
    assert len(formatted) > 0
    print(f"[PASS] Formatted context length: {len(formatted)} chars")
    print(f"[PASS] Context preview:\n{formatted[:200]}...")
    
    # Test empty topic
    empty = mgr.format_context_for_prompt("nonexistent_topic")
    assert "No relevant" in empty or len(mgr.get_context_by_topic("nonexistent_topic")) == 0
    print("[PASS] Empty topic handling")
    
    print("[SUCCESS] Context formatting test passed")


def test_statistics():
    """Test Statistics Tracking"""
    print("\n=== Test: Statistics ===")
    
    mgr = HistoricalContextManager()
    
    # Get stats
    stats = mgr.get_statistics()
    
    assert "total" in stats
    assert "by_topic" in stats
    print(f"[PASS] Total conversations: {stats['total']}")
    print(f"[PASS] By topic: {stats['by_topic']}")
    
    print("[SUCCESS] Statistics test passed")


def run_all_tests():
    """Run all historical context tests"""
    print("\n" + "="*60)
    print("  HISTORICAL CONTEXT MODULE TEST SUITE (Phase 2.2)")
    print("="*60)
    
    try:
        test_initialization()
        test_add_conversation()
        test_get_context_by_topic()
        test_check_duplicate()
        test_format_context_for_prompt()
        test_statistics()
        
        print("\n" + "="*60)
        print("  ALL HISTORICAL CONTEXT TESTS PASSED!")
        print("  Status: Historical indexing system operational")
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

