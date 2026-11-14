# 05 — Assembly & test

Practise first. The [Holykeebs PG1316S practice board](https://holykeebs.com/products/pg1316s-practice-board) is cheap, and these switches are close to impossible to desolder.

## How hard it is
Intermediate. It's harder than a through-hole keyboard kit, but you need no hot plate, stencil or microscope. Expect about 340 joints for the whole keyboard, or roughly 3–5 unhurried hours per half the first time.

| Part (per keyboard) | Joints | Difficulty | Notes |
|---|---|---|---|
| 36 diodes, SOD-323, back | 72 | Easy–moderate | Hand-solder pads (1 × 1 mm). Use tweezers and flux, and check orientation |
| 36 PG1316S switches | 216 (6 each) | Moderate, unforgiving | Heat each pad from the back through its plated hole, so solder wicks to the switch. Kailh allows 280 °C for 3 s, and a soldered switch is close to impossible to remove |
| 2 XIAO nRF52840, face-down | 28 | **Hardest** | You can't see under it, and it's hard to remove. The board's pads stick out about 0.6 mm past its edge, which gives the iron access |
| 2 power switches, MSK-12C02 | 14 | Moderate | 0.6 mm pins and a plastic body that melts if you linger |
| 2 batteries | 6 + 2 wires | Moderate | Tiny BAT+ pad on the XIAO. A LiPo short is dangerous |

### JLCPCB places the back-side parts (the plan)
The diodes and the power switch are the only parts on the back (B.Cu), and both are LCSC parts: the 1N4148WS ([C2128](https://jlcpcb.com/partdetail/1N4148WS/C2128), basic library) and the MSK-12C02 ([C431540](https://jlcpcb.com/partdetail/SHOUHAN-MSK12C02/C431540), extended). JLCPCB assembles them as a **single-side, bottom-side** order, which removes 86 of the fiddliest joints. You still solder the switches, the XIAO and the battery.

- **Files:** `hardware/pcb/fab.py` writes the Gerbers, BOM and placement (CPL) file for each board to `exports/pcb/<side>/`. The steps for ordering are in [02-pcb.md](02-pcb.md#6-order).
- **Cost:** an assembly fee per design, so two orders for left and right. The MSK-12C02 is an extended part, which adds a small per-part loading fee.
- **Economic or Standard:** Economic is cheaper, but at 0.8 mm it only offers green HASL. Standard allows ENIG.
- **When soldering the switches:** the diodes sit about 1.5 mm from each switch's contact holes. Keep the iron on the hole and the contact brief, so you don't reflow a diode.

## Order of operations (per half)
1. **Test the XIAO loose.** Plug it in, flash the firmware, and confirm it shows up over USB *before* soldering it. Face-down, it's hard to rework.
2. **Inspect the bare PCB.** Check for shorts between BAT+, VBAT and GND, and between neighbouring row and column nets.
3. **Diodes** on the back (skip this if JLCPCB assembled them). Check orientation against the silkscreen **before** soldering. Use minimal solder, because blobs can lift whatever sits on top.
4. **Power switch** on the back at the top edge (skip if assembled). Solder the three pins and four tabs quickly so the plastic body doesn't melt.
5. **XIAO.** Place it **face-down** over the cutout, USB-C flush with the outer edge. Tack two opposite corner pads, check the alignment, then solder the rest with flux. Do it before the row-2 switches, while there's still iron access along its key side.
6. **Matrix test before the switches:** short each switch's two contact pads with tweezers and confirm the key registers (use the ZMK keymap or a key-tester site).
7. **Switches:**
   - The switch's pegs drop into the board's locating holes, so it aligns itself. Hold it flat.
   - Solder from the back through each plated hole, at 280 °C or less for 3 s or less per joint.
   - **Use very little solder.** Excess solder stops the switch sitting flat.
   - Test continuity on each column after soldering it.
8. **Battery.** **Check polarity with a multimeter before connecting.** Solder the cell's leads to the underside pads TP1 (+) and TP2 (−), with the lead end of the cell facing the column gap. The board carries BAT+ through the power switch to TP3. Wire TP3 to the XIAO's BAT+ back pad. GND reaches the XIAO through its GND pad, so no BAT− wire is needed.
9. **Full test on battery:** pairing, every key, battery % reporting, sleep/wake, and that the power switch really cuts power.
10. **Into the case.** Fix the battery with Kapton or foam. Fit the PCB by sliding one long edge under its snap lip, then pressing the other edge down until it clicks under the other lip, with the locating pins through the board's two holes. There are no screws. To remove it, flex one lip outward.
11. **Keycaps.** Optionally add a 0.5 mm Poron foam layer to quiet them (a tip from chalk).

## Debug tips
- A whole row or column dead means a trace or XIAO pin joint problem. Reflow it.
- A single key dead means the diode orientation or a switch pad joint.
- No power on battery: check the power switch position, then the BAT+ path from TP1 through the switch to TP3 and the XIAO.
- The halves don't pair: flash `settings_reset` to both, then reflash the firmware.
