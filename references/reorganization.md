# Reorganization verification — 2026-11-14

The migration inventory accounted for all 75 original non-cache files: 51 remained byte-identical, 21 received documentation/path changes, and three were consolidated. This is a migration record, not a hardware certification.

- Both KiCad schematic and project files are byte-identical. Both PCB files differ only in the PG1316S model path, now resolving from their new project directories. No geometry, routing or net assignments changed.
- Existing Gerber ZIPs, BOM/CPL CSVs, STEP/GLB/JSON exports, third-party STEP files and render images were retained byte-for-byte.
- The two removed `.glb.txt` files decoded exactly to their corresponding retained binary GLBs.
- The old hand-maintained `docs/index.html` was consolidated into the Markdown chapters and presentation template. Its overview, interactive schematic, phase controls, gallery and viewer controls were retained. Existing Markdown supplied the detailed technical prose; HTML-specific discrepancies are recorded in build readiness. The duplicate numeric height visualization was replaced by the authoritative Markdown height-budget table.
- Library tables and available custom models resolve from both relocated KiCad project directories. All hardware Python scripts parse; no bootstrap, routing or CAD generation was run.
- Unavailable firmware, print-ready cases and external reference archives were documented, not fabricated or silently substituted.

The baseline checkpoint commit was undone at the user's request. The implementation remains uncommitted for final review.
