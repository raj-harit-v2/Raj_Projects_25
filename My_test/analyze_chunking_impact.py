"""Analyze impact of chunking parameter changes"""

# Current settings
CURRENT_CHUNK_SIZE = 512  # words
CURRENT_CHUNK_OVERLAP = 30  # words
CURRENT_MAX_CHUNK_LENGTH = 1000  # characters

# Proposed settings
PROPOSED_CHUNK_SIZE = 512  # words (unchanged)
PROPOSED_CHUNK_OVERLAP = 60  # words (doubled)
PROPOSED_MAX_CHUNK_LENGTH = 200  # characters (reduced by 80%)

# Calculate chunking behavior
def analyze_chunking():
    print("="*70)
    print("CHUNKING PARAMETER IMPACT ANALYSIS")
    print("="*70)
    
    print("\nCURRENT SETTINGS:")
    print(f"  CHUNK_SIZE: {CURRENT_CHUNK_SIZE} words")
    print(f"  CHUNK_OVERLAP: {CURRENT_CHUNK_OVERLAP} words")
    print(f"  MAX_CHUNK_LENGTH: {CURRENT_MAX_CHUNK_LENGTH} characters")
    
    print("\nPROPOSED SETTINGS:")
    print(f"  CHUNK_SIZE: {PROPOSED_CHUNK_SIZE} words (unchanged)")
    print(f"  CHUNK_OVERLAP: {PROPOSED_CHUNK_OVERLAP} words (2x increase)")
    print(f"  MAX_CHUNK_LENGTH: {PROPOSED_MAX_CHUNK_LENGTH} characters (80% reduction)")
    
    # Calculate step size (how many words between chunk starts)
    current_step = CURRENT_CHUNK_SIZE - CURRENT_CHUNK_OVERLAP
    proposed_step = PROPOSED_CHUNK_SIZE - PROPOSED_CHUNK_OVERLAP
    
    print("\n" + "="*70)
    print("IMPACT ANALYSIS")
    print("="*70)
    
    print("\n1. CHUNK_OVERLAP: 30 -> 60 (DOUBLE)")
    print(f"   Current step size: {current_step} words between chunk starts")
    print(f"   Proposed step size: {proposed_step} words between chunk starts")
    print(f"   Change: {((proposed_step - current_step) / current_step * 100):.1f}% reduction in step size")
    print("\n   Effects:")
    print("   [PRO] More context preserved across chunk boundaries")
    print("   [PRO] Less likely to split related information")
    print("   [PRO] Better for queries spanning multiple chunks")
    print("   [CON] More redundant chunks (60 words overlap vs 30)")
    print("   [CON] More chunks generated (smaller step size)")
    print("   [CON] Larger index size (~25% more chunks)")
    print("   [CON] Slightly slower indexing")
    
    print("\n2. MAX_CHUNK_LENGTH: 1000 -> 200 characters (80% REDUCTION)")
    print("   [WARNING] This is a MASSIVE reduction!")
    print("   Current: ~300 words per chunk (1000 chars / ~3.3 chars per word)")
    print("   Proposed: ~60 words per chunk (200 chars / ~3.3 chars per word)")
    print("\n   Effects:")
    print("   [CON] Chunks will be VERY small (60 words = ~2-3 sentences)")
    print("   [CON] Context will be severely fragmented")
    print("   [CON] Information might be split mid-sentence")
    print("   [CON] Much harder to find complete answers")
    print("   [CON] Many more chunks (5x increase)")
    print("   [CON] Much larger index (5x size)")
    print("   [CON] Slower searches (more chunks to compare)")
    print("   [CON] Lower quality embeddings (too little context)")
    print("   [NOTE] MAX_CHUNK_LENGTH may not be actively used in chunk_text()")
    
    # Estimate chunk counts
    sample_doc_words = 10000
    current_chunks = (sample_doc_words // current_step) + 1
    proposed_chunks = (sample_doc_words // proposed_step) + 1
    
    print("\n" + "="*70)
    print("ESTIMATED IMPACT (10,000 word document)")
    print("="*70)
    print(f"Current chunks: ~{current_chunks}")
    print(f"Proposed chunks: ~{proposed_chunks}")
    print(f"Increase: {((proposed_chunks - current_chunks) / current_chunks * 100):.1f}%")
    
    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    print("[NO] DO NOT reduce MAX_CHUNK_LENGTH to 200")
    print("   - Too small for meaningful context")
    print("   - Will fragment information badly")
    print("   - Will create 5x more chunks")
    print("\n[YES] CONSIDER increasing CHUNK_OVERLAP to 60")
    print("   - Better context preservation")
    print("   - Moderate increase in chunks (~25%)")
    print("   - Better for finding information across boundaries")
    print("\n[BETTER ALTERNATIVE]:")
    print("   - Keep CHUNK_SIZE: 512")
    print("   - Increase CHUNK_OVERLAP: 30 -> 60 (or 50)")
    print("   - Keep MAX_CHUNK_LENGTH: 1000 (or increase to 1500)")
    print("   - OR: Increase CHUNK_SIZE to 600-700 for more context")

if __name__ == "__main__":
    analyze_chunking()

