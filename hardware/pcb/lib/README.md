# keeb KiCad library

The project-specific footprints and symbols for the left and right boards. They are in KiCad 10 format. The left and right projects in `hardware/pcb/left/` and `hardware/pcb/right/` each add this library to their tables as:

```text
keeb  ${KIPRJMOD}/../lib/keeb.pretty     (footprints)
keeb  ${KIPRJMOD}/../lib/keeb.kicad_sym  (symbols)
```

The 3D model paths assume that layout too.

## Contents

| File | What it is | Status |
|---|---|---|
| `keeb.pretty/SW_Kailh_PG1316S_ViaInPad.kicad_mod` | PG1316S switch, with plated holes in every pad for back-side iron soldering | Written from the datasheet. **Check it against a real switch before ordering** (see below) |
| `keeb.pretty/XIAO_nRF52840_FaceDown.kicad_mod` | XIAO nRF52840 mounted face-down: castellated pads only, pin order mirrored | Pin grid, cutout, reset and antenna positions from Seeed's v1.1 KiCad layout and STEP model. Pin order cross-checked against chalk (below) |
| `keeb.pretty/Post_Locating_D1.0.kicad_mod` | Ø1.0 mm hole for a case locating pin, with the support post as a B.CrtYd circle | Written for this project |
| `keeb.pretty/SW_Slide_MSK-12C02.kicad_mod` | MSK-12C02 side slide power switch | From LCSC [C431540](https://www.lcsc.com/product-detail/C431540.html) via `easyeda2kicad`. Checked against the manufacturer's recommended land pattern (below). The body-peg holes are NPTH. The nub's outline is on F.Fab, because the nub overhangs the board edge |
| `keeb.3dshapes/MSK-12C02.step` | 3D model for the power switch | From LCSC |
| `keeb.kicad_sym` | `XIAO_nRF52840` symbol; pins 1–14 follow the Seeed pinout | Written for this project |

Stock KiCad parts cover the rest: `Switch:SW_Push` (switch symbol, pins 1/2), `Device:D` with `Diode_SMD:D_SOD-323_HandSoldering` (value 1N4148WS), `Switch:SW_SPDT` for the power switch, `Connector:TestPoint` with `TestPoint:TestPoint_Pad_1.5x1.5mm` for the battery and XIAO wire pads, and `Mechanical:MountingHole` for the locating holes.

The switch footprint's silk outline is broken around the four frame pads, and the XIAO's silk marks only the antenna end, so neither prints over copper or the cutout.

## PG1316S footprint: how it was checked

Every candidate footprint was compared against the [Kailh datasheet](https://docs.holykeebs.com/datasheets/CPG1316S01D02.pdf) land pattern:

| Feature | Datasheet | This footprint |
|---|---|---|
| Overall land extents | 14.70 × 14.00 mm | Same |
| Frame pads | 4 × 2 × 2 mm at (±6.35, ±6.00) | Same, plus a 0.8 mm plated hole. No net |
| Contact pads | 1.55 × 2 mm, 5.00 mm centre to centre (3.45 mm gap, 6.55 mm outer) at y = +2.65 | Outer edges as in the datasheet (±3.275); each pad extended **0.825 mm inward** to ±0.9. 0.8 mm plated hole at ±2.0 |
| Locating holes | Ø1.20 (+0.05/−0) at (5.80, −2.75) and Ø1.00 (+0.05/−0) at (−5.80, +2.75) | Ø1.25 and Ø1.05 NPTH, the top of the datasheet tolerance, to allow for the fab's drill tolerance |
| Courtyard | — | 16.25 × 16.05 mm, the measured stock keycap |

**Why the contact pads are wider than the datasheet's.** Community footprints disagree on where the contacts sit:

| Source | Contact pad centres |
|---|---|
| Kailh datasheet, [kumekay/aronia](https://github.com/kumekay/aronia), [dennisleexyz/libmodulo](https://github.com/dennisleexyz/libmodulo), [yuvalabou/inpulib](https://github.com/yuvalabou/inpulib), [DreaM117er/keebLibrary](https://github.com/DreaM117er/DreaM117er-keebLibrary), Mikefive spec-sheet | ±2.5 |
| [vuoz/chalk](https://github.com/vuoz/chalk) (a built and working PG1316S board) | ±1.5 |
| Mikefive reversible | ±1.55 |
| [ebastler/marbastlib](https://github.com/ebastler/marbastlib) | −2.5 / +1.8 |

The widened pads cover both the datasheet position and chalk's, and the plated hole sits in the overlap (±2.0). The Kailh STEP model doesn't model the terminals clearly enough to decide this. **To settle it, look at the underside of a real switch, or the Holykeebs practice board.** If the terminals clearly sit at ±2.5, shrink the pads back to the datasheet size.

## MSK-12C02 footprint: how it was checked
The [manufacturer's datasheet](https://www.lcsc.com/product-detail/C431540.html) (Shouhan, 2024-12-14, page 1) gives a recommended land pattern. The footprint is that pattern turned 180°:

| Feature | Datasheet | This footprint |
|---|---|---|
| Pins | 0.6 × 1.3 mm, at x = −2.25, −0.75, +2.25 | 0.6 × 1.524 mm, at +2.25, +0.75, −2.25 (turned 180°) |
| Body pegs | 2 × Ø0.85 mm holes, 3 mm apart (pegs are Ø0.75 ± 0.1) | Ø0.9 mm NPTH, 3 mm apart |
| Mounting tabs | 1.05 × 0.7 mm, outer edges 8.4 mm apart (±4.2), rows 2.2 mm apart | 1.2 × 0.7 mm, outer edges ±4.2, rows 2.3 mm apart |

The tab rows differ by 0.1 mm, which reflow pulls into line. This also settles the earlier mismatch with ceoloide's footprint, which put the tabs about 0.5 mm off: ours matches the datasheet. It is also the footprint from JLCPCB's own EasyEDA library, which is what their placement is set up against.

## XIAO footprint notes
- Face-down, the XIAO's back faces up. Seen from above, **D0 is top-right** next to USB-C, and 5V is top-left.
- The 5V and 3V3 pads stay unconnected on our boards. The battery is wired by hand to the XIAO's BAT+ back pad, which faces up. GND is connected, so the board's ground pour shares the XIAO's ground.
- The footprint has no 3D model. A face-down Seeed model would need custom flipping.
- **Where the numbers come from.** Seeed publishes a [STEP model](https://files.seeedstudio.com/wiki/XIAO-BLE/seeed-studio-xiao-nrf52840-3d-model.zip) (older board, with a shielded module) and the [v1.1 KiCad project](https://files.seeedstudio.com/wiki/XIAO-BLE/Seeed-Studio-XIAO-nRF52840V1.1-KiCad-Project-260105.zip) (current board, chip-down). The cutout covers both:

  | Measurement | Value |
  |---|---|
  | Board | 20.96 × 17.78 × 1.24 mm, with the pin grid centred on it (2.86 mm from each end to the end pins) |
  | Tallest part | USB-C, 3.21 mm off the XIAO board, overhanging the USB end by 1.53 mm. The older module is 10.6 × 12.6 × 2.0 mm. Nothing else is over 1 mm |
  | Lateral spread | Within ±6.6 mm of the centreline, except a 0.3 mm-tall capacitor reaching ±7.4 mm, 0.5–1.0 mm from the antenna end |
  | Along the board | Parts run to within 0.2 mm of the antenna end |
  | Antenna | Chip antenna at the end opposite USB-C, on the D0 side |
  | Reset button | D0 side, centred 1.9 mm from the USB-C end and 5.7 mm off the centreline |

- **Cross-check against chalk.** [vuoz/chalk](https://github.com/vuoz/chalk)'s `xiao_nRF52840_new.js` has a back-side variant: the same mirrored XIAO seen from above. Its pin order matches ours pad for pad: P0 at (+x, USB-C end), 5V at (−x, USB-C end), GND next to 5V, P7 at (−x, antenna end). Both use a 2.54 mm pitch with the rows at ±7.62 mm. Chalk's pads sit at ±9.2 mm and are 1.3 mm long; ours sit at ±8.34 mm and are 2.3 mm long, reaching further under the module (to ±7.2 mm, clear of its parts at ±6.6 mm).
- **Cutout** (Dwgs.User): ±6.8 mm wide for the full length, from past the USB-C end to 0.2 mm past the antenna end. At the antenna end it widens to ±7.6 mm for the last 1.7 mm to clear that capacitor. That leaves at least 0.38 mm of board between the cutout and the pads. Copy it onto Edge.Cuts, open at the USB-C end.
- **Antenna keep-out:** a rule area bans tracks, vias and copper pour on both layers for 5 mm past the antenna end. Across the board it covers the antenna chip (−0.15 to 3.75 mm in footprint x) plus 5 mm on the −x side and 4.25 mm on the +x side, not the XIAO's full width. That leaves room for tracks to pass beside it.
