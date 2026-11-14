# 04 — Case (3D printed)

## Design approach
- **Parametric CAD in code**, so it stays reproducible and can be driven by Claude. Use [build123d](https://github.com/gumyr/build123d), which has an MCP server (see [resources](resources.md#mcp--ai-tooling)). OpenSCAD is an alternative.
- Export the board outline from KiCad (`kicad-cli pcb export dxf --layers Edge.Cuts`) and check it against the case, so the case always matches the PCB.
- Expose these as parameters: key pitch, PCB thickness, battery L × W × T, wall thickness, and floor thickness.
- The concept model is [`hardware/case/keyboard.py`](../../hardware/case/keyboard.py). It builds both halves with placeholder switches, the XIAO and the battery, and exports STEP and GLB. Pass `enclosed` to build the Designer-style concept instead: a top shell with a deck around every key on a flat bottom plate, at 18 mm pitch, because the deck webs need room. It is a comparison, not the locked design. The viewer switches between the two with the **Case** buttons. It prints clearance checks after each build. After generating CAD, run `npm run build`, then `node hardware/case/render.mjs` to regenerate the renders in [`buildbook/assets/`](../assets/) from the viewer (it needs `playwright`).

## Switch and keycap models
Use the collected [PG1316S STEP and keycap assets](../../references/pg1316s/README.md) to preview switch clearance and case height. The original Kailh assembly model has a reported undersized keycap exterior; use the measured 16.25 × 16.05 mm outer cap dimensions for initial spacing and confirm with the Holykeebs caps before finalizing the case. The separate custom keycap STEP is an alternate shape, not the selected stock cap.

## Structure
```
  keycaps ─────────▄▄▄▄  ▄▄▄▄  ▄▄▄▄
  switches ────────████  ████  ████
  PCB (0.8 mm) ═══════════════════════════  ← rests on ledge in wall
  diodes / battery ─  ▪    [ battery ]  ▪
  floor (0.8 mm; open under the battery) ▔▔▔▔▔▔▔▔▔▔▔▔
```
- It is a **tray**: the floor and walls are one piece, with soft rounded edges and 6 mm plan-view corner radii. The PCB drops in and sits on a perimeter ledge.
- **Floating keys.** The wall rises only to the PCB top surface, so the switches and keycaps stand proud. There is no top deck, because at 17 mm pitch the webs would be about 0.15 mm.
- **Retention: snap lip.** A lip 0.5 mm deep and 0.4 mm tall runs along the inside top of both long walls. It overlaps the PCB edge by 0.3 mm and clears the caps by 0.17 mm in plan. The PCB clips in under it and can be pried out for rework. The bottom lip starts just past the PCB tab under the XIAO, and the bottom wall's lip now sits 2.6 mm below the thumb caps. Print in PETG or a tough resin so the lip flexes instead of snapping.
- **Mirrored halves.** The left and right PCBs are mirror-image layouts, so the trays are mirror images too.
- **Support:** a Ø2.4 mm post under each key centre, except over the battery. Two extra posts at four-key corners carry Ø0.9 mm locating pins that pass through the PCB's Ø1.0 mm holes and stop flush with its top, so the board can't slide sideways.
- **Cutouts:** USB-C on the outer edge (it sits low, because the XIAO is face-down), a **reset pinhole** in the floor under the XIAO's button, and the power switch slot.
- **Size:** 90.4 × 76.0 mm per half. The PCB's bottom edge runs 2.6 mm past the key grid, to make room for the XIAO's fan-out tracks.
- **PCB tab pocket:** under the XIAO, a 1.1 mm tab sticks out past that edge, so the bottom wall has a matching 0.8 mm-deep pocket. That leaves 1.4 mm of wall outside it, and the wall below the pocket stays full height.
- **Power switch slot:** the switch hangs under the PCB at the top edge, under the outer top key. The ledge is cut away under its body, and a 4 mm slot through the top wall exposes the nub, which sits about 1.6 mm in from the outer face. Slide it with a fingernail or a toothpick.
- **USB-C pocket:** the face-down XIAO's USB-C ends 2.4 mm below the PCB, which is deeper than the 1.9 mm cavity. The floor under it is thinned to 0.2 mm.
- **Reset pinhole:** under the XIAO's button, 1.9 mm in from the USB-C end on the XIAO's D0 side. On the left half that side faces the keys. The right board rotates the XIAO instead of mirroring it, so on the right half the pinhole is on the side away from the keys. The concept model mirrors the left half, so it doesn't show this yet.
- **Battery pocket** goes **through the floor** and is covered with Kapton or a sticker. That saves about 0.8 mm. Hold the cell with Kapton tape, and never compress it.
- Put rubber feet in recessed pockets so they don't add height.

## Print settings
| Method | Notes |
|---|---|
| Resin (SLA) | Best for 0.8 mm floors and crisp cutouts |
| FDM, 0.2–0.4 mm nozzle | PETG or PLA+, 0.1–0.12 mm layers, print floor-down |
| JLC3DP / PCBWay 3D | Resin or MJF, good once the design is stable |

Iterate cheaply: print a **single-key test coupon** and a **PCB-edge fit test** before you print a full half.

## Checklist
- [ ] PCB fits with about 0.2 mm clearance per side, and snaps under the lip without cracking it
- [ ] Battery pocket depth ≥ cell thickness + 0.1 mm
- [ ] USB-C cable plugs in fully (check the plug overmold clearance)
- [ ] Total height measured with calipers and recorded here
