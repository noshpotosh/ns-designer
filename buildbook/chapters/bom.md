# Bill of materials (full keyboard, both halves)

Quantities cover both halves. Spares are in brackets. Prices are from October 2026 and change often.

## From JLCPCB, with the board order
JLCPCB makes the boards and places the back-side parts from its own stock (see [02-pcb.md](02-pcb.md#6-order)). You don't buy these separately.

| Qty | Part | Notes |
|---|---|---|
| 5 + 5 | PCB, 2-layer, 0.8 mm FR4: left and right designs | Minimum 5 per design. Assemble 2 of each |
| 36 | 1N4148WS diode, SOD-323 | [C2128](https://jlcpcb.com/partdetail/1N4148WS/C2128), basic part. 18 per board |
| 2 | MSK-12C02 side slide power switch | [C431540](https://jlcpcb.com/partdetail/SHOUHAN-MSK12C02/C431540), extended part. 1 per board |

## Buy these

| Qty | Part | Where | Notes |
|---|---|---|---|
| 36 (+14) | Kailh PG1316S switch | [Holykeebs](https://holykeebs.com/products/kailh-pg1316s-butterfly-switch-10-pack) | **Already have** |
| 36 (+4) | PG1316S keycaps, 1U | [Keycapsss](https://keycapsss.com/Kailh-PG1316S-Keycaps/KC10237-1U-BK) (EU, 10-packs), [Holykeebs](https://holykeebs.com/products/kailh-pg1316s-keycaps) (US, 10-packs, sold out in October 2026), [Modulo Industries](https://modulo.industries/) | 4 packs of 10. Or 3D-print them |
| 2 (+1) | Seeed XIAO nRF52840 | [Seeed](https://www.seeedstudio.com/Seeed-XIAO-BLE-nRF52840-p-5201.html), about $10 | Choose **Un-Soldered**. Headers would stop it lying flat face-down. A spare helps, since a face-down XIAO is hard to rework |
| 2 (+1) | LiPo pouch, 3.7 V, about 100 mAh, **252030** (2.5 × 20 × 30 mm) | [AliExpress search](https://www.aliexpress.com/w/wholesale-252030-lipo-battery.html), [Amazon search](https://www.amazon.com/s?k=252030+lipo+battery) | No retail shop lists one reliably. Look for a **protection board** and **bare leads**, and check that 30 mm includes the protection board: the pocket is 30.4 × 20.4 mm. Record the model in [requirements](00-requirements.md#battery) |
| ~1 m | 30 AWG silicone wire | Any hobby kit | Joins the TP3 pad to the XIAO's BAT+ back pad. Battery leads too, if the cell's are too short |
| 1 | PG1316S practice board | [Holykeebs](https://holykeebs.com/products/pg1316s-practice-board) | Optional. Worth it before your first PG1316S joint |
| — | Kapton tape, 0.5 mm Poron foam, thin rubber feet | Any hobby supplier | Kapton holds the battery; Poron quiets the caps |
| — | Filament or resin for the case | | See [04-case.md](04-case.md) |

## Tools
- Fine-tip soldering iron (temperature controlled), flux, and 0.3–0.5 mm solder
- Multimeter, tweezers, calipers, flush cutters

## If you hand-solder instead
Skip the JLCPCB assembly and also buy 36 (+10) 1N4148WS diodes (SOD-323) and 2 (+1) MSK-12C02 switches from [LCSC](https://www.lcsc.com/product-detail/C431540.html) or AliExpress. That adds 86 joints (see [assembly](05-assembly.md#how-hard-it-is)).
