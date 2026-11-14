"""Draw the routing diagrams and 3D back renders shown in dist/index.html.

Run it with KiCad's Python, after route.py:

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 hardware/pcb/render.py

For each board it writes to buildbook/assets/:
- pcb-routing-<side>.svg: the copper seen from the top, front tracks and back
  tracks in different colours. The B.Cu GND pour is left out, or it would
  hide the back tracks.
- pcb-back-<side>.png: kicad-cli's 3D render of the back (diodes, power
  switch, battery pads).
"""

import subprocess
from pathlib import Path

import pcbnew
from pcbnew import ToMM

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "buildbook" / "assets"
KICAD_CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

# Fixed colours, so the drawing reads the same on a light or dark page.
BG, BOARD, EDGE = "#14201c", "#1d3029", "#6f8a80"
FRONT, BACK = "#e0794f", "#5aa2e0"
PAD, HOLE, FAB = "#c9a24a", "#14201c", "#4d6a60"
MARGIN = 3.0


def svg(board):
    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline, True)
    box = board.GetBoardEdgesBoundingBox()
    x0, y0 = ToMM(box.GetX()) - MARGIN, ToMM(box.GetY()) - MARGIN
    w, h = ToMM(box.GetWidth()) + 2 * MARGIN, ToMM(box.GetHeight()) + 2 * MARGIN

    def p(v):
        return f"{ToMM(v.x) - x0:.3f},{ToMM(v.y) - y0:.3f}"

    def poly(chain):
        return "M" + " L".join(p(chain.CPoint(i)) for i in range(chain.PointCount())) + " Z"

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" width="{w * 8:.0f}" height="{h * 8:.0f}">',
           f'<rect width="100%" height="100%" fill="{BG}"/>']
    d = " ".join(poly(outline.Outline(i)) + " " + " ".join(poly(outline.Hole(i, j)) for j in range(outline.HoleCount(i)))
                 for i in range(outline.OutlineCount()))
    out.append(f'<path d="{d}" fill="{BOARD}" stroke="{EDGE}" stroke-width="0.25" fill-rule="evenodd"/>')

    # Part bodies, faint, for orientation.
    fab = []
    for fp in board.GetFootprints():
        for g in fp.GraphicalItems():
            if g.GetLayer() not in (pcbnew.F_Fab, pcbnew.B_Fab) or not hasattr(g, "GetShape"):
                continue
            s = g.GetShape()
            if s == pcbnew.SHAPE_T_SEGMENT:
                fab.append(f"M{p(g.GetStart())} L{p(g.GetEnd())}")
            elif s == pcbnew.SHAPE_T_RECT:
                fab.append("M" + " L".join(p(c) for c in g.GetRectCorners()) + " Z")
    out.append(f'<path d="{" ".join(fab)}" fill="none" stroke="{FAB}" stroke-width="0.15"/>')

    # Back copper first, so front tracks draw over it where they cross.
    tracks = [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"]
    for layer, colour in ((pcbnew.B_Cu, BACK), (pcbnew.F_Cu, FRONT)):
        for t in tracks:
            if t.GetLayer() == layer:
                out.append(f'<path d="M{p(t.GetStart())} L{p(t.GetEnd())}" stroke="{colour}" '
                           f'stroke-width="{ToMM(t.GetWidth()):.2f}" stroke-linecap="round" fill="none"/>')

    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                c, r = pad.GetPosition(), ToMM(pad.GetDrillSize().x) / 2
                out.append(f'<circle cx="{ToMM(c.x) - x0:.3f}" cy="{ToMM(c.y) - y0:.3f}" r="{r:.3f}" fill="{HOLE}" stroke="{EDGE}" stroke-width="0.1"/>')
                continue
            layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            shape = pad.GetEffectivePolygon(layer, pcbnew.ERROR_INSIDE)
            dpad = " ".join(poly(shape.Outline(i)) for i in range(shape.OutlineCount()))
            opacity = "1" if layer == pcbnew.F_Cu else "0.6"
            out.append(f'<path d="{dpad}" fill="{PAD}" fill-opacity="{opacity}"/>')
            if pad.GetDrillSize().x:
                c = pad.GetPosition()
                out.append(f'<circle cx="{ToMM(c.x) - x0:.3f}" cy="{ToMM(c.y) - y0:.3f}" r="{ToMM(pad.GetDrillSize().x) / 2:.3f}" fill="{HOLE}"/>')

    for v in board.GetTracks():
        if v.GetClass() == "PCB_VIA":
            c = v.GetPosition()
            out.append(f'<circle cx="{ToMM(c.x) - x0:.3f}" cy="{ToMM(c.y) - y0:.3f}" r="{ToMM(v.GetWidth(pcbnew.F_Cu)) / 2:.3f}" '
                       f'fill="{PAD}" stroke="{HOLE}" stroke-width="{ToMM(v.GetDrillValue()):.2f}" stroke-opacity="0"/>')
            out.append(f'<circle cx="{ToMM(c.x) - x0:.3f}" cy="{ToMM(c.y) - y0:.3f}" r="{ToMM(v.GetDrillValue()) / 2:.3f}" fill="{HOLE}"/>')

    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    for side in ("left", "right"):
        pcb = HERE / side / f"{side}.kicad_pcb"
        (OUT / f"pcb-routing-{side}.svg").write_text(svg(pcbnew.LoadBoard(str(pcb))))
        subprocess.run([KICAD_CLI, "pcb", "render", "--side", "bottom", "--quality", "high",
                        "--use-board-stackup-colors", "--background", "transparent",
                        "-w", "1600", "-h", "1400", "-o", str(OUT / f"pcb-back-{side}.png"), str(pcb)],
                       check=True, capture_output=True)
        print(f"rendered {side}")


if __name__ == "__main__":
    main()
