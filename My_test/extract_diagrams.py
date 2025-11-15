"""
Extract Mermaid diagrams from ARCHITECTURE_DIAGRAM.md into separate files.
Each diagram can then be used in Mermaid Live Editor or converted to images.
"""

import re
from pathlib import Path

def extract_mermaid_diagrams(md_file: str = "ARCHITECTURE_DIAGRAM.md", output_dir: str = "diagrams"):
    """Extract all Mermaid diagrams from markdown file into separate .mmd files"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"Error: {md_file} not found!")
        return
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all mermaid code blocks with their titles
    # Pattern: ## Title followed by ```mermaid ... ```
    pattern = r'##\s+([^\n]+)\n\n```mermaid\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if not matches:
        # Fallback: find any mermaid blocks
        pattern = r'```mermaid\n(.*?)```'
        diagrams = re.findall(pattern, content, re.DOTALL)
        matches = [(f"Diagram {i+1}", d) for i, d in enumerate(diagrams)]
    
    diagram_names = {
        "System Architecture Overview": "01_system_architecture",
        "Detailed Component Flow": "02_component_flow",
        "Module Dependencies": "03_module_dependencies",
        "Data Flow Architecture": "04_data_flow",
        "Layered Architecture": "05_layered_architecture"
    }
    
    for title, diagram in matches:
        # Clean title and create filename
        clean_title = title.strip()
        filename = diagram_names.get(clean_title, clean_title.lower().replace(" ", "_"))
        filename = re.sub(r'[^\w\-_]', '', filename)
        
        output_file = output_path / f"{filename}.mmd"
        output_file.write_text(diagram.strip(), encoding='utf-8')
        print(f"[OK] Extracted: {clean_title}")
        print(f"     -> {output_file}")
    
    print(f"\n{'='*60}")
    print(f"Total diagrams extracted: {len(matches)}")
    print(f"Output directory: {output_path.absolute()}")
    print(f"\nNext steps:")
    print(f"1. Open files in Mermaid Live Editor: https://mermaid.live/")
    print(f"2. Or convert to images using Mermaid CLI:")
    print(f"   npm install -g @mermaid-js/mermaid-cli")
    print(f"   mmdc -i {output_dir}/*.mmd -o {output_dir}/*.png")

if __name__ == "__main__":
    extract_mermaid_diagrams()

