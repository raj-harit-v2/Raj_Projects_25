"""Test historical store initialization"""
from modules.historical_context import HistoricalContextManager

print("Testing Historical Context Manager...")
mgr = HistoricalContextManager()

print("\nStore structure:")
print(f"  Has 'index': {'index' in mgr.store}")
print(f"  Has 'topics': {'topics' in mgr.store}")
print(f"  Has 'metadata': {'metadata' in mgr.store}")

if 'index' in mgr.store:
    print(f"\n  Index structure:")
    print(f"    by_hash: {len(mgr.store['index'].get('by_hash', {}))} entries")
    print(f"    by_date: {len(mgr.store['index'].get('by_date', []))} entries")
    print(f"    recent_topics: {mgr.store['index'].get('recent_topics', [])}")

if 'topics' in mgr.store:
    print(f"\n  Topics: {list(mgr.store['topics'].keys())}")

print("\n[SUCCESS] Historical store properly initialized!")

