"""Breakdown Canvas LMS PDF by pages and images"""
from pathlib import Path
import json

print("=" * 80)
print("CANVAS LMS PDF BREAKDOWN BY PAGES/IMAGES")
print("=" * 80)

# Check if PDF exists
pdf_path = Path("documents/How to use Canvas LMS.pdf")
if not pdf_path.exists():
    print(f"\n[ERROR] PDF not found: {pdf_path}")
    exit(1)

print(f"\nPDF File: {pdf_path.name}")
print(f"Size: {pdf_path.stat().st_size / 1024:.1f} KB")

# Check images directory
images_dir = Path("documents/images")
canvas_images = sorted([img for img in images_dir.glob("How-to-use-Canvas-LMS.pdf-*.png")])

print(f"\nExtracted Images: {len(canvas_images)}")

if canvas_images:
    # Group by page (format: How-to-use-Canvas-LMS.pdf-PAGE-IMAGE.png)
    pages = {}
    for img in canvas_images:
        parts = img.stem.split('-')
        # Find page number (format: pdf-PAGE-IMAGE)
        try:
            # Extract page number from filename
            # Format: How-to-use-Canvas-LMS.pdf-PAGE-IMAGE
            page_idx = None
            for i, part in enumerate(parts):
                if part.isdigit() and i > 0:
                    page_idx = int(part)
                    break
            
            if page_idx is None:
                continue
                
            if page_idx not in pages:
                pages[page_idx] = []
            pages[page_idx].append({
                'filename': img.name,
                'size': img.stat().st_size / 1024,  # KB
                'path': str(img)
            })
        except (ValueError, IndexError):
            continue
    
    print(f"\nPages with images: {len(pages)}")
    print("\nBreakdown by page:")
    for page_num in sorted(pages.keys()):
        imgs = pages[page_num]
        print(f"\n  Page {page_num}: {len(imgs)} image(s)")
        for i, img in enumerate(imgs, 1):
            print(f"    Image {i}: {img['filename']} ({img['size']:.1f} KB)")
            print(f"             Path: {img['path']}")
    
    # Check index for these images
    idx_path = Path('faiss_index/metadata.json')
    if idx_path.exists():
        data = json.loads(idx_path.read_text())
        canvas_chunks = [c for c in data if 'Canvas' in c.get('doc', '')]
        print(f"\n\nIndex Status:")
        print(f"  Canvas LMS chunks in index: {len(canvas_chunks)}")
        if canvas_chunks:
            for i, chunk in enumerate(canvas_chunks[:5], 1):
                image_count = chunk['chunk'].count('**Image:**')
                print(f"  Chunk {i}: {image_count} image caption(s)")
else:
    print("\n[WARNING] No images found for Canvas LMS PDF")
    print("PDF may not have been processed yet")

print("\n" + "=" * 80)

