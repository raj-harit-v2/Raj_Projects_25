"""Quick script to switch from Gemini to Ollama"""
import yaml
from pathlib import Path

profile_path = Path("config/profiles.yaml")

# Read current config
with open(profile_path, "r") as f:
    profile = yaml.safe_load(f)

current_model = profile["llm"]["text_generation"]
print(f"Current model: {current_model}")

# Available Ollama models
available_models = ["phi4", "gemma2:2b", "qwen2.5:32b-instruct-q4_0"]

print("\nAvailable Ollama models:")
for i, model in enumerate(available_models, 1):
    print(f"  {i}. {model}")

choice = input("\nSelect model (1-3) or 'cancel': ").strip()

if choice.lower() == 'cancel':
    print("Cancelled.")
    exit(0)

try:
    idx = int(choice) - 1
    if 0 <= idx < len(available_models):
        new_model = available_models[idx]
        
        # Update config
        profile["llm"]["text_generation"] = new_model
        
        # Write back
        with open(profile_path, "w") as f:
            yaml.dump(profile, f, default_flow_style=False, sort_keys=False)
        
        print(f"\n[SUCCESS] Switched to: {new_model}")
        print(f"Restart agent.py to use the new model.")
        print(f"\nNote: phi4 is recommended for best performance.")
    else:
        print("Invalid choice.")
except ValueError:
    print("Invalid input.")

