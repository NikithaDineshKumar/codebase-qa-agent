import os
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_java as tsjava

# Supported file extensions
EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".java": "java",
}

# Language loaders
LANGUAGE_MAP = {
    "python": Language(tspython.language()),
    "javascript": Language(tsjavascript.language()),
    "java": Language(tsjava.language()),
}

def get_parser(language: str) -> Parser:
    parser = Parser(LANGUAGE_MAP[language])
    return parser

def extract_chunks(file_path: str, source_code: str, language: str) -> list[dict]:
    """
    Parses source code using AST and extracts function/class level chunks.
    Each chunk contains: content, file_path, start_line, end_line, chunk_type, name
    """
    chunks = []

    try:
        parser = get_parser(language)
        tree = parser.parse(bytes(source_code, "utf-8"))
        root = tree.root_node

        node_types = {
            "python": ["function_definition", "class_definition"],
            "javascript": ["function_declaration", "class_declaration", "arrow_function", "method_definition"],
            "java": ["method_declaration", "class_declaration"],
        }

        target_types = node_types.get(language, [])
        lines = source_code.split("\n")

        def traverse(node):
            if node.type in target_types:
                start_line = node.start_point[0]
                end_line = node.end_point[0]
                chunk_text = "\n".join(lines[start_line:end_line + 1])

                # Try to get name of the function/class
                name = "unknown"
                for child in node.children:
                    if child.type == "identifier":
                        name = child.text.decode("utf-8")
                        break

                chunks.append({
                    "content": chunk_text,
                    "file_path": file_path,
                    "start_line": start_line + 1,
                    "end_line": end_line + 1,
                    "chunk_type": node.type,
                    "name": name,
                    "language": language,
                })

            for child in node.children:
                traverse(child)

        traverse(root)

    except Exception as e:
        print(f"AST parsing failed for {file_path}: {e}")

    # Fallback: if no chunks extracted, treat whole file as one chunk
    if not chunks:
        chunks.append({
            "content": source_code,
            "file_path": file_path,
            "start_line": 1,
            "end_line": len(source_code.split("\n")),
            "chunk_type": "file",
            "name": os.path.basename(file_path),
            "language": language,
        })

    return chunks


def parse_repo(repo_path: str) -> list[dict]:
    """
    Walks through all files in the repo and extracts AST chunks.
    """
    all_chunks = []
    skipped = []

    for root, dirs, files in os.walk(repo_path):
        # Skip hidden folders and common non-code folders
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                   ["node_modules", "__pycache__", ".git", "venv", "dist", "build"]]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in EXTENSION_MAP:
                continue

            language = EXTENSION_MAP[ext]
            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    source_code = f.read()

                if not source_code.strip():
                    continue

                chunks = extract_chunks(file_path, source_code, language)
                all_chunks.extend(chunks)
                print(f"Parsed {file_path} → {len(chunks)} chunks")

            except Exception as e:
                skipped.append(file_path)
                print(f"Skipped {file_path}: {e}")

    print(f"\nTotal chunks extracted: {len(all_chunks)}")
    print(f"Skipped files: {len(skipped)}")
    return all_chunks