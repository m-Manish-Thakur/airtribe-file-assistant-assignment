"""
main.py
Simple demo WITHOUT needing OpenAI key.
Shows all 4 tools working step by step.
Good for testing Part A before trying Part B.

Run: python main.py
"""

import fs_tools


def main():
    print("=== Part A: Core File System Tools Demo ===\n")

    # 1. LIST files
    print("1. Listing all files in 'resumes' folder...")
    files = fs_tools.list_files("resumes")
    print(f"   Found {len(files)} files:")
    for f in files:
        print(f"   - {f['name']} ({f['size_bytes']} bytes)")
    print()

    # 2. READ one file
    print("2. Reading resume_john_doe.txt...")
    data = fs_tools.read_file("resumes/resume_john_doe.txt")
    if data["success"]:
        print(f"   Success! Size: {data['size_bytes']} bytes")
        print(f"   First 200 chars: {data['content'][:200]}...\n")
    else:
        print(f"   Error: {data['error']}\n")

    # 3. SEARCH for Python
    print("3. Searching for 'Python' in all resumes...")
    for f in files:
        # only search in .txt files for this simple demo
        if f["name"].endswith(".txt"):
            result = fs_tools.search_in_file(f["path"], "Python")
            print(f"   - {f['name']}: {result['total_matches']} match(es)")
    print()

    # 4. WRITE a summary file
    print("4. Writing a summary file to 'output/summary.txt'...")
    summary = "Resume Summary\n==============\n"
    summary += f"Total files: {len(files)}\n"
    for f in files:
        summary += f"- {f['name']}\n"

    result = fs_tools.write_file("output/summary.txt", summary)
    print(f"   {result['message'] or result['error']}\n")

    print("Done! Check the output/ folder.")


if __name__ == "__main__":
    main()
