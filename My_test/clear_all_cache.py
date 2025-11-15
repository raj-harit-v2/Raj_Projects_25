"""Clear all caches before running agent"""
import json
from pathlib import Path

print("=" * 80)
print("CLEARING ALL CACHES")
print("=" * 80)

# 1. Clear historical conversation cache
historical_file = Path("historical_conversation_store.json")
if historical_file.exists():
    historical_file.write_text(json.dumps({}, indent=2))
    print("[OK] Cleared historical_conversation_store.json")
else:
    print("[SKIP] historical_conversation_store.json not found")

# 2. Clear document index cache (keeps the index, just forces reprocessing)
doc_cache = Path("faiss_index/doc_index_cache.json")
if doc_cache.exists():
    doc_cache.write_text(json.dumps({}, indent=2))
    print("[OK] Cleared faiss_index/doc_index_cache.json")
else:
    print("[SKIP] doc_index_cache.json not found")

# 3. Memory files - ask user or just clear
memory_dir = Path("memory")
if memory_dir.exists():
    # Count files
    memory_files = list(memory_dir.rglob("*.json"))
    if memory_files:
        print(f"[INFO] Found {len(memory_files)} memory files in memory/ directory")
        print("[INFO] Memory files kept (session history)")
        print("[INFO] To clear memory, delete the 'memory' directory manually")
    else:
        print("[SKIP] No memory files found")

print("\n" + "=" * 80)
print("CACHE CLEARED - Ready to run agent")
print("=" * 80)
print("\nNote: FAISS index (index.bin, metadata.json) is kept intact")
print("      Only the document processing cache was cleared")
print("\nRun: python agent.py")

