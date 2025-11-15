"""Check if gemma3:4b is available"""
import requests

try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        data = response.json()
        models = [m.get('name', '') for m in data.get('models', [])]
        print("Available Ollama models:")
        for model in models:
            print(f"  - {model}")
        
        has_gemma3_4b = any('gemma3:4b' in m.lower() or 'gemma3' in m.lower() for m in models)
        print(f"\nHas gemma3:4b model: {has_gemma3_4b}")
        
        if not has_gemma3_4b:
            print("\n[WARNING] gemma3:4b not found!")
            print("To install: ollama pull gemma3:4b")
            print("\nAlternative: Check if 'gemma3' (without tag) is available")
            gemma3_any = [m for m in models if 'gemma3' in m.lower()]
            if gemma3_any:
                print(f"Found gemma3 variants: {gemma3_any}")
        else:
            print("\n[OK] gemma3:4b model is available")
    else:
        print(f"[ERROR] Ollama returned status {response.status_code}")
except Exception as e:
    print(f"[ERROR] Could not check Ollama: {e}")

