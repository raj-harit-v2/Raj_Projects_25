"""Pull llava model via Ollama API"""
import requests
import json

url = "http://localhost:11434/api/pull"
data = {"name": "llava"}

print("Pulling llava model from Ollama...")
print("This may take several minutes depending on your internet connection...")

try:
    response = requests.post(url, json=data, stream=True)
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            try:
                chunk = json.loads(line)
                if "status" in chunk:
                    print(f"Status: {chunk['status']}")
                if "completed" in chunk and "total" in chunk:
                    completed = chunk.get("completed", 0)
                    total = chunk.get("total", 0)
                    if total > 0:
                        percent = (completed / total) * 100
                        print(f"Progress: {percent:.1f}% ({completed}/{total} bytes)")
            except json.JSONDecodeError:
                continue
    
    print("\n[SUCCESS] llava model pulled successfully!")
except requests.exceptions.RequestException as e:
    print(f"[ERROR] Failed to pull model: {e}")
    print("Make sure Ollama is running: curl http://localhost:11434/api/tags")

