#!/usr/bin/env python3
"""
Script to restart Ollama and verify MCP server status.
MCP servers are managed by agent.py and restart automatically.
"""

import subprocess
import time
import sys
import requests
from pathlib import Path

def check_ollama_running():
    """Check if Ollama is responding on port 11434."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def stop_ollama():
    """Stop Ollama processes."""
    print("[1/4] Stopping Ollama...")
    try:
        # Windows: Stop Ollama processes
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq ollama.exe"],
                capture_output=True,
                text=True
            )
            if "ollama.exe" in result.stdout:
                print("  [INFO] Found Ollama process, stopping...")
                subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], 
                             capture_output=True)
                time.sleep(2)
                print("  [OK] Ollama stopped")
            else:
                print("  [INFO] No Ollama process found (may be a service)")
        else:
            # Linux/Mac: Stop Ollama
            subprocess.run(["pkill", "-f", "ollama"], capture_output=True)
            time.sleep(2)
    except Exception as e:
        print(f"  [WARNING] Error stopping Ollama: {e}")

def start_ollama():
    """Start Ollama server."""
    print("[2/4] Starting Ollama...")
    try:
        if sys.platform == "win32":
            # Windows: Start Ollama in background
            subprocess.Popen(["ollama", "serve"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            # Linux/Mac: Start Ollama
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        # Wait for Ollama to start
        print("  [INFO] Waiting for Ollama to start...")
        for i in range(10):
            time.sleep(1)
            if check_ollama_running():
                print("  [OK] Ollama started successfully")
                return True
        print("  [WARNING] Ollama may need more time or manual start")
        return False
    except FileNotFoundError:
        print("  [ERROR] Ollama command not found in PATH")
        print("  [INFO] Please install Ollama from https://ollama.ai/")
        return False
    except Exception as e:
        print(f"  [ERROR] Failed to start Ollama: {e}")
        return False

def verify_ollama():
    """Verify Ollama is running."""
    print("[3/4] Verifying Ollama...")
    if check_ollama_running():
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            models = response.json().get("models", [])
            print(f"  [OK] Ollama is running (found {len(models)} models)")
            return True
        except Exception as e:
            print(f"  [WARNING] Ollama responding but error: {e}")
            return True
    else:
        print("  [ERROR] Ollama is not responding on port 11434")
        print("  [INFO] Please start manually: ollama serve")
        return False

def mcp_server_info():
    """Display MCP server information."""
    print("[4/4] MCP Server Status:")
    print("  [INFO] MCP servers are managed by agent.py")
    print("  [INFO] They will restart automatically when you run: python agent.py")
    print("  [INFO] No manual restart needed for MCP servers")
    
    # Check if profiles.yaml exists
    profiles_path = Path("config/profiles.yaml")
    if profiles_path.exists():
        print("  [OK] MCP server config found: config/profiles.yaml")
    else:
        print("  [WARNING] MCP server config not found")

def main():
    print("=" * 60)
    print("RESTARTING OLLAMA AND MCP SERVERS")
    print("=" * 60)
    print()
    
    # Stop Ollama
    stop_ollama()
    
    # Start Ollama
    start_ollama()
    
    # Verify Ollama
    verify_ollama()
    
    # MCP Server info
    mcp_server_info()
    
    print()
    print("=" * 60)
    print("RESTART COMPLETE")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("  1. Verify Ollama: curl http://localhost:11434/api/tags")
    print("  2. Start agent.py: python agent.py")
    print("  3. MCP servers will initialize automatically")
    print()

if __name__ == "__main__":
    main()

