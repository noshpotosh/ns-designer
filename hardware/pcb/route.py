"""Route the left and right boards that generate.py placed.

Run it with KiCad's Python, after generate.py:

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 hardware/pcb/route.py

It deletes any tracks, vias and the GND pour already on the boards, then lays
down the routes below and refills the pour. Hand edits made in KiCad are lost
on a rerun, so once you start editing the routing by hand, stop using this.

Coordinates are mm from the centre of key (0, 0), y down, as in generate.py.
Each board is listed in full: the switch footprints aren't mirrored, so the
right board's routing is not a mirror of the left's.

The plan (see buildbook/chapters/02-pcb.md):
- Columns run down F.Cu through the gap between each switch's two contacts
  (x = key - 2). Rows run along B.Cu 7.6 mm below each key centre, and each
  diode's anode goes straight up to its switch's pad 2.
- The XIAO's key-side pads are fed from above. The pads on the strip under
  its far side fan out downward on F.Cu (nearest pad shallowest), leave under
  the antenna end, and run along the bottom edge to the matrix.
- BAT+ runs on B.Cu from TP1 to the power switch at the top edge; VBAT runs
  from the switch along the top edge and down a column gap on F.Cu to TP3.
- GND is a B.Cu pour, tied to the XIAO's GND pad by a via.
"""

import pcbnew
from pcbnew import FromMM, VECTOR2I

from generate import HERE, KEYS, ORIGIN, P, DIODE_ABOVE, DIODE_DY

SIG, PWR = 0.2, 0.25
VIA_D, VIA_DRILL = 0.6, 0.3
ROW_DY = 7.6                       # row line below each key centre


def key_x(c, side):
    return (4 - c) * P if side == "right" else c * P


class Router:
    def __init__(self, board):
        self.b = board
        self.nets = {n.GetNetname().lstrip("/"): n for n in board.GetNetsByName().values()}

    def pt(self, x, y):
        return VECTOR2I(FromMM(ORIGIN[0] + x), FromMM(ORIGIN[1] + y))

    def track(self, net, layer, pts, width=SIG):
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(self.pt(*a))
            t.SetEnd(self.pt(*b))
            t.SetWidth(FromMM(width))
            t.SetLayer(layer)
            t.SetNet(self.nets[net])
            self.b.Add(t)

    def f(self, net, *pts, width=SIG):
        self.track(net, pcbnew.F_Cu, pts, width)

    def bk(self, net, *pts, width=SIG):
        self.track(net, pcbnew.B_Cu, pts, width)

    def via(self, net, x, y):
        v = pcbnew.PCB_VIA(self.b)
        v.SetPosition(self.pt(x, y))
        v.SetWidth(FromMM(VIA_D))
        v.SetDrill(FromMM(VIA_DRILL))
        v.SetNet(self.nets[net])
        self.b.Add(v)


def matrix(r, side):
    """Diode stubs, row lines and column lines: the same plan on both boards."""
    rows = {}
    cols = {}
    for c, row in KEYS:
        kx, ky = key_x(c, side), row * P
        dy = -DIODE_DY if (c, row) in DIODE_ABOVE else DIODE_DY
        # Anode up to the switch's pad 2, cathode to the row line.
        r.bk(f"Net-(D{KEYS.index((c, row)) + 1}-A)", (kx + 1.25, ky + dy), (kx + 2, ky + 2.65))
        if dy > 0:
            r.bk(f"ROW{row}", (kx - 1.25, ky + dy), (kx - 1.25, ky + ROW_DY))
        else:
            # Over the battery the diode sits above the switch; the cathode
            # goes left round the switch's locating hole, then down.
            r.bk(f"ROW{row}", (kx - 1.25, ky + dy), (kx - 4.5, ky + dy), (kx - 4.5, ky + ROW_DY))
        xs = rows.setdefault(row, [])
        xs += [kx - 1.25] + ([kx - 4.5] if dy < 0 else [])
        cols.setdefault(c, []).append(ky)
    for row, xs in rows.items():
        rows[row] = (min(xs), max(xs))
    for c, ys in cols.items():
        x = key_x(c, side) - 2
        r.f(f"COL{c}", (x, min(ys) + 2.65), (x, max(ys) + 2.65))
    return rows


def route_left(r):
    rows = matrix(r, "left")
    y = lambda row: row * P + ROW_DY
    r.bk("ROW0", (rows[0][0], y(0)), (rows[0][1], y(0)))
    r.bk("ROW1", (rows[1][0], y(1)), (rows[1][1], y(1)))
    r.bk("ROW2", (-5.0, y(2)), (rows[2][1], y(2)))
    r.bk("ROW3", (30.0, y(3)), (rows[3][1], y(3)))

    # XIAO key-side pads, fed from above: D0 ROW2, D1 COL0, D2 ROW0, D3 ROW1.
    r.via("ROW2", -5.0, 41.6)
    r.f("ROW2", (-5.0, 41.6), (-5.0, 43.0))
    r.f("COL0", (-2, 36.65), (-2, 41.2), (-3.1, 42.3), (-3.1, 43.36))
    r.via("ROW0", -0.3, 7.6)
    r.f("ROW0", (-0.3, 7.6), (-0.3, 41.3), (-0.56, 41.56), (-0.56, 43.36))
    r.via("ROW1", 0.3, 24.6)
    r.f("ROW1", (0.3, 24.6), (0.3, 39.0), (1.98, 40.68), (1.98, 43.36))
    # D4 COL1, D5 COL4, D6 COL3: a three-track bundle from the right, over the
    # top of the pads. COL3/COL4 cross COL2 on B.Cu between rows 2 and 3.
    r.f("COL1", (15, 36.65), (15, 41.35), (4.52, 41.35), (4.52, 43.36))
    r.via("COL4", 66, 42.4)
    r.bk("COL4", (66, 42.4), (17.0, 42.4))
    r.via("COL4", 17.0, 42.4)
    r.f("COL4", (17.0, 42.4), (16.35, 41.75), (7.06, 41.75), (7.06, 43.36))
    r.via("COL3", 49, 43.2)
    r.bk("COL3", (49, 43.2), (15.8, 43.2))
    r.via("COL3", 15.8, 43.2)
    r.f("COL3", (15.8, 43.2), (15.1, 42.5), (9.6, 42.5), (9.6, 43.36))

    # Strip pads: D7 ROW3 leaves at pad level, D8 COL2 and GND fan out below.
    r.f("ROW3", (9.6, 60.04), (30.0, 60.04))
    r.via("ROW3", 30.0, 60.04)
    r.bk("ROW3", (30.0, 60.04), (30.0, y(3)))
    r.f("COL2", (7.06, 60.04), (7.06, 61.475), (32, 61.475), (32, 53.65))
    r.f("GND", (-3.1, 60.04), (-3.1, 61.875), (13.0, 61.875), (13.6, 62.475))
    r.via("GND", 13.6, 62.475)

    # Power: TP1 -> switch common on B.Cu; switch -> TP3 along the top edge
    # and down the column-1/2 gap.
    r.bk("BAT+", (25.5, 4.5), (25.5, -0.6), (0.75, -0.6), (0.75, -4.41), width=PWR)
    r.bk("VBAT", (-2.25, -4.41), (-2.25, -3.9), (-2.6, -3.3), (-2.6, -2.6), width=PWR)
    r.via("VBAT", -2.6, -2.6)
    r.f("VBAT", (-2.6, -2.6), (-2.6, -7.8), (25.5, -7.8), (25.5, 41.0), (21.5, 45.0), (21.5, 47.0), width=PWR)


def route_right(r):
    rows = matrix(r, "right")
    y = lambda row: row * P + ROW_DY
    for row in (0, 1, 2):
        r.bk(f"ROW{row}", (rows[row][0], y(row)), (rows[row][1], y(row)))
    r.bk("ROW3", (rows[3][0], y(3)), (rows[3][1], y(3)))

    # XIAO key-side pads: D7 COL1, D8 ROW1, D9 ROW2, D10 COL0, GND.
    r.f("COL0", (66, 36.65), (66, 43.36))
    r.via("ROW2", 63.48, 41.6)
    r.f("ROW2", (63.48, 41.6), (63.48, 43.36))
    r.via("ROW1", 59.5, 24.6)
    r.f("ROW1", (59.5, 24.6), (59.5, 41.2), (60.94, 42.64), (60.94, 43.36))
    r.f("COL1", (49, 36.65), (49, 41.75), (58.4, 41.75), (58.4, 43.36))
    r.f("GND", (71.1, 43.36), (71.1, 40.5), width=PWR)
    r.via("GND", 71.1, 40.5)

    # Strip pads: D6 ROW0 at pad level, then D5..D2 fan out below and close
    # up to a 0.4 mm pitch once clear of the tab.
    r.f("ROW0", (58.4, 60.04), (42.1, 60.04), (42.1, 7.6))
    r.via("ROW0", 42.1, 7.6)
    r.f("COL2", (60.94, 60.04), (60.94, 61.475), (55.0, 61.475), (53.965, 60.44), (32, 60.44), (32, 53.65))
    r.f("ROW3", (63.48, 60.04), (63.48, 61.875), (54.8, 61.875), (53.765, 60.84), (25.34, 60.84), (25.0, 60.5))
    r.via("ROW3", 25.0, 60.5)
    r.bk("ROW3", (25.0, 60.5), (25.0, y(3)))
    r.f("COL3", (66.02, 60.04), (66.02, 62.275), (54.6, 62.275), (53.565, 61.24), (15, 61.24), (15, 53.65))
    r.f("COL4", (68.56, 60.04), (68.56, 62.675), (54.4, 62.675), (53.365, 61.64), (-2, 61.64), (-2, 53.65))

    # Power, mirrored in spirit: the VBAT lane shares the column-1/2 gap with
    # ROW0, on its outer side.
    r.bk("BAT+", (42.5, 4.5), (42.5, -0.6), (68.75, -0.6), (68.75, -4.41), width=PWR)
    r.bk("VBAT", (65.75, -4.41), (65.75, -3.9), (65.4, -3.3), (65.4, -2.6), width=PWR)
    r.via("VBAT", 65.4, -2.6)
    r.f("VBAT", (65.4, -2.6), (65.4, -7.8), (42.85, -7.8), (42.85, 43.5), (46.5, 47.15), (46.5, 47.0), width=PWR)


def gnd_pour(r):
    z = pcbnew.ZONE(r.b)
    z.SetLayer(pcbnew.B_Cu)
    z.SetNet(r.nets["GND"])
    z.SetZoneName("GND")
    z.SetLocalClearance(FromMM(0.25))
    z.SetMinThickness(FromMM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.Outline().NewOutline()
    for x, y in [(-10, -10), (78, -10), (78, 65), (-10, 65)]:     # clipped to the outline
        p = r.pt(x, y)
        z.Outline().Append(p.x, p.y)
    r.b.Add(z)
    pcbnew.ZONE_FILLER(r.b).Fill(r.b.Zones())


def main():
    for side in ("left", "right"):
        path = HERE / side / f"{side}.kicad_pcb"
        board = pcbnew.LoadBoard(str(path))
        for t in list(board.GetTracks()):
            board.Remove(t)
        for z in list(board.Zones()):
            if not z.GetIsRuleArea():
                board.Remove(z)
        r = Router(board)
        (route_left if side == "left" else route_right)(r)
        gnd_pour(r)
        pcbnew.SaveBoard(str(path), board)
        print(f"routed {side}")


if __name__ == "__main__":
    main()
