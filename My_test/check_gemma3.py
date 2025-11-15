"""Check if gemma3:12b is available"""
import requests

try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        data = response.json()
        models = [m.get('name', '') for m in data.get('models', [])]
        print("Available Ollama models:")
        for model in models:
            print(f"  - {model}")
        
        has_gemma3 = any('gemma3' in m.lower() for m in models)
        print(f"\nHas gemma3 model: {has_gemma3}")
        
        if not has_gemma3:
            print("\n[WARNING] gemma3:12b not found!")
            print("To install: ollama pull gemma3:12b")
        else:
            print("\n[OK] gemma3 model is available")
    else:
        print(f"[ERROR] Ollama returned status {response.status_code}")
except Exception as e:
    print(f"[ERROR] Could not check Ollama: {e}")

