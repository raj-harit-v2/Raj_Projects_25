"""
Clear error entries from historical conversation cache
"""

import json
from pathlib import Path

def clear_error_entries():
    """Remove cached error results from historical_conversation_store.json"""
    
    store_path = Path("historical_conversation_store.json")
    
    if not store_path.exists():
        print("[INFO] No historical store found - nothing to clear")
        return
    
    # Load store
    with open(store_path, 'r', encoding='utf-8') as f:
        store = json.load(f)
    
    error_keywords = [
        "error", "ERROR", "An error occurred", 
        "Expecting value", "failed", "Failed"
    ]
    
    removed_count = 0
    
    # Check all topics
    for topic in store.get("topics", {}):
        conversations = store["topics"][topic]["conversations"]
        
        # Filter out error conversations
        original_count = len(conversations)
        store["topics"][topic]["conversations"] = [
            conv for conv in conversations
            if not any(
                keyword in str(conv.get("result_summary", "")).lower() 
                or keyword in str(conv.get("result", "")).lower()
                for keyword in error_keywords
            )
        ]
        
        removed = original_count - len(store["topics"][topic]["conversations"])
        removed_count += removed
        
        if removed > 0:
            print(f"[CLEARED] {removed} error entries from topic '{topic}'")
    
    # Also clean up hash index
    hash_index = store.get("index", {}).get("by_hash", {})
    original_hash_count = len(hash_index)
    
    # Remove hashes that point to error conversations
    hashes_to_remove = []
    for query_hash, entry in hash_index.items():
        topic = entry.get("topic", "")
        if topic in store.get("topics", {}):
            # Check if conversation still exists
            conversations = store["topics"][topic]["conversations"]
            found = any(
                conv.get("query_hash") == query_hash 
                for conv in conversations
            )
            if not found:
                hashes_to_remove.append(query_hash)
    
    for hash_key in hashes_to_remove:
        del hash_index[hash_key]
    
    if hashes_to_remove:
        print(f"[CLEARED] {len(hashes_to_remove)} error hash entries")
    
    # Update metadata
    store["metadata"]["total_conversations"] = sum(
        len(store["topics"][t]["conversations"]) 
        for t in store["topics"]
    )
    
    # Save
    with open(store_path, 'w', encoding='utf-8') as f:
        json.dump(store, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SUCCESS] Removed {removed_count} error entries from cache")
    print(f"[INFO] Total conversations remaining: {store['metadata']['total_conversations']}")

if __name__ == "__main__":
    print("Clearing error entries from cache...")
    clear_error_entries()
    print("\nDone! You can now run queries without hitting cached errors.")

