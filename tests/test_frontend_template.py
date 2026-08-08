import re
import shutil
import subprocess
from pathlib import Path

import pytest


def test_index_inline_javascript_parses(tmp_path):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")

    root = Path(__file__).resolve().parents[1]
    html = (root / "backend" / "templates" / "index.html").read_text(encoding="utf-8")
    inline_scripts = [
        match.group(1)
        for match in re.finditer(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.DOTALL | re.IGNORECASE)
        if match.group(1).strip()
    ]

    script_path = tmp_path / "index-inline.js"
    script_path.write_text("\n".join(inline_scripts), encoding="utf-8")

    result = subprocess.run(
        [node, "--check", str(script_path)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
