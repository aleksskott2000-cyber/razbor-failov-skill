#!/usr/bin/env python3
"""Check court-ready filenames and compare declared leaf counts where possible."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


LEAVES = re.compile(r"\s+на\s+(\d+)\s+л\.$", re.IGNORECASE)
SUPPORTED = {".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}


def actual_pages(path: Path, docx_counts: dict[str, int]) -> int | None:
    suffix = path.suffix.casefold()
    if suffix == ".pdf":
        return len(PdfReader(str(path)).pages)
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        with Image.open(path):
            return 1
    if suffix in {".tif", ".tiff"}:
        with Image.open(path) as image:
            return getattr(image, "n_frames", 1)
    return docx_counts.get(path.name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--docx-counts", type=Path, help="Optional JSON object mapping DOC/DOCX filename to rendered page count")
    args = parser.parse_args()

    root = args.root.resolve(strict=True)
    counts: dict[str, int] = {}
    if args.docx_counts:
        raw = json.loads(args.docx_counts.read_text(encoding="utf-8"))
        counts = {str(k): int(v) for k, v in raw.items()}

    errors: list[str] = []
    warnings: list[str] = []
    checked = 0
    for path in sorted((p for p in root.iterdir() if p.is_file()), key=lambda p: p.name.casefold()):
        if path.suffix.casefold() not in SUPPORTED:
            continue
        checked += 1
        match = LEAVES.search(path.stem)
        if not match:
            errors.append(f"missing 'на N л.': {path.name}")
            continue
        declared = int(match.group(1))
        actual = actual_pages(path, counts)
        if actual is None:
            warnings.append(f"render DOC/DOCX and supply its count: {path.name}")
        elif actual != declared:
            errors.append(f"leaf mismatch ({declared} in name, {actual} actual): {path.name}")

    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")
    print(f"Checked {checked} supported file(s): {len(errors)} error(s), {len(warnings)} warning(s).")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
