#!/usr/bin/env python3
"""Validate and safely apply a JSON rename plan inside one directory."""

from __future__ import annotations

import argparse
import json
import os
import uuid
from pathlib import Path


def leaf_name(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    value = value.strip()
    if Path(value).name != value or "/" in value or "\\" in value or value in {".", ".."}:
        raise ValueError(f"{field} must be a filename, not a path: {value!r}")
    return value


def load_plan(path: Path) -> list[tuple[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("rename plan must be a non-empty JSON array")
    pairs: list[tuple[str, str]] = []
    for index, item in enumerate(data, 1):
        if not isinstance(item, dict):
            raise ValueError(f"item {index} must be an object")
        old = leaf_name(item.get("old"), f"item {index}.old")
        new = leaf_name(item.get("new"), f"item {index}.new")
        if Path(old).suffix.casefold() != Path(new).suffix.casefold():
            raise ValueError(f"extension change is forbidden: {old!r} -> {new!r}")
        pairs.append((old, new))
    return pairs


def validate(root: Path, pairs: list[tuple[str, str]]) -> None:
    root = root.resolve(strict=True)
    old_keys = [old.casefold() for old, _ in pairs]
    new_keys = [new.casefold() for _, new in pairs]
    if len(old_keys) != len(set(old_keys)):
        raise ValueError("duplicate source filename in plan")
    if len(new_keys) != len(set(new_keys)):
        raise ValueError("duplicate target filename in plan")
    source_keys = set(old_keys)
    for old, new in pairs:
        source = root / old
        target = root / new
        if not source.is_file():
            raise FileNotFoundError(f"source does not exist: {source}")
        if target.exists() and new.casefold() not in source_keys:
            raise FileExistsError(f"target already exists and is not being renamed: {target}")


def apply(root: Path, pairs: list[tuple[str, str]]) -> None:
    root = root.resolve(strict=True)
    staged: list[tuple[Path, Path, Path]] = []
    try:
        for old, new in pairs:
            source = root / old
            target = root / new
            while True:
                temp = root / f".razbor-{uuid.uuid4().hex}.tmp"
                if not temp.exists():
                    break
            os.replace(source, temp)
            staged.append((source, temp, target))
        for source, temp, target in staged:
            os.replace(temp, target)
    except Exception:
        for source, temp, target in reversed(staged):
            if temp.exists() and not source.exists():
                os.replace(temp, source)
            elif target.exists() and not source.exists():
                os.replace(target, source)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Directory containing the files")
    parser.add_argument("plan", type=Path, help='UTF-8 JSON array of {"old": ..., "new": ...}')
    parser.add_argument("--apply", action="store_true", help="Apply after validation; default is dry-run")
    args = parser.parse_args()

    pairs = load_plan(args.plan)
    validate(args.root, pairs)
    for old, new in pairs:
        print(f"{old} -> {new}")
    if args.apply:
        apply(args.root, pairs)
        print(f"Applied {len(pairs)} rename(s).")
    else:
        print(f"Dry-run passed for {len(pairs)} rename(s). Use --apply to commit.")


if __name__ == "__main__":
    main()
