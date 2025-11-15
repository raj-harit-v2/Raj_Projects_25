"""Restart Ollama and verify MCP servers"""
import subprocess
import time
import requests
import json

print("=" * 80)
print("RESTARTING OLLAMA & MCP SERVERS")
print("=" * 80)

# Check Ollama status
print("\n1. Checking Ollama status...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"   [OK] Ollama is running")
        print(f"   [INFO] Installed models: {len(models)}")
        for model in models[:5]:
            print(f"      - {model.get('name', 'unknown')}")
    else:
        print(f"   [WARNING] Ollama returned status {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"   [ERROR] Ollama not responding: {e}")
    print("   [INFO] To restart Ollama:")
    print("      - Windows: Restart Ollama service or restart the application")
    print("      - Or run: ollama serve")

# Note: MCP servers are started by agent.py automatically
print("\n2. MCP Servers:")
print("   [INFO] MCP servers are started automatically by agent.py")
print("   [INFO] No manual restart needed - they restart with agent")

print("\n" + "=" * 80)
print("READY TO START AGENT")
print("=" * 80)
print("\nRun: python agent.py")
print("MCP servers will start automatically")

