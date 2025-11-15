# modules/heuristics.py
"""
Heuristic rules for query preprocessing and result validation.
Implements 10 heuristic functions to improve agent reliability.
"""

import re
import json
import hashlib
from typing import Dict, Any, List, Optional

# ==================== Query Pre-processing Heuristics ====================

def canonicalize_query(query: str) -> str:
    """
    H-01: Query Canonicalization
    Normalizes query format for better processing.
    """
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    
    # Standardize common abbreviations
    replacements = {
        r'\bpls\b': 'please',
        r'\bu\b': 'you',
        r'\br\b': 'are',
        r'\bw/': 'with',
        r'\bw/o': 'without',
    }
    
    for pattern, replacement in replacements.items():
        query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)
    
    return query


def extract_entities(query: str) -> Dict[str, List[str]]:
    """
    H-02: Entity Extraction
    Identifies key entities (numbers, names, dates) in query.
    """
    entities = {
        "numbers": [],
        "names": [],
        "dates": [],
        "urls": []
    }
    
    # Extract numbers
    entities["numbers"] = re.findall(r'\b\d+(?:\.\d+)?\b', query)
    
    # Extract potential names (capitalized words)
    entities["names"] = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
    
    # Extract dates
    entities["dates"] = re.findall(
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
        query,
        re.IGNORECASE
    )
    
    # Extract URLs
    entities["urls"] = re.findall(r'https?://[^\s]+', query)
    
    return entities


def classify_query_type(query: str) -> str:
    """
    H-03: Query Type Classification
    Categorizes query into: math, document, web, code, or hybrid.
    """
    query_lower = query.lower()
    
    # Math indicators
    math_keywords = ['calculate', 'compute', 'sum', 'multiply', 'divide', 'factorial', 
                     'ascii', 'exponential', 'log', 'sqrt', 'power']
    
    # Document indicators
    doc_keywords = ['document', 'pdf', 'file', 'search', 'find in', 'what does',
                   'who is', 'relationship', 'information about']
    
    # Web indicators
    web_keywords = ['http', 'url', 'website', 'webpage', 'search web', 'online']
    
    # Code indicators
    code_keywords = ['execute', 'run python', 'shell command', 'sql query']
    
    scores = {
        "math": sum(1 for kw in math_keywords if kw in query_lower),
        "document": sum(1 for kw in doc_keywords if kw in query_lower),
        "web": sum(1 for kw in web_keywords if kw in query_lower),
        "code": sum(1 for kw in code_keywords if kw in query_lower)
    }
    
    # Check if hybrid (multiple high scores)
    high_scores = [k for k, v in scores.items() if v >= 2]
    if len(high_scores) > 1:
        return "hybrid"
    
    # Return highest score or default
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "general"


def identify_topic(query: str) -> str:
    """
    H-04: Topic Triage
    Maps query to a domain topic for historical context lookup.
    """
    query_lower = query.lower()
    
    # Define topic keywords
    topics = {
        "mathematics": ['calculate', 'compute', 'math', 'arithmetic', 'algebra', 'factorial', 'exponential'],
        "documents": ['document', 'pdf', 'file', 'paper', 'report', 'invoice'],
        "finance": ['payment', 'paid', 'cost', 'price', 'money', 'amount', 'financial'],
        "technology": ['code', 'programming', 'software', 'api', 'database', 'system'],
        "web_research": ['website', 'url', 'search', 'online', 'internet', 'web'],
        "education": ['course', 'teaching', 'learning', 'canvas', 'lms', 'student'],
        "general": []
    }
    
    # Score each topic
    scores = {}
    for topic, keywords in topics.items():
        scores[topic] = sum(1 for kw in keywords if kw in query_lower)
    
    # Return highest scoring topic (excluding general)
    best_topic = max((k for k in scores if k != "general"), key=scores.get, default="general")
    
    return best_topic if scores.get(best_topic, 0) > 0 else "general"


def suggest_tools(query: str, query_type: str) -> List[str]:
    """
    H-05: Tool Suggestion
    Recommends likely tools based on query analysis.
    """
    suggestions = []
    
    query_lower = query.lower()
    
    # Math tools
    if query_type in ["math", "hybrid"]:
        if any(kw in query_lower for kw in ['ascii', 'character', 'string']):
            suggestions.append('strings_to_chars_to_int')
        if any(kw in query_lower for kw in ['exponential', 'exp', 'sum']):
            suggestions.append('int_list_to_exponential_sum')
        if 'log' in query_lower:
            suggestions.append('logarithm')
        if any(kw in query_lower for kw in ['add', 'sum', '+']):
            suggestions.append('add')
        if 'factorial' in query_lower:
            suggestions.append('factorial')
    
    # Document tools
    if query_type in ["document", "hybrid"]:
        if any(kw in query_lower for kw in ['search', 'find', 'what', 'who', 'relationship']):
            suggestions.append('search_stored_documents')
        if 'pdf' in query_lower:
            suggestions.append('extract_pdf')
    
    # Web tools
    if query_type in ["web", "hybrid"]:
        if 'http' in query_lower or 'url' in query_lower:
            suggestions.append('convert_webpage_url_into_markdown')
        if 'search' in query_lower and 'web' in query_lower:
            suggestions.append('duckduckgo_search_results')
    
    return suggestions[:3]  # Return top 3 suggestions


# ==================== Result Post-processing Heuristics ====================

def validate_json_response(result: Any) -> bool:
    """
    H-06: JSON Validation
    Validates that tool response is properly formatted.
    """
    try:
        if isinstance(result, str):
            json.loads(result)
            return True
        elif isinstance(result, dict):
            return True
        elif hasattr(result, 'content'):
            # MCP result format
            if result.content and len(result.content) > 0:
                json.loads(result.content[0].text)
                return True
        return False
    except (json.JSONDecodeError, AttributeError, IndexError):
        return False


def extract_answer_confidence(result: str) -> Dict[str, Any]:
    """
    H-07: Confidence Scoring
    Analyzes result to estimate confidence level.
    """
    confidence = {
        "score": 0.5,  # Default medium confidence
        "indicators": []
    }
    
    result_lower = result.lower()
    
    # High confidence indicators
    if any(phrase in result_lower for phrase in ['found', 'calculated', 'result is', 'equals']):
        confidence["score"] += 0.2
        confidence["indicators"].append("definitive_answer")
    
    # Low confidence indicators
    if any(phrase in result_lower for phrase in ['not found', 'no information', 'unclear', 'possibly']):
        confidence["score"] -= 0.3
        confidence["indicators"].append("uncertain_answer")
    
    # Check for numeric precision
    if re.search(r'\d+\.\d{2,}', result):
        confidence["score"] += 0.1
        confidence["indicators"].append("precise_numeric")
    
    # Cap between 0 and 1
    confidence["score"] = max(0.0, min(1.0, confidence["score"]))
    
    return confidence


def detect_incomplete_answer(result: str) -> bool:
    """
    H-08: Incomplete Answer Detection
    Identifies when result needs further processing.
    """
    incomplete_indicators = [
        'partial',
        'incomplete',
        'need more',
        'requires additional',
        'step 1 of',
        'first, we need',
        'to be continued'
    ]
    
    result_lower = result.lower()
    return any(indicator in result_lower for indicator in incomplete_indicators)


def sanitize_output(result: str) -> str:
    """
    H-09: Output Sanitization
    Cleans result for safe display (removes sensitive patterns).
    """
    # Remove potential code injection patterns
    result = re.sub(r'<script[^>]*>.*?</script>', '', result, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove excessive whitespace
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = re.sub(r' {2,}', ' ', result)
    
    # Truncate if too long (keep first 2000 chars)
    if len(result) > 2000:
        result = result[:2000] + "... [truncated]"
    
    return result.strip()


def generate_query_hash(query: str) -> str:
    """
    H-10: Query Hashing for Deduplication
    Creates unique hash for caching and historical lookup.
    """
    # Normalize query before hashing
    normalized = canonicalize_query(query).lower()
    
    # Create SHA-256 hash
    hash_obj = hashlib.sha256(normalized.encode('utf-8'))
    return hash_obj.hexdigest()[:16]  # Use first 16 chars for brevity


# ==================== Combined Preprocessing Pipeline ====================

def preprocess_query(query: str) -> Dict[str, Any]:
    """
    Combined preprocessing pipeline applying multiple heuristics.
    """
    processed = {
        "original": query,
        "canonical": canonicalize_query(query),
        "entities": extract_entities(query),
        "query_type": classify_query_type(query),
        "topic": identify_topic(query),
        "query_hash": generate_query_hash(query)
    }
    
    # Add tool suggestions
    processed["suggested_tools"] = suggest_tools(
        processed["canonical"],
        processed["query_type"]
    )
    
    return processed


def postprocess_result(result: Any, result_text: str) -> Dict[str, Any]:
    """
    Combined postprocessing pipeline for results.
    """
    processed = {
        "is_valid": validate_json_response(result),
        "confidence": extract_answer_confidence(result_text),
        "is_incomplete": detect_incomplete_answer(result_text),
        "sanitized_output": sanitize_output(result_text)
    }
    
    return processed

