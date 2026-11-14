# Build readiness

**Design in progress — not a validated build kit.** The repository contains editable PCBs, fabrication snapshots and concept assemblies. Reorganization did not regenerate or certify them.

| Area | Present | Still needed before a complete build |
|---|---|---|
| PCB | Separate routed KiCad left/right projects and custom library | Fresh ERC/DRC reports, physical footprint check, export-to-source comparison |
| Fabrication | Gerbers, assembly BOM and CPL for both sides | Validate snapshots against the current source and fab requirements before ordering |
| Case | Parametric code, STEP/GLB concept assemblies | Correct right-side controller/reset geometry; printable separate left/right case files; fit coupons and physical testing |
| Firmware | Design instructions only | Buildable ZMK shield, per-side GPIO overlays, keymap, pinned build config and tested UF2 outputs |
| Battery | Placeholder 252030 class, 2.5 × 20 × 30 mm | Exact protected cell, dimensions including protection board and leads, verified clearance |
| Height and fit | Nominal 7 mm budget with no margin | Real switch/keycap measurements, USB cable clearance, snap retention and battery clearance |

The 17 mm open tray is the selected design. The 18 mm enclosed model is a comparison concept and does not match the selected PCB pitch. Both are **concept assemblies**, not print-ready cases. The CAD mirrors the left controller, whereas the actual right PCB rotates it; its reset pinhole must be checked and corrected in future mechanical work.

## Evidence and discrepancies

- Historical notes claim clean ERC/DRC apart from four expected power-switch peg warnings. No saved reports are included; this migration does not establish fresh results.
- The routed design uses different left/right GPIO maps. The earlier shared-map claim has been corrected.
- The old HTML described a 2.0 mm PCB tab; the Markdown and generator describe a 1.1 mm tab. Use the actual board outline when completing the case; no geometry was changed here.
- The old HTML estimated 2–2.5 hours for charging. This was an unverified estimate, not a measured result; validate with the selected cell and controller.
- Supplier prices, availability and manufacturing capabilities in the chapters are historical notes, not current quotations.
- Phase checkboxes are personal browser notes, not engineering verification records.

## Existing downloads

See the [artifact catalog](../../exports/README.md) for source and regeneration commands. These snapshots are preserved unchanged:

- [Left Gerbers](../../exports/pcb/left/left-gerbers.zip), [assembly BOM](../../exports/pcb/left/left-bom.csv), [CPL](../../exports/pcb/left/left-cpl.csv)
- [Right Gerbers](../../exports/pcb/right/right-gerbers.zip), [assembly BOM](../../exports/pcb/right/right-bom.csv), [CPL](../../exports/pcb/right/right-cpl.csv)
- Tray concept: [STEP](../../exports/models/tray/keyboard.step), [GLB](../../exports/models/tray/keyboard.glb), [metadata](../../exports/models/tray/keyboard.json)
- Enclosed alternative: [STEP](../../exports/models/enclosed/keyboard-enclosed.step), [GLB](../../exports/models/enclosed/keyboard-enclosed.glb), [metadata](../../exports/models/enclosed/keyboard-enclosed.json)
