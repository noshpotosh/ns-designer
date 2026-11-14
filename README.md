# NS Designer

A 36-key ortholinear wireless split keyboard using Kailh PG1316S switches and two XIAO nRF52840 controllers. The selected design is a 17 mm-pitch open tray with a ≤7 mm height target. **It is not yet a validated, complete build kit.**

[Read the buildbook](https://noshpotosh.github.io/ns-designer/). Start with [build readiness](buildbook/chapters/readiness.md) before ordering parts.

## Read and edit

The authoritative text is in `buildbook/chapters/`. Edit Markdown there; the generated HTML is not tracked. Raw HTML in the overview and model chapters preserves interactive figures. Layout, styles and behavior live in `buildbook/template/`; the 3D viewer lives in `buildbook/viewer/`.

With Node.js 22 or newer:

```sh
npm ci
npm run check
npm run preview
```

Open http://localhost:8000/ns-designer/. `npm run build` generates `dist/index.html` with adjacent assets, viewer and downloads. Deploy the **entire dist directory**, not just the HTML. Preview uses a project prefix to catch GitHub Pages path issues. Google Fonts and the pinned Three.js CDN need network access; text, static renders and downloads remain available without them.

## Repository map

| Directory | What belongs here |
|---|---|
| `buildbook/` | Markdown chapters, presentation, static renders and viewer |
| `hardware/pcb/` | Editable left/right KiCad projects, project library, bootstrap/routing/export scripts |
| `hardware/case/` | Parametric concept CAD and render script |
| `references/` | Collected third-party assets and provenance catalog |
| `exports/` | Existing fabrication snapshots and concept models; see [catalog](exports/README.md) |
| `firmware/` | Missing-implementation notice; no buildable ZMK config yet |
| `scripts/` | Website build, preview and validation |

Open each `.kicad_pro` with KiCad 10 and its stock libraries installed. Custom libraries and available models resolve relative to the projects. The XIAO footprint has no 3D model. Firmware and printable per-half cases still need implementation; the right-side reset location and physical fit need validation.

## Hardware workflow

Hardware generation is **manual and separate** from publishing. See [artifact catalog](exports/README.md) for commands. Do not run `generate.py --force` or `route.py` to build the site: they overwrite design work. The committed KiCad projects are the editable source of truth; the bootstrap is not a lossless round-trip.

## GitHub Pages and checks

In repository Settings → Pages, select **GitHub Actions**. The workflow validates pull requests and deploys default-branch pushes (or a manual run on that branch). It uploads only `dist/`; it does not run KiCad or CAD tools. The expected site URL is linked above. Publishing becomes active after these changes are pushed and Pages is configured.

`npm run check` validates the bundle, local links/anchors, download inventory and KiCad relative references. For browser checks:

```sh
npx playwright install chromium
npm run check:browser
```

Browser checks cover desktop/mobile layouts, colorway controls, both 3D variants, and a blocked-CDN fallback. Browser and dependency downloads require network access. These checks do not certify electronics, fabrication output freshness, or mechanical fit.
