import py_compile
from pathlib import Path


def test_project_python_files_compile():
    root = Path(__file__).resolve().parents[1]
    failures = []

    for path in sorted(root.rglob("*.py")):
        rel_parts = path.relative_to(root).parts
        if any(part in {".venv", "venv", "__pycache__"} for part in rel_parts):
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            failures.append(f"{path.relative_to(root)}: {exc}")

    assert failures == []
