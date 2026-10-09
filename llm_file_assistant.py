"""
llm_file_assistant.py
Part B: LLM Integration

Connects our fs_tools to OpenRouter so the LLM can call tools
based on user queries. Uses OpenAI-compatible API.

Example queries:
- "Read all resumes in the resumes folder"
- "Find resumes mentioning Python experience"
- "Create a summary file for resume_john_doe.txt"

Run: python llm_file_assistant.py
"""

import json
import os

from dotenv import load_dotenv

# Load .env file (for OPENROUTER_API_KEY)
load_dotenv()

import fs_tools

# -------------------------------------------------
# 1. Tool definitions for the LLM (in simple words)
# -------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a resume file (pdf, txt, docx) and get its text",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to file, e.g. resumes/resume_john_doe.txt",
                    }
                },
                "required": ["filepath"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a folder, optionally filter by extension",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Folder path, e.g. resumes",
                    },
                    "extension": {
                        "type": "string",
                        "description": "Optional filter like .pdf or .txt",
                    },
                },
                "required": ["directory"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Where to save, e.g. output/summary.txt"},
                    "content": {"type": "string", "description": "Text to write in file"},
                },
                "required": ["filepath", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search for a keyword inside a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "File to search in"},
                    "keyword": {"type": "string", "description": "Word to search, e.g. Python"},
                },
                "required": ["filepath", "keyword"],
            },
        },
    },
]

# Map tool name -> real python function
AVAILABLE_FUNCTIONS = {
    "read_file": fs_tools.read_file,
    "list_files": fs_tools.list_files,
    "write_file": fs_tools.write_file,
    "search_in_file": fs_tools.search_in_file,
}

SYSTEM_PROMPT = """You are a helpful file assistant.
You can use tools to read, list, search and write resume files.
Always use tools when user asks about files.
After using tools, give a short simple summary to the user.
Resumes are stored in the 'resumes' folder.
"""


def get_client():
    """Create OpenRouter client. Returns None if no API key."""
    # Support OPENROUTER_API_KEY, fallback to OPENAI_API_KEY just in case
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    from openai import OpenAI

    # OpenRouter uses OpenAI-compatible API
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def ask_assistant(user_query: str, max_steps: int = 5) -> str:
    """
    Send one user query to LLM, let it call tools, return final answer.

    Args:
        user_query: e.g. "Read all resumes in the resumes folder"
        max_steps: max tool-call rounds (to avoid infinite loop)

    Returns:
        Final text answer from LLM.
    """
    client = get_client()
    if client is None:
        return "ERROR: OPENROUTER_API_KEY not found. Please check your .env file."

    model = os.getenv("OPENROUTER_MODEL") or os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")

    # Chat history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    # Loop: LLM -> tool call -> tool result -> LLM -> ...
    for _ in range(max_steps):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message
        messages.append(msg)  # save LLM reply in history

        # If LLM did not call any tool, we are done
        if not msg.tool_calls:
            return msg.content

        # LLM called one or more tools, run them one by one
        print(f"\n[Tool calling] LLM wants to call {len(msg.tool_calls)} tool(s)...")
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"  -> {name}({args})")

            # Call our real python function
            func = AVAILABLE_FUNCTIONS[name]
            result = func(**args)

            # Send tool result back to LLM
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)[:4000],  # keep it short
                }
            )

    return "Stopped after too many tool steps. Please try a simpler query."


def main():
    """Simple chat loop in terminal."""
    print("=== LLM File Assistant ===")
    print("Examples:")
    print('  - "Read all resumes in the resumes folder"')
    print('  - "Find resumes mentioning Python experience"')
    print('  - "Create a summary file for resume_john_doe.txt"')
    print('Type "exit" to quit.\n')

    if get_client() is None:
        print("ERROR: OPENROUTER_API_KEY not found.")
        print("1. Copy .env.example to .env")
        print("2. Put your real OpenRouter key in .env")
        return

    while True:
        query = input("\nYou: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Bye!")
            break
        if query == "":
            continue

        answer = ask_assistant(query)
        print(f"\nAssistant: {answer}")


if __name__ == "__main__":
    main()
