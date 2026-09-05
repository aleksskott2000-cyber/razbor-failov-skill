#!/usr/bin/env python3
"""Run a portable smoke test without touching user files."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


HERE = Path(__file__).resolve().parent


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="razbor-failov-") as temp_name:
        root = Path(temp_name)
        images = root / "images"
        images.mkdir()
        for number, color in [(1, "red"), (2, "green"), (10, "blue")]:
            Image.new("RGB", (320, 240), color).save(images / f"photo_{number}.jpg")

        pdf = root / "reverse.pdf"
        manifest = root / "manifest.json"
        run(str(HERE / "build_image_pdf.py"), str(images), str(pdf), "--order", "desc", "--manifest", str(manifest))
        sources = [item["source"] for item in json.loads(manifest.read_text(encoding="utf-8"))]
        assert sources == ["photo_10.jpg", "photo_2.jpg", "photo_1.jpg"]
        assert len(PdfReader(str(pdf)).pages) == 3

        rename_root = root / "rename"
        rename_root.mkdir()
        (rename_root / "a.pdf").write_bytes(b"a")
        (rename_root / "b.pdf").write_bytes(b"b")
        plan = root / "rename.json"
        plan.write_text(json.dumps([{"old": "a.pdf", "new": "b.pdf"}, {"old": "b.pdf", "new": "a.pdf"}]), encoding="utf-8")
        run(str(HERE / "apply_rename_plan.py"), str(rename_root), str(plan))
        run(str(HERE / "apply_rename_plan.py"), str(rename_root), str(plan), "--apply")
        assert (rename_root / "a.pdf").read_bytes() == b"b"
        assert (rename_root / "b.pdf").read_bytes() == b"a"

    print("razbor-failov self-test passed")


if __name__ == "__main__":
    main()
