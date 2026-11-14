# Artifact catalog

These are preserved design snapshots, not certified manufacturing releases. Their correspondence to the current sources has not been revalidated. Do not order directly from them without the [readiness checks](../buildbook/chapters/readiness.md).

Run commands from the repository root. `KICAD_PYTHON` below means the Python interpreter bundled with KiCad 10 (on macOS: `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`). KiCad scripts also require `kicad-cli` on PATH, or the documented macOS installation. CAD uses Python 3.12 and build123d; no tested dependency lock for the historical hardware toolchain exists yet.

| Files | Purpose and source | Regeneration | Status |
|---|---|---|---|
| `pcb/left/*`, `pcb/right/*` | Gerbers/drills ZIP, bottom assembly BOM and CPL from matching `hardware/pcb/<side>/` | `"$KICAD_PYTHON" hardware/pcb/fab.py` | Preserved snapshots; source parity unverified |
| `models/tray/*` | Selected 17 mm concept STEP/GLB and dimensional JSON from `hardware/case/keyboard.py` | `uv run --python 3.12 --with build123d python hardware/case/keyboard.py tray` | Concept; right-side mirror mismatch; not printable per-half exports |
| `models/enclosed/*` | Alternative 18 mm concept exports from the same CAD | Same command with `enclosed` | Comparison only; incompatible with selected PCB pitch |
| `../buildbook/assets/pcb-*` | Board routing and underside illustrations | `"$KICAD_PYTHON" hardware/pcb/render.py` | Historical renders; not new check evidence |
| Other `../buildbook/assets/*` | Concept beauty renders | Build CAD, then `npm run build`, then `node hardware/case/render.mjs` | Requires Playwright Chromium and network for Three.js; run website build again afterward |

Editable KiCad projects are authoritative. `generate.py` is a one-time bootstrap; `--force` discards routing. `route.py` deletes and replaces existing tracks. Neither is part of the site build or export verification.

Binary GLBs replace the old base64 text copies, whose decoded bytes were checked identical before removal. Existing STEP, GLB, JSON, fabrication and render bytes were retained. No STL/3MF production cases or firmware binaries exist yet.
