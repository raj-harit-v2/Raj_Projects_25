"""Force rebuild Canvas LMS PDF"""
import json
from pathlib import Path

cache_path = Path('faiss_index/doc_index_cache.json')
if cache_path.exists():
    cache = json.loads(cache_path.read_text())
    if 'How to use Canvas LMS.pdf' in cache:
        del cache['How to use Canvas LMS.pdf']
        cache_path.write_text(json.dumps(cache, indent=2))
        print("Removed Canvas LMS from cache")
    else:
        print("Canvas LMS not in cache (will be processed)")
else:
    print("Cache file not found")

print("\nNow run: python mcp_server_2.py index")

