from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import os
import json
import faiss
import numpy as np
from pathlib import Path
import requests
from markitdown import MarkItDown
import time
from models import AddInput, AddOutput, SqrtInput, SqrtOutput, StringsToIntsInput, StringsToIntsOutput, ExpSumInput, ExpSumOutput, PythonCodeInput, PythonCodeOutput, UrlInput, FilePathInput, MarkdownInput, MarkdownOutput, ChunkListOutput, SearchDocumentsInput
from tqdm import tqdm
import hashlib
from pydantic import BaseModel
import subprocess
import sqlite3
import trafilatura
import pymupdf4llm
import re
import base64 # ollama needs base64-encoded-image


mcp = FastMCP("Calculator")

EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_URL = "http://localhost:11434/api/generate"
EMBED_MODEL = "nomic-embed-text"
GEMMA_MODEL = "llava"  # Vision model for image captioning
PHI_MODEL = "gemma2:2b"  # Using smaller model (1.6GB) for faster setup
QWEN_MODEL = "qwen2.5:32b-instruct-q4_0 "
CHUNK_SIZE = 512
CHUNK_OVERLAP = 120  # Increased from 30 for better context preservation across chunk boundaries
MAX_CHUNK_LENGTH = 3000  # characters (aligned with ~512 words ≈ 2000-3000 chars typical)
TOP_K = 6  # FAISS top-K matches
ROOT = Path(__file__).parent.resolve()


def get_embedding(text: str) -> np.ndarray:
    result = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    result.raise_for_status()
    return np.array(result.json()["embedding"], dtype=np.float32)

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Chunk text by word count with overlap, enforcing MAX_CHUNK_LENGTH character limit.
    """
    words = text.split()
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i+size])
        # Enforce MAX_CHUNK_LENGTH: truncate if exceeds character limit
        if len(chunk) > MAX_CHUNK_LENGTH:
            # Truncate to last complete word within limit
            truncated = chunk[:MAX_CHUNK_LENGTH]
            last_space = truncated.rfind(' ')
            if last_space > 0:
                chunk = truncated[:last_space] + "..."
            else:
                chunk = truncated + "..."
        yield chunk

def mcp_log(level: str, message: str) -> None:
    sys.stderr.write(f"{level}: {message}\n")
    sys.stderr.flush()

# === CHUNKING ===





def are_related(chunk1: str, chunk2: str, index: int) -> bool:
    prompt = f"""
You are helping to segment a document into topic-based chunks. Unfortunately, the sentences are mixed up.

CHUNK 1: "{chunk1}"
CHUNK 2: "{chunk2}"

Should these two chunks appear in the **same paragraph or flow of writing**?

Even if the subject changes slightly (e.g., One person to another), treat them as related **if they belong to the same broader context or topic** (like cricket, AI, or real estate). 

Also consider cues like continuity words (e.g., "However", "But", "Also") or references that link the sentences.

Answer with:
Yes – if the chunks should appear together in the same paragraph or section  
No – if they are about different topics and should be separated

Just respond in one word (Yes or No), and do not provide any further explanation.
"""
    mcp_log("COMPARE", f"Comparing chunk {index} and {index+1}")
    mcp_log("COMPARE", f"  Chunk {index}: {chunk1[:60]}{'...' if len(chunk1) > 60 else ''}")
    mcp_log("COMPARE", f"  Chunk {index+1}: {chunk2[:60]}{'...' if len(chunk2) > 60 else ''}")

    result = requests.post(OLLAMA_CHAT_URL, json={
        "model": PHI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    })
    result.raise_for_status()
    reply = result.json().get("message", {}).get("content", "").strip().lower()
    mcp_log("MODEL", f"Reply: {reply}")
    return reply.startswith("yes")



@mcp.tool()
def search_stored_documents(input: SearchDocumentsInput) -> list[str]:
    """Search documents to get relevant extracts. Usage: input={"input": {"query": "your query"}} result = await mcp.call_tool('search_stored_documents', input) 
    
    IMPORTANT: This function returns list[str] directly. When called via MCP, extract the result like:
    result = await mcp.call_tool('search_stored_documents', {"input": {"query": "..."}})
    chunks = result if isinstance(result, list) else (result.content[0].text if hasattr(result, 'content') and result.content else [])
    """

    ensure_faiss_ready()
    query = input.query
    mcp_log("SEARCH", f"Query: {query}")
    try:
        index = faiss.read_index(str(ROOT / "faiss_index" / "index.bin"))
        metadata = json.loads((ROOT / "faiss_index" / "metadata.json").read_text())
        query_vec = get_embedding(query).reshape(1, -1)
        # Increase k to 10 for better retrieval of specific information
        D, I = index.search(query_vec, k=10)
        results = []
        
        # Optional: Distance threshold to filter low-quality matches
        # Based on analysis: good matches typically < 390, bad matches typically > 415
        # Using 400 as threshold: keeps ~89% of good results, filters ~90% of bad results
        # Set to None to disable distance filtering (recommended - trust semantic ranking)
        DISTANCE_THRESHOLD = None  # L2 distance threshold (lower = more similar), None = disabled
        
        for rank, idx in enumerate(I[0]):
            if idx < len(metadata):  # Safety check
                distance = D[0][rank]
                
                # Filter by distance threshold (optional - can be disabled by setting to None)
                if DISTANCE_THRESHOLD is not None and distance > DISTANCE_THRESHOLD:
                    mcp_log("FILTER", f"Skipping result {rank+1} (distance {distance:.2f} > threshold {DISTANCE_THRESHOLD})")
                    continue
                
                data = metadata[idx]
                # Safety check: ensure 'chunk' key exists
                if 'chunk' not in data:
                    mcp_log("WARNING", f"Chunk {idx} missing 'chunk' key, skipping")
                    continue
                chunk_text = data['chunk']
                
                # Build enhanced reference string with all available metadata
                ref_parts = [f"Source: {data['doc']}"]
                ref_parts.append(f"ID: {data.get('chunk_id', 'unknown')}")
                
                if 'chunk_position' in data:
                    ref_parts.append(f"Position: {data['chunk_position']}")
                
                if 'section' in data:
                    ref_parts.append(f"Section: {data['section']}")
                
                if 'page' in data:
                    ref_parts.append(f"Page: {data['page']}")
                
                if 'doc_type' in data:
                    ref_parts.append(f"Type: {data['doc_type']}")
                
                reference = " | ".join(ref_parts)
                
                # Include image captions in search results (they're stored as "**Image:** {caption}")
                results.append(f"{chunk_text}\n[{reference}]")
        mcp_log("SEARCH", f"Returning {len(results)} results")
        if len(results) == 0:
            mcp_log("WARNING", "No results found - this might indicate an issue")
        return results
    except Exception as e:
        mcp_log("ERROR", f"Search failed: {str(e)}")
        import traceback
        mcp_log("ERROR", f"Traceback: {traceback.format_exc()}")
        return [f"ERROR: Failed to search: {str(e)}"]


def caption_image(img_url_or_path: str) -> str:
    mcp_log("CAPTION", f"[IMAGE] Attempting to caption image: {img_url_or_path}")

    full_path = Path(__file__).parent / "documents" / img_url_or_path
    full_path = full_path.resolve()

    if not full_path.exists():
        mcp_log("ERROR", f"[ERROR] Image file not found: {full_path}")
        return f"[Image file not found: {img_url_or_path}]"

    try:
        if img_url_or_path.startswith("http"): # for extract_web_pages
            result = requests.get(img_url_or_path)
            encoded_image = base64.b64encode(result.content).decode("utf-8")
        else:
            with open(full_path, "rb") as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

        # Set stream=True to get the full generator-style output
        with requests.post(OLLAMA_URL, json={
            "model": GEMMA_MODEL,
            "prompt": "If there is lot of text in the image, then ONLY reply back with exact text in the image, else Describe the image such that your result can replace 'alt-text' for it. Only explain the contents of the image and provide no further explaination.",
            "images": [encoded_image],
            "stream": True
        }, stream=True) as result:

            caption_parts = []
            for line in result.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    # Ollama uses "response" field, not "result"
                    caption_parts.append(data.get("response", data.get("result", "")))
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue  # silently skip malformed lines

            caption = "".join(caption_parts).strip()
            if not caption:
                mcp_log("WARN", f"[WARNING] Empty caption returned for {img_url_or_path}")
                return "[No caption returned - model may not support vision or image processing failed]"
            mcp_log("CAPTION", f"[SUCCESS] Caption generated: {caption[:100]}...")
            return caption

    except requests.exceptions.HTTPError as e:
        mcp_log("ERROR", f"[ERROR] HTTP error captioning image {img_url_or_path}: {e}")
        if hasattr(e.response, 'text'):
            mcp_log("ERROR", f"[ERROR] Response: {e.response.text[:200]}")
        return f"[Image captioning failed: {str(e)}]"
    except Exception as e:
        mcp_log("ERROR", f"[WARNING] Failed to caption image {img_url_or_path}: {e}")
        return f"[Image could not be processed: {img_url_or_path}]"





def replace_images_with_captions(markdown: str) -> str:
    def replace(match):
        alt, src = match.group(1), match.group(2)
        try:
            caption = caption_image(src)
            # Attempt to delete only if local and file exists
            if not src.startswith("http"):
                img_path = Path(__file__).parent / "documents" / src
                if img_path.exists():
                    img_path.unlink()
                    mcp_log("INFO", f"[DELETE] Deleted image after captioning: {img_path}")
            return f"**Image:** {caption}"
        except Exception as e:
            mcp_log("WARN", f"Image deletion failed: {e}")
            return f"[Image could not be processed: {src}]"

    return re.sub(r'!\[(.*?)\]\((.*?)\)', replace, markdown)


@mcp.tool()
def convert_webpage_url_into_markdown(input: UrlInput) -> MarkdownOutput:
    """Return clean webpage content without Ads, and clutter. Usage: input={{"input": {{"url": "https://example.com"}}}} result = await mcp.call_tool('convert_webpage_url_into_markdown', input)"""

    downloaded = trafilatura.fetch_url(input.url)
    if not downloaded:
        return MarkdownOutput(markdown="Failed to download the webpage.")

    markdown = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
        include_images=True,
        output_format='markdown'
    ) or ""

    markdown = replace_images_with_captions(markdown)
    return MarkdownOutput(markdown=markdown)

@mcp.tool()
def extract_pdf(input: FilePathInput) -> MarkdownOutput:
    """Convert PDF to markdown. Usage: input={"input": {"file_path": "documents/sample.pdf"} } result = await mcp.call_tool('extract_pdf', input)"""


    if not os.path.exists(input.file_path):
        return MarkdownOutput(markdown=f"File not found: {input.file_path}")

    ROOT = Path(__file__).parent.resolve()
    global_image_dir = ROOT / "documents" / "images"
    global_image_dir.mkdir(parents=True, exist_ok=True)

    # Suppress pymupdf4llm warnings to stdout (MCP uses stdout for JSON-RPC only)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Redirect stdout temporarily to stderr for library output
        import contextlib
        import io
        old_stdout = sys.stdout
        sys.stdout = sys.stderr
        try:
            # Actual markdown with relative image paths
            markdown = pymupdf4llm.to_markdown(
                input.file_path,
                write_images=True,
                image_path=str(global_image_dir)
            )
        finally:
            sys.stdout = old_stdout

    # Re-point image links in the markdown
    markdown = re.sub(
        r'!\[\]\((.*?/images/)([^)]+)\)',
        r'![](images/\2)',
        markdown.replace("\\", "/")
    )

    markdown = replace_images_with_captions(markdown)
    return MarkdownOutput(markdown=markdown)


def semantic_merge(text: str) -> list[str]:
    """Splits text semantically using LLM: detects second topic and reuses leftover intelligently."""
    WORD_LIMIT = 256  # Aligned with CHUNK_SIZE for consistent chunk sizing
    words = text.split()
    i = 0
    final_chunks = []

    while i < len(words):
        # 1. Take next chunk of words (and prepend leftovers if any)
        chunk_words = words[i:i + WORD_LIMIT]
        chunk_text = " ".join(chunk_words).strip()

        prompt = f"""
You are a markdown document segmenter.

Here is a portion of a markdown document:

---
{chunk_text}
---

If this chunk clearly contains **more than one distinct topic or section**, reply ONLY with the **second part**, starting from the first sentence or heading of the new topic.

If it's only one topic, reply with NOTHING.

Keep markdown formatting intact.
"""

        try:
            result = requests.post(OLLAMA_CHAT_URL, json={
                "model": PHI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            })
            reply = result.json().get("message", {}).get("content", "").strip()

            if reply:
                # If LLM returned second part, separate it
                split_point = chunk_text.find(reply)
                if split_point != -1:
                    first_part = chunk_text[:split_point].strip()
                    second_part = reply.strip()

                    final_chunks.append(first_part)

                    # Get remaining words from second_part and re-use them in next batch
                    leftover_words = second_part.split()
                    words = leftover_words + words[i + WORD_LIMIT:]
                    i = 0  # restart loop with leftover + remaining
                    continue
                else:
                    # fallback: if split point not found
                    final_chunks.append(chunk_text)
            else:
                final_chunks.append(chunk_text)

        except Exception as e:
            mcp_log("ERROR", f"Semantic chunking LLM error: {e}")
            final_chunks.append(chunk_text)

        i += WORD_LIMIT

    return final_chunks







def process_documents():
    """Process documents and create FAISS index using unified multimodal strategy."""
    mcp_log("INFO", "Indexing documents with unified RAG pipeline...")
    ROOT = Path(__file__).parent.resolve()
    DOC_PATH = ROOT / "documents"
    INDEX_CACHE = ROOT / "faiss_index"
    INDEX_CACHE.mkdir(exist_ok=True)
    INDEX_FILE = INDEX_CACHE / "index.bin"
    METADATA_FILE = INDEX_CACHE / "metadata.json"
    CACHE_FILE = INDEX_CACHE / "doc_index_cache.json"

    def file_hash(path):
        return hashlib.md5(Path(path).read_bytes()).hexdigest()

    CACHE_META = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
    metadata = json.loads(METADATA_FILE.read_text()) if METADATA_FILE.exists() else []
    index = faiss.read_index(str(INDEX_FILE)) if INDEX_FILE.exists() else None

    for file in DOC_PATH.glob("*.*"):
        fhash = file_hash(file)
        if file.name in CACHE_META and CACHE_META[file.name] == fhash:
            mcp_log("SKIP", f"Skipping unchanged file: {file.name}")
            continue

        mcp_log("PROC", f"Processing: {file.name}")
        try:
            ext = file.suffix.lower()
            markdown = ""

            if ext == ".pdf":
                mcp_log("INFO", f"Using MuPDF4LLM to extract {file.name}")
                # Redirect stdout to stderr during PDF extraction (pymupdf4llm prints warnings)
                old_stdout = sys.stdout
                sys.stdout = sys.stderr
                try:
                    markdown = extract_pdf(FilePathInput(file_path=str(file))).markdown
                finally:
                    sys.stdout = old_stdout

            elif ext in [".html", ".htm", ".url"]:
                mcp_log("INFO", f"Using Trafilatura to extract {file.name}")
                markdown = convert_webpage_url_into_markdown(UrlInput(url=file.read_text().strip())).markdown

            else:
                # Fallback to MarkItDown for other formats
                converter = MarkItDown()
                mcp_log("INFO", f"Using MarkItDown fallback for {file.name}")
                markdown = converter.convert(str(file)).text_content

            if not markdown.strip():
                mcp_log("WARN", f"No content extracted from {file.name}")
                continue

            if len(markdown.split()) < 10:
                mcp_log("WARN", f"Content too short for chunking in {file.name} - Using as single chunk.")
                chunks = [markdown.strip()]
            else:
                mcp_log("INFO", f"Using fast word-based chunking on {file.name} with {len(markdown.split())} words")
                # Fast word-based chunking instead of slow semantic merge
                chunks = list(chunk_text(markdown, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP))


            embeddings_for_file = []
            new_metadata = []
            
            # Extract headings/sections from markdown for context
            headings = []
            if ext == ".pdf" or ext in [".md", ".txt"]:
                # Extract markdown headings (##, ###, etc.)
                heading_pattern = r'^(#{1,6})\s+(.+)$'
                for line in markdown.split('\n'):
                    match = re.match(heading_pattern, line.strip())
                    if match:
                        level = len(match.group(1))
                        heading_text = match.group(2).strip()
                        headings.append((level, heading_text))
            
            # Calculate chunk position in document
            total_chunks = len(chunks)
            
            for i, chunk in enumerate(tqdm(chunks, desc=f"Embedding {file.name}")):
                embedding = get_embedding(chunk)
                embeddings_for_file.append(embedding)
                
                # Find nearest heading for context
                nearest_heading = None
                if headings:
                    # Simple heuristic: find heading that appears before this chunk
                    chunk_start_pos = markdown.find(chunk[:100])  # Find chunk position in markdown
                    for level, heading in reversed(headings):
                        heading_pos = markdown.find(f"{'#' * level} {heading}")
                        if heading_pos != -1 and heading_pos < chunk_start_pos:
                            nearest_heading = heading
                            break
                
                # Extract first few words as preview
                preview_words = chunk.split()[:10]
                preview = " ".join(preview_words) + ("..." if len(chunk.split()) > 10 else "")
                
                # Build enhanced metadata
                chunk_metadata = {
                    "doc": file.name,
                    "doc_path": str(file.relative_to(ROOT / "documents")),
                    "doc_type": ext.lstrip('.'),
                    "chunk": chunk,
                    "chunk_id": f"{file.stem}_chunk_{i:04d}",
                    "chunk_index": i,
                    "total_chunks": total_chunks,
                    "chunk_position": f"{i+1}/{total_chunks}",
                    "word_count": len(chunk.split()),
                    "char_count": len(chunk),
                    "preview": preview,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add section context if available
                if nearest_heading:
                    chunk_metadata["section"] = nearest_heading
                
                # For PDFs, try to extract page number from chunk (if available in markdown)
                if ext == ".pdf":
                    # Look for page markers in markdown (pymupdf4llm sometimes adds them)
                    page_match = re.search(r'page[_\s]*(\d+)', chunk, re.IGNORECASE)
                    if page_match:
                        chunk_metadata["page"] = int(page_match.group(1))
                
                new_metadata.append(chunk_metadata)

            if embeddings_for_file:
                if index is None:
                    dim = len(embeddings_for_file[0])
                    index = faiss.IndexFlatL2(dim)
                index.add(np.stack(embeddings_for_file))
                metadata.extend(new_metadata)
                CACHE_META[file.name] = fhash

                # Immediately save index and metadata
                CACHE_FILE.write_text(json.dumps(CACHE_META, indent=2))
                METADATA_FILE.write_text(json.dumps(metadata, indent=2))
                faiss.write_index(index, str(INDEX_FILE))
                mcp_log("SAVE", f"Saved FAISS index and metadata after processing {file.name}")

        except Exception as e:
            mcp_log("ERROR", f"Failed to process {file.name}: {e}")



def ensure_faiss_ready():
    from pathlib import Path
    index_path = ROOT / "faiss_index" / "index.bin"
    meta_path = ROOT / "faiss_index" / "metadata.json"
    if not (index_path.exists() and meta_path.exists()):
        mcp_log("INFO", "Index not found — running process_documents()...")
        process_documents()
    else:
        mcp_log("INFO", "Index already exists. Skipping regeneration.")


if __name__ == "__main__":
    mcp_log("INFO", "STARTING THE SERVER AT AMAZING LOCATION")

    if len(sys.argv) > 1 and sys.argv[1] == "index":
        # Just build the index, don't start server
        mcp_log("INFO", "Building FAISS index only...")
        process_documents()
        mcp_log("INFO", "Index build complete!")
    elif len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run() # Run without transport for dev server
    else:
        # Start the server in stdio mode (for MCP client)
        mcp.run(transport="stdio")
