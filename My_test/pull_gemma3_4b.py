"""Pull gemma3:4b model using Ollama API"""
import requests
import json

print("Pulling gemma3:4b model...")
print("This may take several minutes depending on your internet speed...")

url = "http://localhost:11434/api/pull"
payload = {
    "name": "gemma3:4b",
    "stream": False
}

try:
    response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
    if response.status_code == 200:
        print("\n[SUCCESS] gemma3:4b model pulled successfully!")
        print("\nYou can now use gemma3:4b in profiles.yaml")
    else:
        print(f"\n[ERROR] Failed to pull model. Status: {response.status_code}")
        print(response.text)
except requests.exceptions.Timeout:
    print("\n[WARNING] Request timed out. The model may still be downloading.")
    print("Check Ollama logs or try again later.")
except Exception as e:
    print(f"\n[ERROR] Failed to pull model: {e}")

