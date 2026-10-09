"""
fs_tools.py
Part A: Core File System Tools

Simple beginner-friendly tools to work with resume files.
Each tool returns a dict or list so LLM can easily understand output.
"""

import os
from datetime import datetime


def read_file(filepath: str) -> dict:
    """
    Read a resume file (PDF, TXT, DOCX) and return text + metadata.

    Args:
        filepath: path to file, e.g. "resumes/resume_john_doe.txt"

    Returns:
        dict like:
        {
            "success": True,
            "filepath": "...",
            "filename": "...",
            "extension": ".txt",
            "content": "file text here",
            "size_bytes": 123,
            "error": None
        }
    """
    # 1. Check if file exists
    if not os.path.exists(filepath):
        return {
            "success": False,
            "filepath": filepath,
            "filename": None,
            "extension": None,
            "content": None,
            "size_bytes": None,
            "error": f"File not found: {filepath}",
        }

    filename = os.path.basename(filepath)
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    size = os.path.getsize(filepath)

    try:
        # 2. TXT file -> simple read
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        # 3. PDF file -> needs pypdf library
        elif ext == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(filepath)
            parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    parts.append(text)
            content = "\n".join(parts)

        # 4. DOCX file -> needs python-docx library
        elif ext == ".docx":
            from docx import Document

            doc = Document(filepath)
            parts = []
            for para in doc.paragraphs:
                parts.append(para.text)
            content = "\n".join(parts)

        # 5. Any other file type is not supported
        else:
            return {
                "success": False,
                "filepath": filepath,
                "filename": filename,
                "extension": ext,
                "content": None,
                "size_bytes": size,
                "error": f"Unsupported file type: {ext}. Use .pdf, .txt or .docx",
            }

        return {
            "success": True,
            "filepath": filepath,
            "filename": filename,
            "extension": ext,
            "content": content,
            "size_bytes": size,
            "error": None,
        }

    except Exception as e:
        # Never crash, always return error in dict
        return {
            "success": False,
            "filepath": filepath,
            "filename": filename,
            "extension": ext,
            "content": None,
            "size_bytes": size,
            "error": str(e),
        }


def list_files(directory: str, extension: str = None) -> list:
    """
    List all files in a directory.

    Args:
        directory: folder path, e.g. "resumes"
        extension: optional filter, e.g. ".pdf" or ".txt". None = all files.

    Returns:
        list of dicts, each with name, path, size, modified date.
        Example: [{"name": "a.txt", "path": "resumes/a.txt", ...}]
    """
    # 1. If folder does not exist, return empty list
    if not os.path.exists(directory):
        return []

    # 2. Make extension lowercase for safe comparison
    if extension is not None:
        extension = extension.lower()
        # Add dot if user forgot: "pdf" -> ".pdf"
        if not extension.startswith("."):
            extension = "." + extension

    result = []

    # 3. Loop through files in folder
    for name in os.listdir(directory):
        full_path = os.path.join(directory, name)

        # Skip sub-folders, we want only files
        if not os.path.isfile(full_path):
            continue

        # Skip files that do not match extension
        if extension is not None:
            _, ext = os.path.splitext(name)
            if ext.lower() != extension:
                continue

        # 4. Collect simple metadata
        size = os.path.getsize(full_path)
        modified_time = os.path.getmtime(full_path)
        modified_date = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")

        result.append(
            {
                "name": name,
                "path": full_path,
                "size_bytes": size,
                "modified": modified_date,
            }
        )

    return result


def write_file(filepath: str, content: str) -> dict:
    """
    Write text content to a file. Creates folders if needed.

    Args:
        filepath: where to write, e.g. "output/summary.txt"
        content: text to write inside file

    Returns:
        dict with success True/False and message.
    """
    try:
        # 1. Create parent folder if it does not exist
        folder = os.path.dirname(filepath)
        if folder != "" and not os.path.exists(folder):
            os.makedirs(folder)

        # 2. Write the file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "filepath": filepath,
            "message": f"File written successfully: {filepath}",
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "filepath": filepath,
            "message": None,
            "error": str(e),
        }


def search_in_file(filepath: str, keyword: str) -> dict:
    """
    Search for a keyword inside a file (case-insensitive).

    Args:
        filepath: file to search in
        keyword: word to find, e.g. "Python"

    Returns:
        dict with matches. Each match has line number + context.
    """
    # 1. First read the file using our own read_file tool
    data = read_file(filepath)

    if not data["success"]:
        return {
            "success": False,
            "filepath": filepath,
            "keyword": keyword,
            "total_matches": 0,
            "matches": [],
            "error": data["error"],
        }

    content = data["content"]
    if content is None or content.strip() == "":
        return {
            "success": True,
            "filepath": filepath,
            "keyword": keyword,
            "total_matches": 0,
            "matches": [],
            "error": None,
        }

    # 2. Split into lines and search line by line
    matches = []
    lines = content.split("\n")
    keyword_lower = keyword.lower()

    for i, line in enumerate(lines, start=1):
        if keyword_lower in line.lower():
            # Context = 1 line before + current line + 1 line after
            before = lines[i - 2] if i - 2 >= 0 else ""
            after = lines[i] if i < len(lines) else ""

            matches.append(
                {
                    "line_number": i,
                    "line": line.strip(),
                    "context_before": before.strip(),
                    "context_after": after.strip(),
                }
            )

    return {
        "success": True,
        "filepath": filepath,
        "keyword": keyword,
        "total_matches": len(matches),
        "matches": matches,
        "error": None,
    }
