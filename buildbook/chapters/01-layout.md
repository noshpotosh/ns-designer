# 01 — Layout & matrix

## Grid
Each half is 5 columns × 4 rows on a uniform pitch `P`. The pitch is **P = 17 mm** (see [requirements](00-requirements.md#locked-decisions)). There is no stagger anywhere.

```
 Left half                         col:  0   1   2   3   4
                                       ┌───┬───┬───┬───┬───┐
 row 0                                 │ x │ x │ x │ x │ x │
                                       ├───┼───┼───┼───┼───┤
 row 1                                 │ x │ x │ x │ x │ x │
                                       ├───┼───┼───┼───┼───┤
 row 2                                 │ x │ x │ x │ x │ x │
                                       ├───┴───┼───┼───┼───┤
 row 3 (thumbs)                        │ XIAO  │ x │ x │ x │
                                       └───────┴───┴───┴───┘
```
The right half is its **own board, laid out as a mirror image** of the left. Its XIAO sits at the outer edge (columns 3–4). The switches face up on both boards and the diodes sit on the back of both.

**Outline per half:** the keys take 5P × 4P = 85 × 68 mm at 17 mm pitch. The PCB runs 2.6 mm further at the bottom edge, which makes it 85 × 70.6 mm, because the XIAO's far pins fan out there (see the XIAO slot below). Add 0.2 mm clearance and a 2.5 mm case wall on each side, which gives **90.4 × 76.0 mm** per half.

**The XIAO slot** is 2P × 1P = 34 × 17 mm. The XIAO measures 21 × 17.8 mm, so it fits lengthwise. It sits 0.7 mm below the row centre, which keeps its courtyard 0.08 mm clear of the row-2 caps (0.79 mm between the XIAO and the caps). Its far pad row lands on a strip of board boxed in by the cutout, so those pins can only get out downward. The board's bottom edge sits 2.6 mm below the key grid, plus a 1.1 mm tab under the XIAO, and the tray has a matching pocket. That leaves room for up to five tracks to fan out under the strip and run along the bottom edge to the matrix. It mounts **face-down** on top of the PCB, with its components and USB-C hanging down through a cutout (see [requirements](00-requirements.md#height-budget-target--7-mm)). The USB-C port faces the **outer side edge**. Check this in the KiCad 3D view.

## Matrix
- Each half uses a 5-col × 4-row diode matrix with 18 switches populated, so row 3 has 3 switches.
- That is **9 GPIO** (5 columns + 4 rows). The XIAO has 11 (D0–D10), which leaves **2 spare**.
- Diode direction is **col2row** (ZMK default): switch → diode anode, diode cathode → row.
- Use 1N4148WS (SOD-323) diodes on the back (B.Cu), the side opposite the switches. Keep them outside the battery pocket area: the two row-0 keys over the battery have their diodes above the switch instead of below.
- A diodeless matrix isn't possible; see [requirements](00-requirements.md#locked-decisions).

### GPIO map (as routed)
The two halves use different pins. The right board can't mirror the XIAO, so it rotates it instead. That turns the XIAO's other long side toward the keys: the left board's key-side pads are D0–D6, and the right board's are D7–D10 plus 3V3, GND and 5V. Each map is chosen so the routing never crosses itself (see [02-pcb](02-pcb.md#3-projects-and-placement)). Each half's firmware overlay lists its own pins.

| Signal | Left half | Right half |
|---|---|---|
| COL0 | D1 | D10 |
| COL1 | D4 | D7 |
| COL2 | D8 | D5 |
| COL3 | D6 | D3 |
| COL4 | D5 | D2 |
| ROW0 | D2 | D6 |
| ROW1 | D3 | D8 |
| ROW2 | D0 | D9 |
| ROW3 | D7 | D4 |
| Spare | D9, D10 | D0, D1 |
| Battery sense | internal (P0.31 / P0.14, from the ZMK board definition) | same |

Columns are numbered from the outer edge on both halves: COL0 is the pinky column. Leave the XIAO's 5V and 3V3 pads unconnected: the battery is wired to the XIAO's back pads, and the matrix needs only GPIO. Its GND pad is connected, so the board's GND pour and the battery − pad share the XIAO's ground.

Do not use the NFC pins (P0.09 / P0.10) for the matrix unless NFC is disabled in config.

## Other components per half
- **Power switch:** a small SMD side-actuated slide switch (e.g. MSK-12C02 or similar) in series with BAT+. Without it, the battery drains during transport. It sits on the underside at the top edge under the outer top key, with its nub facing out through a slot in the top wall. The outer side edge has no room: at every row, the frame pads and locating holes of the column-0 switches sit where the switch would go. The bottom edge is taken by the XIAO's fan-out. The switch's plastic pegs sit just inside that key switch's outline, but they reach only 0.5 mm into the 0.8 mm board, so they stop short of the switch.
- **Reset:** there's no extra switch. The face-down XIAO's onboard reset button faces the case floor, so you reach it through a pinhole in the floor. For normal use, put `&bootloader` / `&sys_reset` on a keymap layer.
- **Battery pads:** the cell's leads solder to two underside pads (TP1 +, TP2 −) in the column gap beside the battery pocket. The cell's lead end should face that gap. TP1 runs through the power switch to TP3, a top-side pad next to the XIAO, and a short wire joins TP3 to the XIAO's BAT+ back pad. TP2 is GND, which reaches the XIAO through its GND pad. With the XIAO face-down, its battery pads face up and are easy to reach.
