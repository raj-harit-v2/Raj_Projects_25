"""
Test Suite for Heuristics Module (Phase 2.1)
Tests all 10 heuristic functions (H-01 to H-10)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.heuristics import (
    canonicalize_query,
    extract_entities,
    classify_query_type,
    identify_topic,
    suggest_tools,
    validate_json_response,
    extract_answer_confidence,
    detect_incomplete_answer,
    sanitize_output,
    generate_query_hash,
    preprocess_query,
    postprocess_result
)

def test_h01_canonicalize_query():
    """Test H-01: Query Canonicalization"""
    print("\n=== Test H-01: Query Canonicalization ===")
    
    # Test 1: Whitespace normalization
    test1 = canonicalize_query("Calculate   2  +  2")
    assert test1 == "Calculate 2 + 2", f"Failed: {test1}"
    print("[PASS] Whitespace normalization")
    
    # Test 2: Abbreviation expansion
    test2 = canonicalize_query("pls calculate sum")
    assert "please" in test2.lower(), f"Failed: {test2}"
    print("[PASS] Abbreviation expansion (pls -> please)")
    
    # Test 3: Combined
    test3 = canonicalize_query("  pls   tell  me  w/ examples  ")
    assert "please" in test3.lower() and "with" in test3.lower()
    print("[PASS] Combined normalization")
    
    print("[SUCCESS] H-01: All tests passed")


def test_h02_extract_entities():
    """Test H-02: Entity Extraction"""
    print("\n=== Test H-02: Entity Extraction ===")
    
    # Test 1: Names
    test1 = extract_entities("How much did Anmol Singh pay?")
    assert "Anmol Singh" in test1["names"], f"Failed: {test1}"
    print(f"[PASS] Name extraction: {test1['names']}")
    
    # Test 2: Numbers
    test2 = extract_entities("Calculate 42.5 plus 100")
    assert "42.5" in test2["numbers"] and "100" in test2["numbers"]
    print(f"[PASS] Number extraction: {test2['numbers']}")
    
    # Test 3: URLs
    test3 = extract_entities("Summarize https://example.com")
    assert len(test3["urls"]) > 0
    print(f"[PASS] URL extraction: {test3['urls']}")
    
    print("[SUCCESS] H-02: All tests passed")


def test_h03_classify_query_type():
    """Test H-03: Query Type Classification"""
    print("\n=== Test H-03: Query Type Classification ===")
    
    # Test 1: Math query
    test1 = classify_query_type("Calculate factorial of 10")
    assert test1 == "math", f"Expected 'math', got '{test1}'"
    print(f"[PASS] Math classification: {test1}")
    
    # Test 2: Document query
    test2 = classify_query_type("Search documents for payment information")
    assert test2 == "document", f"Expected 'document', got '{test2}'"
    print(f"[PASS] Document classification: {test2}")
    
    # Test 3: Web query
    test3 = classify_query_type("Visit website http://example.com for latest news")
    assert test3 in ["web", "document"], f"Expected 'web' or 'document', got '{test3}'"
    print(f"[PASS] Web classification: {test3}")
    
    # Test 4: Hybrid query
    test4 = classify_query_type("Calculate sum and search documents for information")
    assert test4 in ["hybrid", "document", "math"], f"Expected hybrid/document/math, got '{test4}'"
    print(f"[PASS] Hybrid/mixed classification: {test4}")
    
    print("[SUCCESS] H-03: All tests passed")


def test_h04_identify_topic():
    """Test H-04: Topic Triage"""
    print("\n=== Test H-04: Topic Triage ===")
    
    # Test 1: Mathematics
    test1 = identify_topic("Calculate exponential sum")
    assert test1 == "mathematics", f"Expected 'mathematics', got '{test1}'"
    print(f"[PASS] Mathematics topic: {test1}")
    
    # Test 2: Finance
    test2 = identify_topic("How much money was paid for the apartment purchase?")
    assert test2 in ["finance", "general"], f"Expected 'finance' or 'general', got '{test2}'"
    print(f"[PASS] Finance topic: {test2}")
    
    # Test 3: Education
    test3 = identify_topic("Which course are we teaching on Canvas LMS?")
    assert test3 == "education", f"Expected 'education', got '{test3}'"
    print(f"[PASS] Education topic: {test3}")
    
    print("[SUCCESS] H-04: All tests passed")


def test_h05_suggest_tools():
    """Test H-05: Tool Suggestion"""
    print("\n=== Test H-05: Tool Suggestion ===")
    
    # Test 1: ASCII conversion
    test1 = suggest_tools("Find ASCII values", "math")
    assert "strings_to_chars_to_int" in test1
    print(f"[PASS] ASCII tool suggestion: {test1}")
    
    # Test 2: Document search
    test2 = suggest_tools("Search for payment info", "document")
    assert "search_stored_documents" in test2
    print(f"[PASS] Document search suggestion: {test2}")
    
    print("[SUCCESS] H-05: All tests passed")


def test_h06_validate_json():
    """Test H-06: JSON Validation"""
    print("\n=== Test H-06: JSON Validation ===")
    
    # Test 1: Valid JSON string
    test1 = validate_json_response('{"result": 42}')
    assert test1 == True
    print("[PASS] Valid JSON string")
    
    # Test 2: Valid dict
    test2 = validate_json_response({"result": 42})
    assert test2 == True
    print("[PASS] Valid dict")
    
    # Test 3: Invalid JSON
    test3 = validate_json_response("not json{}")
    assert test3 == False
    print("[PASS] Invalid JSON detection")
    
    print("[SUCCESS] H-06: All tests passed")


def test_h07_confidence_scoring():
    """Test H-07: Confidence Scoring"""
    print("\n=== Test H-07: Confidence Scoring ===")
    
    # Test 1: High confidence
    test1 = extract_answer_confidence("The result is calculated as 42.5678")
    assert test1["score"] >= 0.7, f"Expected high confidence, got {test1['score']}"
    print(f"[PASS] High confidence: {test1['score']:.2f}")
    
    # Test 2: Low confidence
    test2 = extract_answer_confidence("No information found, unclear")
    assert test2["score"] <= 0.4, f"Expected low confidence, got {test2['score']}"
    print(f"[PASS] Low confidence: {test2['score']:.2f}")
    
    print("[SUCCESS] H-07: All tests passed")


def test_h08_incomplete_detection():
    """Test H-08: Incomplete Answer Detection"""
    print("\n=== Test H-08: Incomplete Answer Detection ===")
    
    # Test 1: Incomplete answer
    test1 = detect_incomplete_answer("Step 1 of 3: Found document")
    assert test1 == True
    print("[PASS] Incomplete detection: True")
    
    # Test 2: Complete answer
    test2 = detect_incomplete_answer("The final result is 42")
    assert test2 == False
    print("[PASS] Complete detection: False")
    
    print("[SUCCESS] H-08: All tests passed")


def test_h09_sanitize_output():
    """Test H-09: Output Sanitization"""
    print("\n=== Test H-09: Output Sanitization ===")
    
    # Test 1: Whitespace cleanup
    test1 = sanitize_output("Result   is\n\n\n\n42    ")
    assert "Result is" in test1 and test1.count('\n') <= 2
    print("[PASS] Whitespace sanitization")
    
    # Test 2: Script tag removal
    test2 = sanitize_output("Result <script>alert('xss')</script> is 42")
    assert "<script>" not in test2
    print("[PASS] Script tag removal")
    
    # Test 3: Truncation
    test3 = sanitize_output("x" * 3000)
    assert len(test3) <= 2100  # 2000 + "... [truncated]"
    print(f"[PASS] Truncation: {len(test3)} chars")
    
    print("[SUCCESS] H-09: All tests passed")


def test_h10_query_hashing():
    """Test H-10: Query Hashing"""
    print("\n=== Test H-10: Query Hashing ===")
    
    # Test 1: Hash generation
    test1 = generate_query_hash("Calculate 2 + 2")
    assert len(test1) == 16, f"Expected 16 chars, got {len(test1)}"
    print(f"[PASS] Hash generation: {test1}")
    
    # Test 2: Consistent hashing
    test2a = generate_query_hash("Calculate  2  +  2")
    test2b = generate_query_hash("calculate 2 + 2")
    assert test2a == test2b, "Hashes should be identical after normalization"
    print(f"[PASS] Consistent hashing: {test2a}")
    
    print("[SUCCESS] H-10: All tests passed")


def test_preprocess_pipeline():
    """Test Combined Preprocessing Pipeline"""
    print("\n=== Test Preprocessing Pipeline ===")
    
    query = "Calculate ASCII values of INDIA"
    result = preprocess_query(query)
    
    # Verify all fields present
    assert "canonical" in result
    assert "entities" in result
    assert "query_type" in result
    assert "topic" in result
    assert "query_hash" in result
    assert "suggested_tools" in result
    
    print(f"[PASS] Original: {result['original']}")
    print(f"[PASS] Canonical: {result['canonical']}")
    print(f"[PASS] Query Type: {result['query_type']}")
    print(f"[PASS] Topic: {result['topic']}")
    print(f"[PASS] Hash: {result['query_hash']}")
    print(f"[PASS] Suggested Tools: {result['suggested_tools']}")
    
    print("[SUCCESS] Preprocessing Pipeline: All tests passed")


def test_postprocess_pipeline():
    """Test Combined Postprocessing Pipeline"""
    print("\n=== Test Postprocessing Pipeline ===")
    
    result_text = "FINAL_ANSWER: The calculated result is 42.5"
    result = postprocess_result({"result": 42.5}, result_text)
    
    # Verify all fields present
    assert "is_valid" in result
    assert "confidence" in result
    assert "is_incomplete" in result
    assert "sanitized_output" in result
    
    print(f"[PASS] Is Valid: {result['is_valid']}")
    print(f"[PASS] Confidence: {result['confidence']['score']:.2f}")
    print(f"[PASS] Is Incomplete: {result['is_incomplete']}")
    print(f"[PASS] Sanitized Output: {result['sanitized_output'][:50]}...")
    
    print("[SUCCESS] Postprocessing Pipeline: All tests passed")


def run_all_tests():
    """Run all heuristic tests"""
    print("\n" + "="*60)
    print("  HEURISTICS MODULE TEST SUITE (Phase 2.1)")
    print("="*60)
    
    try:
        test_h01_canonicalize_query()
        test_h02_extract_entities()
        test_h03_classify_query_type()
        test_h04_identify_topic()
        test_h05_suggest_tools()
        test_h06_validate_json()
        test_h07_confidence_scoring()
        test_h08_incomplete_detection()
        test_h09_sanitize_output()
        test_h10_query_hashing()
        test_preprocess_pipeline()
        test_postprocess_pipeline()
        
        print("\n" + "="*60)
        print("  ALL HEURISTICS TESTS PASSED!")
        print("  Status: 10/10 heuristics operational")
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

