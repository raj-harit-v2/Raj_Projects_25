# Fix: Rate Limits, Image Captioning, and Search Strategy

## Issues Identified

1. **Rate Limit Errors (429)**: Google Gemini API has a 15 requests/minute limit for free tier, causing repeated failures
2. **Image Captioning Failure**: Canvas LMS PDF images are returning "[No caption returned]" - all captions failed
3. **Search Strategy**: Agent not prioritizing document search before web search

## Fixes Applied

### 1. Rate Limit Handling (`modules/model_manager.py`)

**Added retry logic with exponential backoff:**
- Detects 429 errors (rate limit exceeded)
- Retries up to 3 times with increasing delays (2s, 4s, 8s)
- Extracts suggested retry delay from error message if available
- Provides clear error messages if all retries fail

**Code changes:**
```python
def _gemini_generate(self, prompt: str) -> str:
    import time
    max_retries = 3
    base_delay = 2  # Start with 2 seconds
    
    for attempt in range(max_retries):
        try:
            response = self.client.models.generate_content(...)
            # ... extract response ...
        except Exception as e:
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
                    continue
```

### 2. Search Strategy (`prompts/New_Decision_Prompt.txt`)

**Updated prompt to prioritize documents first:**
- Added "SEARCH STRATEGY (CRITICAL)" section at the top
- Clear instructions: Documents FIRST, then web search
- Updated document query example to show proper flow
- Emphasized that image captions are searchable

**Key changes:**
```
# SEARCH STRATEGY (CRITICAL)
ALWAYS follow this order:
1. **FIRST**: Search stored documents using `search_stored_documents` (includes PDFs with image captions)
2. **THEN**: Only if documents don't have the answer, try web search using `duckduckgo_search_results`
3. Documents contain image captions stored as "**Image:** {caption}" - these are fully searchable
```

### 3. Image Captioning Error Handling (`mcp_server_2.py`)

**Improved error handling and logging:**
- Better error messages when captioning fails
- HTTP error detection and reporting
- More detailed logging for debugging

**Issue discovered:**
- Canvas LMS PDF has 1 chunk with 20+ images
- All images returned "[No caption returned]"
- This suggests `gemma2:2b` may not support vision properly, or images aren't being processed correctly

**Current status:**
- Canvas LMS PDF is indexed (1 chunk)
- But all image captions failed
- The chunk contains: `**Image:** [No caption returned]` repeated 20+ times

## Root Cause Analysis

### Canvas LMS PDF Issue

**Problem:**
- PDF is mostly images (screenshots/tutorials)
- Image captioning is failing for all images
- Search query "course Canvas LMS teaching" doesn't match because:
  - No actual text content in the PDF
  - Image captions are all "[No caption returned]"
  - The chunk only contains failed caption placeholders

**Possible causes:**
1. `gemma2:2b` may not be a vision model (or vision support is limited)
2. Image format/encoding issues
3. Ollama vision API not working correctly
4. Images too large or in unsupported format

**Recommendations:**
1. Try a dedicated vision model like `llava` or `llava2`
2. Check if images are being extracted correctly from PDF
3. Verify Ollama vision API is working: `curl http://localhost:11434/api/generate -d '{"model": "gemma2:2b", "prompt": "test", "images": ["base64..."]}'`
4. Consider OCR for text-heavy images

## Testing

### Rate Limit Fix
- Test with multiple rapid queries
- Should see retry messages: `[model_manager] Rate limit hit (429), waiting X.Xs before retry...`
- Should eventually succeed or provide clear error after 3 retries

### Search Strategy
- Query: "which course are we teaching on Canvas LMS?"
- Should search documents first
- Only try web if documents don't have answer
- Check logs for tool call order

### Image Captioning
- Check `faiss_index/metadata.json` for Canvas LMS chunks
- Verify if any captions succeeded
- Check Ollama logs for vision API errors

## Next Steps

1. **For Canvas LMS PDF:**
   - Install a proper vision model: `ollama pull llava` or `ollama pull llava2`
   - Update `GEMMA_MODEL` in `mcp_server_2.py` to use vision model
   - Rebuild index: `python mcp_server_2.py index`

2. **For Rate Limits:**
   - Consider switching to Ollama for text generation (no rate limits)
   - Or upgrade Gemini API tier
   - Or implement request queuing/throttling

3. **For Search:**
   - Test with queries that should find document content
   - Verify staged query examples work correctly
   - Monitor tool call order in logs

## Files Modified

1. `modules/model_manager.py` - Added retry logic for 429 errors
2. `prompts/New_Decision_Prompt.txt` - Updated search strategy and examples
3. `mcp_server_2.py` - Improved image captioning error handling

## Verification Commands

```bash
# Check Canvas LMS chunks
python check_canvas_chunks.py

# Check all documents in index
python -c "import json; from pathlib import Path; data = json.loads(Path('faiss_index/metadata.json').read_text()); docs = set(c['doc'] for c in data); print('\n'.join(sorted(docs)))"

# Test rate limit handling (run multiple queries rapidly)
# Should see retry messages in logs
```

