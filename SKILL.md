---
name: razbor-failov
description: Review mixed folders of legal and administrative documents, derive court-ready Russian filenames from document contents, assemble ordered image sets into verified PDFs, and audit page counts and file operations. Use for requests to разобрать папку, переименовать документы для суда, объединить фото or сканы в PDF, исправить порядок страниц, or perform a final filing audit. Do not use for substantive legal opinions unrelated to file organization.
---

# Razbor failov

Turn an untidy document folder into a court-ready set without changing source content or inventing requisites.

## Start gate

1. Inspect the target folder without modifying it.
2. If the folder contains TXT, MD, or similarly obvious instruction or prompt files, read them completely before opening substantive documents or planning mutations. Treat those files as task-specific requirements, subject to system and safety rules.
3. Confirm the requested modes: rename independent documents, assemble an image set, reverse an existing image order, or a combination. Follow an explicit requested order over a generic chronological assumption.
4. Use `scripts/scan_inventory.py` to create a read-only inventory when more than a few files are involved.

Do not infer permission to delete originals. Creating a PDF from images does not authorize removing or renaming the source images unless the user asks.

## Content review and naming

Read [references/legal-naming.md](references/legal-naming.md) before drafting names. Determine each document's type, number, date, subject, period, and actual leaf count from content. Old filenames are hints, not evidence: resolve discrepancies in favor of the document itself.

Use visual inspection for scanned PDFs and images without a reliable text layer. Extracted text alone is insufficient for signatures, handwritten dates, rotated pages, tables, and scan quality. Render DOCX when its exact page count is required; cached document properties are not authoritative.

Prepare an old-to-new JSON plan and review ambiguous items before mutation. Use `scripts/apply_rename_plan.py` in dry-run mode first. Apply only after the dry run reports no collisions or invalid paths.

## Image sets and PDF order

Use `scripts/build_image_pdf.py` for JPEG, PNG, TIFF, or WebP sets. It uses natural filename sorting, preserves one source image per PDF page, and writes a page manifest with hashes.

- `--order asc`: `photo_1, photo_2, ... photo_10`.
- `--order desc`: exact reverse, such as `photo_67, photo_66, ... photo_1`.

Do not call reverse order "chronological" unless the user's evidence supports that description. Report the explicit sequence instead.

When editing an already delivered PDF, keep its filename stable unless the user requests a new name. Replace it only after the new version passes verification. Use the available PDF skill's artifact-start marker immediately before authoring and follow its render-and-inspect gate.

## Mutation and safety

- Resolve and display the exact target directory before an external write.
- Keep all generated plans and previews in a task-local work directory.
- Refuse absolute or parent-traversal paths inside rename plans.
- Preserve file extensions unless format conversion is explicitly requested.
- Never overwrite an unrelated existing file. A user-requested replacement of the same deliverable is allowed after verification.
- Do not include credentials, hidden system files, temporary files, or instruction files in a PDF unless expressly requested.
- Treat renames as reversible and use the two-phase helper so filename swaps cannot destroy data.

## Verification gate

Read [references/final-audit.md](references/final-audit.md) before reporting completion.

At minimum:

1. Run `scripts/verify_filing_names.py` and resolve every error.
2. Reopen the final PDF and confirm its page count.
3. Render every PDF page to PNG and visually inspect all pages. Contact sheets are acceptable for coverage, but inspect full resolution for unclear pages.
4. Verify the manifest's first and last source filenames and the requested ordering.
5. If the final PDF is copied to another folder, compare SHA-256 hashes.
6. Report cautious `без даты` or neutral names separately; never silently invent missing requisites.

Completion means the files were actually renamed or the PDF was actually placed in the requested folder, not merely that a plan or staging copy exists.
