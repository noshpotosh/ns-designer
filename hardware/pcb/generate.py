"""Bootstrap the left and right KiCad projects: schematic, placement, outline.

Run it with KiCad's own Python, which provides `pcbnew`:

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 hardware/pcb/generate.py

It writes hardware/pcb/left/ and hardware/pcb/right/ and refuses to overwrite them unless
you pass --force, because routing is done by hand in KiCad afterwards and a
rerun would wipe it. The schematic is written first; its netlist (exported
with kicad-cli) assigns the pad nets, so the board starts in sync with it.

Board coordinates are in mm relative to the centre of key (0, 0), with y
pointing down as in KiCad. The CAD model (hardware/case/keyboard.py) uses the same
origin with y pointing up. Everything is laid out for the left board and
mirrored in x for the right one, except the parts that can't be mirrored:
the switches keep their footprint orientation and the XIAO is rotated.
"""

import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import pcbnew
from pcbnew import FromMM, VECTOR2I

HERE = Path(__file__).resolve().parent
LIB = HERE / "lib"
KICAD_FP = Path(os.environ.get(
    "KICAD10_FOOTPRINT_DIR", "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"))
KICAD_SYM = Path(os.environ.get(
    "KICAD10_SYMBOL_DIR", "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"))
KICAD_CLI = shutil.which("kicad-cli") or "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

# --- Layout (mm) -------------------------------------------------------------
P = 17.0
COLS, ROWS = 5, 4
KEYS = [(c, r) for r in range(3) for c in range(COLS)] + [(c, 3) for c in (2, 3, 4)]
ORIGIN = (100.0, 100.0)            # page position of key (0, 0)

# The bottom edge sits 2.6 mm below the 3.5P key edge: the strip of pads the
# XIAO's far side lands on is boxed in by its cutout, so those pins fan out
# under the strip and run along the bottom edge to the matrix.
L, R, T, B = -P / 2, COLS * P - P / 2, -P / 2, ROWS * P - P / 2 + 2.6
CORNER_R = 3.3                     # tray inner corner radius (3.5) less the 0.2 mm clearance

# XIAO, face-down in row 3, columns 0-1, USB-C flush with the outer edge. It
# sits 0.7 mm below the row centre so its courtyard clears the row-2 caps.
XIAO_XY = (L + 20.96 / 2, 3 * P + 0.7)
XIAO_A, XIAO_AW = 6.8, 7.6         # cutout half-widths (footprint Dwgs.User)
XIAO_WIDE, XIAO_END = 9.0, 10.7    # where the cutout widens / ends, from the XIAO centre
# A tab under the XIAO gives the fan-out room for five tracks below its outer
# pad row. The tray gets a matching pocket in its bottom wall.
TAB_X, TAB_B = 16.0, 63.2

BAT_X, BAT_Y = (27.3, 57.7), (-1.7, 18.7)   # battery pocket in the case floor, with 0.2 mm clearance
POST_R = 1.2                       # case support post under each key centre
LOCATING = [(0.5 * P, 0.5 * P), (3.5 * P, 1.5 * P)]
DIODE_DY = 5.2                     # below the switch contacts, clear of the centre post
# Row-0 keys over the battery pocket: their diodes sit above the switch instead.
DIODE_ABOVE = {(2, 0), (3, 0)}
# Power switch on B.Cu at the top edge under key (0, 0), nub facing out, body
# edge 0.5 mm in from the board edge.
PWR_SW_XY = (0.0, T + 0.5 + 1.89)
PADS = {                           # test-point pads: (x, y, layer)
    "TP1": (25.5, 4.5, "B"),       # battery +
    "TP2": (25.5, 12.5, "B"),      # battery -
    "TP3": (21.5, 47.0, "F"),      # wire to the XIAO's BAT+ back pad
}
LABEL_XY = (21.5, 53.0)
# LCSC part numbers, by value, for the parts JLCPCB assembles (the back side).
LCSC = {"1N4148WS": "C2128", "MSK-12C02": "C431540"}


def key_xy(c, r):
    return c * P, r * P


def over_battery(x, y, margin):
    return BAT_X[0] - margin < x < BAT_X[1] + margin and BAT_Y[0] - margin < y < BAT_Y[1] + margin


# --- Schematic -----------------------------------------------------------------

def uid(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "keeb/" + "/".join(map(str, parts))))


def sexpr_block(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError("unbalanced s-expression")


def lib_symbol(lib, name):
    path = LIB / "keeb.kicad_sym" if lib == "keeb" else KICAD_SYM / f"{lib}.kicad_sym"
    text = path.read_text()
    body = sexpr_block(text, text.index(f'(symbol "{name}"\n'))
    return body.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)


def pin_xy(at, pin, rot):
    """Schematic position of a library pin end for a symbol placed at `at`."""
    px, py = pin[0], -pin[1]
    a = math.radians(rot)
    return (round(at[0] + px * math.cos(a) + py * math.sin(a), 4),
            round(at[1] - px * math.sin(a) + py * math.cos(a), 4))


def font(hide=False, justify=None):
    j = f" (justify {justify})" if justify else ""
    h = " (hide yes)" if hide else ""
    return f"(effects (font (size 1.27 1.27)){j}{h})"


class Schematic:
    PINS = {
        "Switch:SW_Push": {"1": (-5.08, 0), "2": (5.08, 0)},
        "Device:D": {"1": (-3.81, 0), "2": (3.81, 0)},
        "Switch:SW_SPDT": {"1": (5.08, 2.54), "2": (-5.08, 0), "3": (5.08, -2.54)},
        "Connector:TestPoint": {"1": (0, 0)},
        "Mechanical:MountingHole": {},
        "power:PWR_FLAG": {"1": (0, 0)},
        "keeb:XIAO_nRF52840": {
            **{str(n + 1): (-12.7, 7.62 - 2.54 * n) for n in range(7)},
            **{str(n + 8): (12.7, -7.62 + 2.54 * n) for n in range(7)},
        },
    }

    def __init__(self, project):
        self.project = project
        self.root = uid(project, "root")
        self.items = []
        self.symbols = {}          # reference -> symbol uuid

    def symbol(self, lib_id, ref, value, at, rot=0, footprint="", in_bom=True, on_board=True,
               ref_side=False, hide_value=False):
        u = uid(self.project, "sym", ref)
        self.symbols[ref] = u
        pins = "".join(f'\n  (pin "{n}" (uuid "{uid(self.project, ref, "pin", n)}"))' for n in self.PINS[lib_id])
        hidden = ref.startswith("#")
        lcsc = f'\n  (property "LCSC" "{LCSC[value]}" (at {at[0]} {at[1]} 0) {font(True)})' if value in LCSC else ""
        if ref_side:               # beside the symbol, for the upright diodes
            ref_at, ref_just = (round(at[0] + 2.54, 2), at[1]), "left"
        else:
            ref_at, ref_just = (at[0], round(at[1] - 3.81, 2)), None
        self.items.append(f"""(symbol (lib_id "{lib_id}") (at {at[0]} {at[1]} {rot}) (unit 1)
  (exclude_from_sim no) (in_bom {"yes" if in_bom else "no"}) (on_board {"yes" if on_board else "no"}) (dnp no)
  (uuid "{u}")
  (property "Reference" "{ref}" (at {ref_at[0]} {ref_at[1]} 0) {font(hidden, ref_just)})
  (property "Value" "{value}" (at {at[0]} {round(at[1] + 3.81, 2)} 0) {font(hide_value)})
  (property "Footprint" "{footprint}" (at {at[0]} {at[1]} 0) {font(True)})
  (property "Datasheet" "" (at {at[0]} {at[1]} 0) {font(True)}){lcsc}{pins}
  (instances (project "{self.project}" (path "/{self.root}" (reference "{ref}") (unit 1))))
)""")
        return {n: pin_xy(at, p, rot) for n, p in self.PINS[lib_id].items()}

    def label(self, name, at, rot=0):
        just = "right bottom" if rot == 180 else "left bottom"
        self.items.append(f'(label "{name}" (at {at[0]} {at[1]} {rot}) (fields_autoplaced yes) '
                          f'{font(justify=just)} (uuid "{uid(self.project, "label", name, *at)}"))')

    def no_connect(self, at):
        self.items.append(f'(no_connect (at {at[0]} {at[1]}) (uuid "{uid(self.project, "nc", *at)}"))')

    def text(self, body, at):
        body = body.replace('"', '\\"').replace("\n", "\\n")
        self.items.append(f'(text "{body}" (exclude_from_sim no) (at {at[0]} {at[1]} 0) '
                          f'{font(justify="left top")} (uuid "{uid(self.project, "text", *at)}"))')

    def write(self, path, title):
        libs = sorted({re.search(r'lib_id "([^"]+)"', s).group(1) for s in self.items if s.startswith("(symbol")})
        lib_symbols = "\n".join(lib_symbol(*l.split(":")) for l in libs)
        path.write_text(f"""(kicad_sch
(version 20231120)
(generator "eeschema")
(generator_version "8.0")
(uuid "{self.root}")
(paper "A4")
(title_block (title "{title}") (date "2026-10-27") (rev "0.1") (comment 1 "Generated by hardware/pcb/generate.py; edit in KiCad from here on"))
(lib_symbols
{lib_symbols}
)
{chr(10).join(self.items)}
(sheet_instances (path "/" (page "1")))
)
""")


# XIAO pin -> net for each half, chosen so the routing doesn't cross itself
# (see buildbook/chapters/02-pcb.md). The left board's XIAO faces D0-D6 toward the keys; the
# right board's is rotated, so D7-D10 face the keys and D0-D6 land on the
# fan-out strip.
PIN_MAP = {
    "left": {"D0": "ROW2", "D1": "COL0", "D2": "ROW0", "D3": "ROW1", "D4": "COL1", "D5": "COL4",
             "D6": "COL3", "D7": "ROW3", "D8": "COL2"},
    "right": {"D2": "COL4", "D3": "COL3", "D4": "ROW3", "D5": "COL2", "D6": "ROW0", "D7": "COL1",
              "D8": "ROW1", "D9": "ROW2", "D10": "COL0"},
}
XIAO_PIN = {f"D{n}": n + 1 for n in range(11)} | {"3V3": 12, "GND": 13, "5V": 14}


def build_schematic(project, title):
    s = Schematic(project)
    # Key matrix, col2row: COLn -> switch -> diode anode, cathode -> ROWn.
    for k, (c, r) in enumerate(KEYS, 1):
        x, y = 38.1 + c * 25.4, 38.1 + r * 22.86
        sw = s.symbol("Switch:SW_Push", f"SW{k}", "PG1316S", (x, y), hide_value=True,
                      footprint="keeb:SW_Kailh_PG1316S_ViaInPad")
        d = s.symbol("Device:D", f"D{k}", "1N4148WS", (round(x + 5.08, 2), round(y + 3.81, 2)), rot=90,
                     ref_side=True, hide_value=True, footprint="Diode_SMD:D_SOD-323_HandSoldering")
        assert d["2"] == sw["2"], "diode anode must meet switch pin 2"
        s.label(f"COL{c}", sw["1"], 180)
        s.label(f"ROW{r}", d["1"])

    # XIAO: 3V3 and 5V stay unused (the battery goes to the back pads), as do
    # the two spare GPIO.
    u = s.symbol("keeb:XIAO_nRF52840", "U1", "XIAO_nRF52840", (195.58, 50.8),
                 footprint="keeb:XIAO_nRF52840_FaceDown")
    nets = PIN_MAP[project] | {"GND": "GND"}
    for name, n in XIAO_PIN.items():
        at = u[str(n)]
        if name in nets:
            s.label(nets[name], at, 180 if n <= 7 else 0)
        else:
            s.no_connect(at)

    # Power: battery + -> slide switch -> wire to the XIAO's BAT+ back pad.
    sw = s.symbol("Switch:SW_SPDT", "SW19", "MSK-12C02", (195.58, 88.9), footprint="keeb:SW_Slide_MSK-12C02")
    s.label("BAT+", sw["2"], 180)
    s.label("VBAT", sw["1"])
    s.no_connect(sw["3"])
    for ref, net, x in [("TP1", "BAT+", 175.26), ("TP2", "GND", 190.5), ("TP3", "VBAT", 205.74)]:
        value = {"TP1": "BAT+", "TP2": "BAT-", "TP3": "XIAO_BAT+"}[ref]
        tp = s.symbol("Connector:TestPoint", ref, value, (x, 111.76), in_bom=False,
                      footprint="TestPoint:TestPoint_Pad_1.5x1.5mm")
        s.label(net, tp["1"], 180)
    flg = s.symbol("power:PWR_FLAG", "#FLG01", "PWR_FLAG", (220.98, 111.76), in_bom=False, on_board=False)
    s.label("GND", flg["1"])

    for i, ref in enumerate(["H1", "H2"]):
        s.symbol("Mechanical:MountingHole", ref, "Locating pin", (175.26 + 15.24 * i, 132.08), in_bom=False,
                 footprint="keeb:Post_Locating_D1.0")

    s.text("Matrix: 5 cols x 4 rows, col2row (ZMK default). Row 3 has thumbs on cols 2-4 only.\n"
           "SW1-SW18 are Kailh PG1316S, D1-D18 are 1N4148WS (values hidden on the sheet).\n"
           "XIAO is face-down; its 3V3 and 5V pads stay unconnected. GND ties the board's pour to the XIAO.\n"
           "The battery is hand-wired: TP1/TP2 take the cell leads, TP3 is wired to the XIAO's BAT+ back pad.\n"
           "H1/H2 are the case's locating-pin holes.", (25.4, 134.62))
    path = HERE / project / f"{project}.kicad_sch"
    s.write(path, title)
    run(KICAD_CLI, "sch", "upgrade", str(path))
    return s


def netlist(sch_path):
    """Pad nets from kicad-cli's netlist: {(ref, pad): net name}."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "net.net"
        run(KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(out), str(sch_path))
        text = out.read_text()
    nets = {}
    for m in re.finditer(r'\(net\s+\(code "\d+"\)\s+\(name "([^"]*)"\)', text):
        block = sexpr_block(text, m.start())
        for ref, pin in re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
            nets[(ref, pin)] = m.group(1)
    return nets


# --- Board ---------------------------------------------------------------------

class Board:
    def __init__(self, path, mirror):
        self.board = pcbnew.NewBoard(str(path))
        self.mirror = mirror
        self.nets = {}

    def xy(self, x, y):
        if self.mirror:
            x = (COLS - 1) * P - x
        return VECTOR2I(FromMM(ORIGIN[0] + x), FromMM(ORIGIN[1] + y))

    def net(self, name):
        if name not in self.nets:
            ni = pcbnew.NETINFO_ITEM(self.board, name)
            self.board.Add(ni)
            self.nets[name] = ni
        return self.nets[name]

    def footprint(self, lib, name, ref, value, x, y, rot=0, back=False, sch=None, pad_nets=None):
        lib_dir = LIB / "keeb.pretty" if lib == "keeb" else KICAD_FP / f"{lib}.pretty"
        fp = pcbnew.FootprintLoad(str(lib_dir), name)
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(value)
        if value in LCSC:
            fp.SetField("LCSC", LCSC[value])
            fp.GetField("LCSC").SetVisible(False)
        fp.SetPosition(self.xy(x, y))
        self.board.Add(fp)         # Flip() needs the board's layer set
        if back:
            # Mirrors x but also turns the footprint to 180 degrees, so rot is added to that.
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(fp.GetOrientationDegrees() + rot)
        if sch:
            fp.SetPath(pcbnew.KIID_PATH(f"/{sch.symbols[ref]}"))
            fp.SetSheetname("/")
            fp.SetSheetfile(f"{sch.project}.kicad_sch")
        for pad in fp.Pads():
            net = (pad_nets or {}).get((ref, pad.GetNumber()))
            if net:
                pad.SetNet(self.net(net))
        return fp

    def edge(self, pts):
        """Closed outline from a list of points and ('arc', mid, end) steps."""
        cur = pts[0]
        closed = isinstance(pts[-1][0], str) and math.dist(pts[-1][2], pts[0]) < 1e-6
        steps = pts[1:] if closed else pts[1:] + [pts[0]]
        for step in steps:
            s = pcbnew.PCB_SHAPE(self.board)
            s.SetLayer(pcbnew.Edge_Cuts)
            s.SetWidth(FromMM(0.05))
            if isinstance(step[0], str):
                _, mid, end = step
                s.SetShape(pcbnew.SHAPE_T_ARC)
                s.SetArcGeometry(self.xy(*cur), self.xy(*mid), self.xy(*end))
                cur = end
            else:
                s.SetShape(pcbnew.SHAPE_T_SEGMENT)
                s.SetStart(self.xy(*cur))
                s.SetEnd(self.xy(*step))
                cur = step
            self.board.Add(s)

    def keepout(self, name, pts):
        """B.Cu rule area that keeps footprints out (the case floor features)."""
        z = pcbnew.ZONE(self.board)
        z.SetIsRuleArea(True)
        z.SetZoneName(name)
        z.SetLayer(pcbnew.B_Cu)
        z.SetDoNotAllowFootprints(True)
        for flag in ("Tracks", "Vias", "Pads", "ZoneFills"):
            getattr(z, f"SetDoNotAllow{flag}")(False)
        z.Outline().NewOutline()
        for x, y in pts:
            p = self.xy(x, y)
            z.Outline().Append(p.x, p.y)
        self.board.Add(z)

    def text(self, body, x, y, layer, size=1.2):
        t = pcbnew.PCB_TEXT(self.board)
        t.SetText(body)
        t.SetPosition(self.xy(x, y))
        t.SetLayer(layer)
        t.SetMirrored(layer == pcbnew.B_SilkS)
        t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
        t.SetTextThickness(FromMM(0.15 * size))
        self.board.Add(t)


def arc(cx, cy, r, a0, a1):
    """('arc', mid, end) step for a corner arc from angle a0 to a1 (degrees, y down)."""
    am = math.radians((a0 + a1) / 2)
    a1 = math.radians(a1)
    return ("arc", (cx + r * math.cos(am), cy + r * math.sin(am)), (cx + r * math.cos(a1), cy + r * math.sin(a1)))


def outline():
    r, cx, cy = CORNER_R, XIAO_XY[0], XIAO_XY[1]
    return [
        (L + r, T), (R - r, T), arc(R - r, T + r, r, -90, 0),
        (R, B - r), arc(R - r, B - r, r, 0, 90),
        (TAB_X, B), (TAB_X, TAB_B - 1), arc(TAB_X - 1, TAB_B - 1, 1, 0, 90),
        (L + 2, TAB_B), arc(L + 2, TAB_B - 2, 2, 90, 180),
        # XIAO cutout, open to the outer edge at the USB-C end.
        (L, cy + XIAO_A), (cx + XIAO_WIDE, cy + XIAO_A), (cx + XIAO_WIDE, cy + XIAO_AW),
        (cx + XIAO_END, cy + XIAO_AW), (cx + XIAO_END, cy - XIAO_AW), (cx + XIAO_WIDE, cy - XIAO_AW),
        (cx + XIAO_WIDE, cy - XIAO_A), (L, cy - XIAO_A),
        (L, T + r), arc(L + r, T + r, r, 180, 270),
    ]


def build_board(project, sch, side):
    mirror = side == "right"
    path = HERE / project / f"{project}.kicad_pcb"
    nets = netlist(HERE / project / f"{project}.kicad_sch")
    b = Board(path, mirror)
    ds = b.board.GetDesignSettings()
    ds.SetBoardThickness(FromMM(0.8))
    origin = b.xy(0, 0)
    ds.SetAuxOrigin(origin)
    ds.SetGridOrigin(origin)
    tb = b.board.GetTitleBlock()
    tb.SetTitle(f"keeb — {side} half")
    tb.SetRevision("0.1")
    tb.SetDate("2026-10-27")

    def fp(*args, **kw):
        return b.footprint(*args, sch=sch, pad_nets=nets, **kw)

    for k, (c, r) in enumerate(KEYS, 1):
        x, y = key_xy(c, r)
        fp("keeb", "SW_Kailh_PG1316S_ViaInPad", f"SW{k}", "PG1316S", x, y)
        dy = -DIODE_DY if (c, r) in DIODE_ABOVE else DIODE_DY
        d = fp("Diode_SMD", "D_SOD-323_HandSoldering", f"D{k}", "1N4148WS", x, y + dy, back=True)
        # Anode toward the switch's pad 2, which is on the +x side on both boards.
        anode = next(p for p in d.Pads() if p.GetNumber() == "2")
        if anode.GetPosition().x < d.GetPosition().x:
            d.SetOrientationDegrees(d.GetOrientationDegrees() + 180)
        if (c, r) in DIODE_ABOVE:          # its label would sit on the switch's
            d.Reference().SetLayer(pcbnew.B_Fab)

    xiao = fp("keeb", "XIAO_nRF52840_FaceDown", "U1", "XIAO_nRF52840", *XIAO_XY, rot=270 if mirror else 90)
    d0 = next(p for p in xiao.Pads() if p.GetNumber() == "1")
    usb_side = (d0.GetPosition().x < xiao.GetPosition().x) != mirror
    keys_side = d0.GetPosition().y < xiao.GetPosition().y
    assert usb_side and keys_side == (not mirror), "XIAO orientation"

    fp("keeb", "SW_Slide_MSK-12C02", "SW19", "MSK-12C02", *PWR_SW_XY, rot=180, back=True)
    for ref, (x, y, layer) in PADS.items():
        value = {"TP1": "BAT+", "TP2": "BAT-", "TP3": "XIAO_BAT+"}[ref]
        tp = fp("TestPoint", "TestPoint_Pad_1.5x1.5mm", ref, value, x, y, back=layer == "B")
        tp.Reference().SetLayer(pcbnew.B_Fab if layer == "B" else pcbnew.F_Fab)
    for i, (x, y) in enumerate(LOCATING, 1):
        fp("keeb", "Post_Locating_D1.0", f"H{i}", "Locating pin", x, y)

    b.edge(outline())
    b.keepout("Battery pocket", [(BAT_X[0], BAT_Y[0]), (BAT_X[1], BAT_Y[0]), (BAT_X[1], BAT_Y[1]), (BAT_X[0], BAT_Y[1])])
    for c, r in KEYS:
        x, y = key_xy(c, r)
        if not over_battery(x, y, POST_R + 0.5):
            b.keepout(f"Post {c},{r}", [(x + POST_R * math.cos(a * math.pi / 8), y + POST_R * math.sin(a * math.pi / 8))
                                        for a in range(16)])
    b.text(f"keeb {side[0].upper()} v0.1", *LABEL_XY, pcbnew.F_SilkS)
    # Wiring marks: the battery pads sit in a 2.3 mm column gap, so just + and -.
    b.text("+", PADS["TP1"][0], PADS["TP1"][1] + 1.75, pcbnew.B_SilkS, 0.9)
    b.text("-", PADS["TP2"][0], PADS["TP2"][1] - 1.75, pcbnew.B_SilkS, 0.9)
    b.text("BAT+", PADS["TP3"][0], PADS["TP3"][1] + 1.9, pcbnew.F_SilkS, 0.9)

    pcbnew.SaveBoard(str(path), b.board)
    return path


def run(*cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode:
        sys.exit(f"{' '.join(cmd)} failed:\n{res.stdout}{res.stderr}")
    return res.stdout


PROJECT_RULES = {
    "rules": {
        "min_clearance": 0.2, "min_track_width": 0.15, "min_via_diameter": 0.5, "min_through_hole_diameter": 0.3,
        "min_hole_clearance": 0.25, "min_hole_to_hole": 0.25, "min_copper_edge_clearance": 0.3,
    },
}
NET_SETTINGS = {
    "classes": [
        {"name": "Default", "clearance": 0.2, "track_width": 0.2, "via_diameter": 0.6, "via_drill": 0.3,
         "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2, "wire_width": 6, "bus_width": 12,
         "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "pcb_color": "rgba(0, 0, 0, 0.000)",
         "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647},
        {"name": "Power", "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3,
         "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2, "wire_width": 6, "bus_width": 12,
         "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "pcb_color": "rgba(0, 0, 0, 0.000)",
         "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 0},
    ],
    "netclass_patterns": [{"netclass": "Power", "pattern": p} for p in ("/BAT+", "/VBAT", "/GND")],
}


def write_project(project):
    pro = HERE / project / f"{project}.kicad_pro"
    data = json.loads(pro.read_text()) if pro.exists() else {}
    data.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {}).update(PROJECT_RULES["rules"])
    data.setdefault("net_settings", {}).update(NET_SETTINGS)
    data.setdefault("meta", {"filename": pro.name, "version": 3})
    pro.write_text(json.dumps(data, indent=2) + "\n")
    for kind, ext in (("fp", "pretty"), ("sym", "kicad_sym")):
        uri = f"${{KIPRJMOD}}/../lib/keeb.{ext}"
        (HERE / project / f"{kind}-lib-table").write_text(
            f'({kind}_lib_table\n  (version 7)\n  (lib (name "keeb")(type "KiCad")(uri "{uri}")(options "")(descr "Project library"))\n)\n')


def main():
    force = "--force" in sys.argv
    for side in ("left", "right"):
        d = HERE / side
        if d.exists() and any(d.iterdir()) and not force:
            sys.exit(f"{d} already exists; pass --force to overwrite it (this discards any routing)")
        d.mkdir(exist_ok=True)
        sch = build_schematic(side, f"keeb — {side} half")
        build_board(side, sch, side)
        write_project(side)
        print(f"wrote {d.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
