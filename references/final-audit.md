# Final audit

## Coverage

- Count source files before work and final files after work.
- Confirm every intended source has exactly one disposition: unchanged, renamed, or included as a PDF page.
- Confirm instruction files and unrelated artifacts were excluded.
- For image PDFs, compare page count with source-image count and inspect the page manifest for gaps, duplicates, and natural-sort errors such as `1, 10, 2`.

## Content and names

- Verify document type, number, date, subject, period, address, and parties against the visible document.
- Recheck every content-versus-filename discrepancy.
- Confirm every final filename states the actual leaf count.
- Confirm `без даты` is used only where a reliable date was not established.
- Confirm no invalid Windows filename characters, reserved names, duplicates, or excessively long names remain.

## PDF integrity and visual QA

- Reopen the written PDF using a PDF parser.
- Render every page using Poppler or the bundled PDF workflow.
- Inspect for clipping, unexpected blank pages, missing glyphs, black squares, low-resolution regressions, stretched images, repeated pages, and missing pages.
- Compare the rendered first and last pages with the requested first and last source files.
- Preserve source orientation unless rotation is explicitly requested or clearly needed for usability; never crop document content.

## Safe delivery

- Before writing outside the workspace, resolve the exact destination and obtain any required approval.
- Replace a prior deliverable only when the user requested the change and the new version has passed QA.
- Compare SHA-256 hashes when copying the same deliverable to two locations.
- Do not delete source documents unless the user explicitly requests deletion.

## Completion report

State the number of renamed files, the final PDF page count, the exact source order, the destination, and any neutral or `без даты` decisions. Do not claim completion from a dry run, preview, or staging file.
