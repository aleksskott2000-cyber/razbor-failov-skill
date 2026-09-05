#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def natural_key(value: str):
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a read-only inventory of a document folder.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--text-pages", type=int, default=3)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    rows = []
    for index, path in enumerate(sorted((p for p in root.iterdir() if p.is_file()), key=lambda p: natural_key(p.name)), 1):
        row = {"index": index, "name": path.name, "extension": path.suffix.lower(), "bytes": path.stat().st_size}
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            row["pages"] = len(reader.pages)
            row["text_sample"] = "\n".join((page.extract_text() or "") for page in reader.pages[: args.text_pages])[:5000]
        elif path.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}:
            from PIL import Image

            with Image.open(path) as image:
                row["width"], row["height"] = image.size
        elif path.suffix.lower() == ".docx":
            from docx import Document

            doc = Document(str(path))
            row["text_sample"] = "\n".join(p.text for p in doc.paragraphs)[:10000]
            row["page_count_note"] = "Render the DOCX; cached metadata is not authoritative."
        rows.append(row)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Inventoried {len(rows)} files into {args.out}")


if __name__ == "__main__":
    main()

