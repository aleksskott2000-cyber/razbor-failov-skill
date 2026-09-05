#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}


def natural_key(value: str):
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build one-page-per-image PDF using natural filename order.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--order", choices=("asc", "desc"), default="asc")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--title", default="Image document set")
    args = parser.parse_args()
    source_dir = args.input_dir.resolve()
    files = sorted((p for p in source_dir.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS), key=lambda p: natural_key(p.name))
    if args.order == "desc":
        files.reverse()
    if not files:
        raise RuntimeError("No supported images found")
    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(args.output_pdf), pagesize=A4, pageCompression=1)
    pdf.setTitle(args.title)
    manifest = []
    margin = 14
    for page_number, path in enumerate(files, 1):
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            page_size = landscape(A4) if image.width > image.height else portrait(A4)
            page_w, page_h = page_size
            pdf.setPageSize(page_size)
            scale = min((page_w - 2 * margin) / image.width, (page_h - 2 * margin) / image.height)
            draw_w, draw_h = image.width * scale, image.height * scale
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=96, subsampling=0)
            buffer.seek(0)
            pdf.drawImage(ImageReader(buffer), (page_w - draw_w) / 2, (page_h - draw_h) / 2, draw_w, draw_h)
            pdf.showPage()
        manifest.append({"page": page_number, "source": path.name, "sha256": sha256(path)})
    pdf.save()
    from pypdf import PdfReader

    actual = len(PdfReader(str(args.output_pdf)).pages)
    if actual != len(files):
        raise RuntimeError(f"PDF has {actual} pages for {len(files)} source images")
    manifest_path = args.manifest or args.output_pdf.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created {args.output_pdf}: {actual} pages; first={files[0].name}; last={files[-1].name}")


if __name__ == "__main__":
    main()
