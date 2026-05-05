from __future__ import annotations

import ast
import re
from pathlib import Path


CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
}


IMPORT_PATTERNS = {
    ".js": (r"^\s*import\s+.+?\s+from\s+['\"]([^'\"]+)['\"]", r"require\(['\"]([^'\"]+)['\"]\)"),
    ".jsx": (r"^\s*import\s+.+?\s+from\s+['\"]([^'\"]+)['\"]", r"require\(['\"]([^'\"]+)['\"]\)"),
    ".ts": (r"^\s*import\s+.+?\s+from\s+['\"]([^'\"]+)['\"]", r"require\(['\"]([^'\"]+)['\"]\)"),
    ".tsx": (r"^\s*import\s+.+?\s+from\s+['\"]([^'\"]+)['\"]", r"require\(['\"]([^'\"]+)['\"]\)"),
    ".java": (r"^\s*import\s+([\w.*]+)\s*;",),
    ".kt": (r"^\s*import\s+([\w.*]+)",),
    ".go": (r"^\s*import\s+(?:\(\s*)?[`\"]([^`\"]+)[`\"]",),
    ".rs": (r"^\s*use\s+([^;]+);",),
    ".rb": (r"^\s*require(?:_relative)?\s+['\"]([^'\"]+)['\"]",),
    ".php": (r"^\s*use\s+([^;]+);",),
    ".c": (r"^\s*#\s*include\s+[<\"]([^>\"]+)[>\"]",),
    ".h": (r"^\s*#\s*include\s+[<\"]([^>\"]+)[>\"]",),
    ".cc": (r"^\s*#\s*include\s+[<\"]([^>\"]+)[>\"]",),
    ".cpp": (r"^\s*#\s*include\s+[<\"]([^>\"]+)[>\"]",),
    ".hpp": (r"^\s*#\s*include\s+[<\"]([^>\"]+)[>\"]",),
    ".cs": (r"^\s*using\s+([\w.]+)\s*;",),
}


def is_code_file(path: Path) -> bool:
    return path.suffix.lower() in CODE_EXTENSIONS


def count_dependencies(path: Path) -> int:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0

    if path.suffix.lower() == ".py":
        return _count_python_dependencies(source)

    dependencies: set[str] = set()
    for pattern in IMPORT_PATTERNS.get(path.suffix.lower(), ()):
        dependencies.update(re.findall(pattern, source, flags=re.MULTILINE))
    return len(dependencies)


def _count_python_dependencies(source: str) -> int:
    dependencies: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            dependencies.add(node.module.split(".")[0])

    return len(dependencies)
