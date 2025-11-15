# Gemini Model Switching Guide

## Current Configuration

### When GEMINI_API_KEY is used:
- **Model**: `gemini-2.0-flash` (configured in `config/models.json`)
- **Type**: Google Gemini API (cloud-based)
- **Cost**: Higher cost, subject to rate limits

## Model Options

### 1. **Gemini Models (Cloud - API Key Required)**

#### A. `gemini-2.0-flash` (Current Default)
- **Cost**: Higher
- **Rate Limits**: Yes (15 requests/minute free tier)
- **Best For**: High-quality responses, complex tasks

#### B. `gemini-2.0-flash-lite` (NEW - Lower Cost)
- **Cost**: Much lower
  - Input: $0.075 per 1M tokens
  - Output: $0.30 per 1M tokens
- **Rate Limits**: Yes (but higher limits)
- **Best For**: Cost-effective, large-scale usage
- **Configuration**: Added as `gemini-lite` in `config/models.json`

### 2. **Ollama Models (Local - FREE, No Rate Limits)** ⭐ RECOMMENDED

#### A. `phi4` (Currently Available)
- **Cost**: FREE (runs locally)
- **Rate Limits**: NONE
- **Best For**: Avoiding API costs and rate limits

#### B. `gemma2:2b` (Currently Available)
- **Cost**: FREE (runs locally)
- **Rate Limits**: NONE
- **Best For**: Fast, lightweight tasks

#### C. `gemma3:4b` (If Installed)
- **Cost**: FREE (runs locally)
- **Rate Limits**: NONE
- **Best For**: Better quality than gemma2:2b

## How to Switch Models

### Option 1: Switch to Lower-Cost Gemini Model

Edit `config/profiles.yaml`:
```yaml
llm:
  text_generation: gemini-lite  # Instead of "gemini"
```

### Option 2: Switch to FREE Ollama Model (RECOMMENDED)

Edit `config/profiles.yaml`:
```yaml
llm:
  text_generation: phi4  # or gemma2:2b, gemma3:4b
```

**Benefits:**
- ✅ FREE (no API costs)
- ✅ NO rate limits
- ✅ Runs locally (privacy)
- ✅ Always available

## Rate Limit Solutions

### Problem: Gemini API Rate Limits
- Free tier: ~15 requests/minute
- Paid tier: Higher limits but still subject to quotas

### Solutions:

1. **Use Ollama (Best Solution)** ⭐
   - Switch to `phi4`, `gemma2:2b`, or `gemma3:4b`
   - No rate limits, no costs
   - Already configured and available

2. **Use Gemini Lite**
   - Switch to `gemini-lite` (lower cost, higher limits)
   - Still subject to rate limits but more affordable

3. **Implement Retry Logic** (Already in code)
   - `modules/model_manager.py` has retry logic with exponential backoff
   - Automatically retries on 429 errors

4. **Reduce Request Frequency**
   - Use caching (historical context)
   - Batch requests when possible

## Current Status

- **Active Model**: `gemma3:4b` (Ollama - local)
- **Gemini Model**: `gemini-2.0-flash` (if switched to "gemini")
- **Available Ollama Models**: `phi4`, `gemma2:2b`, `llava`, `nomic-embed-text`

## Recommendation

**Use Ollama models (`phi4` or `gemma2:2b`) to:**
- ✅ Avoid all API costs
- ✅ Avoid all rate limits
- ✅ Maintain privacy (local processing)
- ✅ Have unlimited usage

Switch in `config/profiles.yaml`:
```yaml
llm:
  text_generation: phi4  # or gemma2:2b
```

