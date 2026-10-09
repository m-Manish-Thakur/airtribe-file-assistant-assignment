# File Assistant — FS Tools + LLM Tool Calling

A beginner-friendly Python project for the course assignment.

- **Part A (60%)**: Core file system tools in `fs_tools.py`
- **Part B (40%)**: LLM integration with tool calling in `llm_file_assistant.py`

The LLM can read, list, search, and write resume files based on plain English queries.

---

## Folder Structure

```
file-assistant-assignment/
├── fs_tools.py              # Part A: 4 tools (read, list, write, search)
├── llm_file_assistant.py    # Part B: OpenRouter + tool calling
├── main.py                  # Demo of Part A (no API key needed)
├── requirements.txt         # Dependencies
├── .env.example             # Example env (copy to .env)
├── .gitignore
├── resumes/                 # Sample data (7 dummy resumes)
│   ├── resume_john_doe.txt
│   ├── resume_priya_sharma.txt
│   ├── resume_rahul_verma.txt
│   ├── resume_anjali_gupta.txt
│   ├── resume_amit_patel.txt
│   ├── resume_sneha_reddy.txt
│   └── resume_karan_mehta.txt
├── output/                  # Generated files go here
└── README.md
```

---

## Setup (5 minutes)

### 1. Install Python 3.9+

Check:

```bash
python --version
```

### 2. Install dependencies

```bash
cd file-assistant-assignment
pip install -r requirements.txt
```

### 3. Setup API key (only for Part B, via OpenRouter)

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Open `.env` and paste your real key:

```
OPENROUTER_API_KEY=sk-or-v1-your-real-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

Get a key from: https://openrouter.ai/keys

> You only need these 2 values. Nothing else.

---

## Usage

### Demo 1: Part A only (no API key needed)

```bash
python main.py
```

This will:
1. List all files in `resumes/`
2. Read `resume_john_doe.txt`
3. Search for "Python" in all resumes
4. Write `output/summary.txt`

### Demo 2: Part B — LLM with tools (needs API key)

```bash
python llm_file_assistant.py
```

Then try these example queries:

```
Read all resumes in the resumes folder
```

```
Find resumes mentioning Python experience
```

```
Create a summary file for resume_john_doe.txt
```

Watch the terminal — you will see lines like:

```
[Tool calling] LLM wants to call 1 tool(s)...
  -> list_files({'directory': 'resumes'})
  -> search_in_file({'filepath': 'resumes/resume_priya_sharma.txt', 'keyword': 'Python'})
```

That is **tool calling in action** — the LLM decides which function to call.

---

## Tools Documentation

### 1. `read_file(filepath: str) -> dict`

Read PDF, TXT, or DOCX file and return text + metadata.

```python
import fs_tools
result = fs_tools.read_file("resumes/resume_john_doe.txt")
print(result["content"])   # file text
print(result["size_bytes"])  # file size
```

Success response:

```python
{"success": True, "filename": "...", "extension": ".txt",
 "content": "...", "size_bytes": 123, "error": None}
```

Error response (file missing, unsupported type) returns `success: False` with `error` message — never crashes.

### 2. `list_files(directory: str, extension: str = None) -> list`

```python
fs_tools.list_files("resumes")          # all files
fs_tools.list_files("resumes", ".txt")  # only .txt files
fs_tools.list_files("resumes", "pdf")   # dot is optional
```

Each item: `{"name": ..., "path": ..., "size_bytes": ..., "modified": ...}`

### 3. `write_file(filepath: str, content: str) -> dict`

```python
fs_tools.write_file("output/summary.txt", "Hello world")
# Creates output/ folder automatically if missing
```

### 4. `search_in_file(filepath: str, keyword: str) -> dict`

Case-insensitive search with context (1 line before/after).

```python
result = fs_tools.search_in_file("resumes/resume_john_doe.txt", "Python")
print(result["total_matches"])
print(result["matches"][0]["line"])
```

---

## How LLM Tool Calling Works

```
User: "Find resumes mentioning Python"
        |
        v
LLM reads query + tool list
        |
        v
LLM calls: list_files("resumes")
        |
        v
Python runs list_files, returns file list
        |
        v
LLM calls: search_in_file(file, "Python") for each file
        |
        v
LLM writes final answer: "4 resumes mention Python..."
```

Code flow is in `ask_assistant()` in `llm_file_assistant.py`:
1. Send user message + `TOOLS` to OpenRouter
2. If LLM returns `tool_calls`, run the real Python function
3. Send tool result back to LLM
4. Repeat (max 5 steps) until LLM gives a final text answer

---

## Demo Video Guide (2–3 minutes)

Record your own video with this script:

**0:00 – 0:30 — Show project**
- Open folder, show `fs_tools.py`, `llm_file_assistant.py`, `resumes/`
- Run `python main.py` to show Part A works

**0:30 – 1:30 — Query 1 & 2**
- Run `python llm_file_assistant.py`
- Ask: *“Read all resumes in the resumes folder”* → show `list_files` + `read_file` calls
- Ask: *“Find resumes mentioning Python experience”* → show `search_in_file` calls

**1:30 – 2:30 — Query 3**
- Ask: *“Create a summary file for resume_john_doe.txt”* → show `read_file` + `write_file` calls
- Open `output/` folder, show the created file
- Close with: “LLM decided which tool to call based on my query.”

You can record with OBS, Zoom, or Loom (free).

---

## Notes for Beginners

- All code is kept simple on purpose — small functions, plain comments.
- Every tool returns `dict`/`list` (never throws) so the LLM can always understand the result.
- `main.py` works without any API key — start there.
- Only 2 env variables are needed: `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`.
