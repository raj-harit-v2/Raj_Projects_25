# How to Bypass API Rate Limits

## Current Situation

- **Gemini API**: 15 requests/minute limit (free tier)
- **Rate Limit Errors**: 429 RESOURCE_EXHAUSTED
- **Current Handling**: Retry with exponential backoff (3 retries)

## Solutions

### Option 1: Switch to Ollama (RECOMMENDED - No Rate Limits)

**Best solution** - Run models locally, no API limits!

#### Steps:

1. **Install Ollama model** (if not already installed):
   ```bash
   # Check what's installed
   curl http://localhost:11434/api/tags
   
   # Install a model (e.g., phi4)
   ollama pull phi4
   ```

2. **Update `config/profiles.yaml`**:
   ```yaml
   llm:
     text_generation: phi4  # Change from "gemini" to "phi4"
     embedding: nomic
   ```

3. **Verify `config/models.json`** has Ollama config (already present):
   ```json
   "phi4": {
     "type": "ollama",
     "model": "phi4",
     "url": {
       "generate": "http://localhost:11434/api/generate"
     }
   }
   ```

4. **Restart agent**:
   ```bash
   python agent.py
   ```

**Pros:**
- ✅ No rate limits
- ✅ No API costs
- ✅ Works offline
- ✅ Full control

**Cons:**
- ⚠️ Requires local GPU/RAM
- ⚠️ May be slower than API
- ⚠️ Model quality depends on local model

---

### Option 2: Improve Rate Limit Handling (Keep Gemini)

Enhance the existing retry logic with request queuing.

#### Current Implementation:
- Retries 3 times with exponential backoff
- Extracts retry delay from error message

#### Enhanced Implementation:

Add request queuing to `modules/model_manager.py`:

```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute=15):
        self.requests_per_minute = requests_per_minute
        self.request_times = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = datetime.now()
            # Remove requests older than 1 minute
            while self.request_times and (now - self.request_times[0]).total_seconds() > 60:
                self.request_times.popleft()
            
            # If at limit, wait until we can make another request
            if len(self.request_times) >= self.requests_per_minute:
                wait_time = 60 - (now - self.request_times[0]).total_seconds() + 0.1
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Clean up again after waiting
                    now = datetime.now()
                    while self.request_times and (now - self.request_times[0]).total_seconds() > 60:
                        self.request_times.popleft()
            
            self.request_times.append(now)

# Add to ModelManager class
rate_limiter = RateLimiter(requests_per_minute=15)

def _gemini_generate(self, prompt: str) -> str:
    # Wait for rate limit slot
    asyncio.run(rate_limiter.acquire())
    
    # Then make request (with existing retry logic)
    ...
```

**Pros:**
- ✅ Prevents hitting rate limit proactively
- ✅ Keeps using Gemini API
- ✅ Better than reactive retries

**Cons:**
- ⚠️ Still limited to 15 req/min
- ⚠️ Adds latency (queuing)

---

### Option 3: Upgrade Gemini API Tier

**Paid solution** - Higher rate limits.

1. **Upgrade Google Cloud account**:
   - Go to: https://console.cloud.google.com/
   - Enable billing
   - Upgrade to paid tier

2. **Rate limits increase**:
   - Free tier: 15 requests/minute
   - Paid tier: 60+ requests/minute (varies by tier)

**Pros:**
- ✅ Higher limits
- ✅ Better performance
- ✅ Keep using Gemini

**Cons:**
- ❌ Costs money
- ❌ Still has limits (just higher)

---

### Option 4: Request Throttling (Simple)

Add delays between requests to stay under limit.

#### Simple Implementation:

```python
import time
from datetime import datetime, timedelta

class SimpleThrottle:
    def __init__(self, requests_per_minute=15):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute  # ~4 seconds
        self.last_request = None
    
    def wait_if_needed(self):
        if self.last_request:
            elapsed = (datetime.now() - self.last_request).total_seconds()
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        self.last_request = datetime.now()

# Use in _gemini_generate:
throttle = SimpleThrottle(requests_per_minute=14)  # Stay under 15

def _gemini_generate(self, prompt: str) -> str:
    throttle.wait_if_needed()  # Add this before request
    # ... rest of code
```

**Pros:**
- ✅ Simple to implement
- ✅ Prevents rate limit hits
- ✅ No API changes needed

**Cons:**
- ⚠️ Adds ~4 second delay per request
- ⚠️ Slower overall performance

---

## Recommended Solution

**Switch to Ollama (Option 1)** for best results:

1. ✅ No rate limits
2. ✅ No API costs
3. ✅ Better for development/testing
4. ✅ Already configured in your system

### Quick Switch:

```bash
# 1. Edit config/profiles.yaml
# Change line 24: text_generation: phi4  (or gemma2:2b)

# 2. Restart agent
python agent.py
```

---

## Implementation: Enhanced Rate Limiting

If you want to keep Gemini but improve handling, I can implement Option 2 (request queuing) or Option 4 (throttling).

Which option would you like me to implement?

