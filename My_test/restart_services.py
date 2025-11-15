"""Restart Ollama and MCP servers"""
import subprocess
import sys
import time
import os
from pathlib import Path

def kill_process_by_name(name_pattern):
    """Kill processes matching name pattern"""
    try:
        if sys.platform == "win32":
            # Windows: Use taskkill
            result = subprocess.run(
                ["taskkill", "/F", "/IM", name_pattern, "/T"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 or "not found" not in result.stderr.lower():
                print(f"  [OK] Killed {name_pattern} processes")
            else:
                print(f"  [INFO] No {name_pattern} processes found")
        else:
            # Linux/Mac: Use pkill
            subprocess.run(["pkill", "-f", name_pattern], capture_output=True)
            print(f"  [OK] Killed {name_pattern} processes")
    except Exception as e:
        print(f"  [WARNING] Could not kill {name_pattern}: {e}")

def start_ollama():
    """Start Ollama service"""
    print("\n2. Starting Ollama...")
    try:
        if sys.platform == "win32":
            # Check if Ollama is already running
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq ollama.exe"],
                capture_output=True,
                text=True
            )
            if "ollama.exe" in result.stdout:
                print("  [INFO] Ollama is already running")
                return True
            
            # Try to start Ollama (usually runs as a service on Windows)
            print("  [INFO] Ollama should be running as a service")
            print("  [INFO] If not running, start it manually or check services")
            return True
        else:
            # Linux/Mac: Start ollama serve in background
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            print("  [OK] Ollama started")
            return True
    except Exception as e:
        print(f"  [ERROR] Could not start Ollama: {e}")
        return False

def verify_ollama():
    """Verify Ollama is running"""
    print("\n3. Verifying Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("  [OK] Ollama is running and accessible")
            return True
        else:
            print(f"  [WARNING] Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] Ollama is not accessible: {e}")
        return False

def main():
    print("=" * 80)
    print("RESTARTING OLLAMA AND MCP SERVERS")
    print("=" * 80)
    
    # Kill existing Python processes running MCP servers
    print("\n1. Stopping MCP servers...")
    if sys.platform == "win32":
        # Kill Python processes that might be running MCP servers
        try:
            # Get all Python processes
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                capture_output=True,
                text=True
            )
            print("  [INFO] Note: MCP servers are typically managed by the agent")
            print("  [INFO] They will restart automatically when agent.py runs")
        except Exception as e:
            print(f"  [WARNING] Could not check Python processes: {e}")
    else:
        kill_process_by_name("mcp_server")
    
    # Restart Ollama
    start_ollama()
    time.sleep(1)
    
    # Verify Ollama
    ollama_ok = verify_ollama()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Ollama: {'[OK] Running' if ollama_ok else '[ERROR] Not accessible'}")
    print("MCP Servers: [INFO] Will start automatically when agent.py runs")
    print("\nNext steps:")
    print("  1. Run: python agent.py")
    print("  2. MCP servers will start automatically")
    print("  3. Check stderr logs for [SEARCH] messages when querying")
    print("=" * 80)

if __name__ == "__main__":
    main()

