# How to Use Mermaid Diagrams

This guide explains how to render the architecture diagrams using Mermaid Live Editor and other tools.

## Option 1: Mermaid Live Editor (Recommended)

### Steps:

1. **Open Mermaid Live Editor**
   - Go to: https://mermaid.live/
   - Or: https://mermaid-js.github.io/mermaid-live-editor/

2. **Copy Diagram Code**
   - Open `ARCHITECTURE_DIAGRAM.md`
   - Find the diagram you want (they're in code blocks starting with ````mermaid`)
   - Copy the entire code block (including the `mermaid` tag)

3. **Paste and Render**
   - Paste the code into the left panel of Mermaid Live Editor
   - The diagram will automatically render on the right
   - You can adjust colors, layout, and styling

4. **Export Options**
   - Click "Actions" → "Download PNG" (for images)
   - Click "Actions" → "Download SVG" (for vector graphics)
   - Click "Actions" → "Download PDF" (for documents)

### Example: Copying the System Architecture Diagram

```mermaid
graph TB
    subgraph "User Layer"
        USER[User Input/Output]
    end
    ... (rest of the diagram code)
```

Just copy everything between the ````mermaid` and ```` markers.

---

## Option 2: VS Code with Mermaid Extension

### Steps:

1. **Install Mermaid Extension**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Markdown Preview Mermaid Support" or "Mermaid Preview"
   - Install the extension

2. **View Diagrams**
   - Open `ARCHITECTURE_DIAGRAM.md` in VS Code
   - Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac) to open Markdown preview
   - The diagrams will render automatically

3. **Export**
   - Right-click on the rendered diagram
   - Select "Save Image As..." or use extension export features

---

## Option 3: GitHub/GitLab (Automatic Rendering)

### Steps:

1. **Push to Repository**
   - Push `ARCHITECTURE_DIAGRAM.md` to GitHub or GitLab
   - The Mermaid diagrams will render automatically in the web interface

2. **View Online**
   - Navigate to the file in your repository
   - GitHub/GitLab will automatically render all Mermaid diagrams

3. **Export**
   - Right-click on the rendered diagram
   - Select "Save Image As..."

---

## Option 4: Using Mermaid CLI (Command Line)

### Installation:

```bash
npm install -g @mermaid-js/mermaid-cli
```

### Convert to Image:

```bash
# Convert to PNG
mmdc -i ARCHITECTURE_DIAGRAM.md -o architecture.png

# Convert to SVG
mmdc -i ARCHITECTURE_DIAGRAM.md -o architecture.svg

# Convert to PDF
mmdc -i ARCHITECTURE_DIAGRAM.md -o architecture.pdf
```

### Extract Individual Diagrams:

If you want to extract a specific diagram:

1. Create a new file (e.g., `system_architecture.mmd`)
2. Copy just the Mermaid code (without the markdown code block markers)
3. Run:
   ```bash
   mmdc -i system_architecture.mmd -o system_architecture.png
   ```

---

## Option 5: Online Diagram Tools

### Draw.io / diagrams.net:

1. Go to: https://app.diagrams.net/
2. File → Import → From Text → Mermaid
3. Paste your Mermaid code
4. Edit and export as needed

### Excalidraw:

1. Go to: https://excalidraw.com/
2. Use Mermaid import feature (if available)
3. Or manually recreate using the Mermaid diagram as reference

---

## Quick Reference: Extracting Individual Diagrams

### System Architecture Overview

Copy this code block from `ARCHITECTURE_DIAGRAM.md` (lines ~10-100):

```mermaid
graph TB
    subgraph "User Layer"
        USER[User Input/Output]
    end
    ... (full diagram code)
```

### Sequence Diagram

Copy the sequence diagram code block (starts with `sequenceDiagram`)

### Module Dependencies

Copy the dependency graph code block (starts with `graph LR`)

### Data Flow

Copy the flowchart code block (starts with `flowchart TD`)

### Layered Architecture

Copy the layered architecture code block (starts with `graph TB`)

---

## Tips for Best Results

1. **Large Diagrams**: If a diagram is too large, Mermaid Live Editor might be slow. Consider:
   - Breaking it into smaller sub-diagrams
   - Using the "Actions" → "Zoom" feature
   - Exporting at higher resolution

2. **Customization**: In Mermaid Live Editor, you can:
   - Adjust theme (default, dark, forest, etc.)
   - Change layout direction
   - Modify colors and styles
   - Add custom CSS

3. **Export Quality**: For presentations:
   - Use PNG for raster images (good for slides)
   - Use SVG for vector graphics (scalable, good for documents)
   - Use PDF for documentation

4. **Troubleshooting**: If a diagram doesn't render:
   - Check for syntax errors (missing brackets, quotes, etc.)
   - Ensure all code is between ````mermaid` and ```` markers
   - Try pasting into Mermaid Live Editor to see error messages

---

## Example: Complete Workflow

### Step-by-Step for PowerPoint/Presentation:

1. **Open Mermaid Live**: https://mermaid.live/
2. **Copy Diagram**: From `ARCHITECTURE_DIAGRAM.md`, copy the "System Architecture Overview" diagram
3. **Paste**: Paste into Mermaid Live Editor
4. **Customize**: 
   - Select theme (e.g., "Default" or "Dark")
   - Adjust zoom if needed
5. **Export**: 
   - Click "Actions" → "Download PNG"
   - Choose high resolution (if available)
6. **Insert**: 
   - Open PowerPoint/Google Slides
   - Insert → Picture → Select downloaded PNG
7. **Repeat**: For other diagrams as needed

---

## Alternative: Python Script to Extract Diagrams

If you want to programmatically extract diagrams, here's a Python script:

```python
import re
from pathlib import Path

def extract_mermaid_diagrams(md_file: str, output_dir: str = "diagrams"):
    """Extract all Mermaid diagrams from markdown file"""
    Path(output_dir).mkdir(exist_ok=True)
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all mermaid code blocks
    pattern = r'```mermaid\n(.*?)```'
    diagrams = re.findall(pattern, content, re.DOTALL)
    
    for i, diagram in enumerate(diagrams, 1):
        output_file = Path(output_dir) / f"diagram_{i}.mmd"
        output_file.write_text(diagram, encoding='utf-8')
        print(f"Extracted diagram {i} to {output_file}")
    
    print(f"\nTotal diagrams extracted: {len(diagrams)}")
    print(f"To convert to images, run:")
    print(f"  mmdc -i {output_dir}/diagram_*.mmd -o {output_dir}/diagram_*.png")

if __name__ == "__main__":
    extract_mermaid_diagrams("ARCHITECTURE_DIAGRAM.md")
```

Save as `extract_diagrams.py` and run:
```bash
python extract_diagrams.py
```

Then convert to images:
```bash
mmdc -i diagrams/diagram_*.mmd -o diagrams/diagram_*.png
```

---

## Recommended Workflow

1. **For Quick Viewing**: Use VS Code with Mermaid extension
2. **For Editing/Customization**: Use Mermaid Live Editor
3. **For Export to Images**: Use Mermaid Live Editor → Download PNG/SVG
4. **For Documentation**: Push to GitHub/GitLab (auto-renders)
5. **For Batch Processing**: Use Mermaid CLI

---

## Links

- **Mermaid Live Editor**: https://mermaid.live/
- **Mermaid Documentation**: https://mermaid.js.org/
- **Mermaid CLI**: https://github.com/mermaid-js/mermaid-cli
- **VS Code Extension**: Search "Markdown Preview Mermaid Support"

