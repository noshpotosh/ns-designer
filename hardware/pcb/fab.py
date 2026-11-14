"""Write the JLCPCB order files for both boards.

Run it with KiCad's Python, after route.py:

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 hardware/pcb/fab.py

For each board it writes to exports/pcb/<side>/:
- <side>-gerbers.zip: the copper, mask, paste, silk and outline Gerbers, plus
  separate PTH and NPTH Excellon drill files. Upload this to start the order.
- <side>-bom.csv and <side>-cpl.csv: the parts list and placement file for
  JLCPCB assembly, in the column names JLCPCB asks for. They list only the
  footprints with an LCSC field (the diodes and power switch on the back);
  the switches, XIAO and battery are hand-soldered.
"""

import csv
import shutil
import subprocess
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
KICAD_CLI = shutil.which("kicad-cli") or "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
LAYERS = "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"


def cli(*args):
    subprocess.run([KICAD_CLI, *args], check=True, capture_output=True)


def gerbers(pcb, out):
    with tempfile.TemporaryDirectory() as tmp:
        cli("pcb", "export", "gerbers", "--layers", LAYERS, "-o", tmp, str(pcb))
        cli("pcb", "export", "drill", "--excellon-separate-th", "-u", "mm", "-o", tmp, str(pcb))
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(Path(tmp).iterdir()):
                z.write(f, f.name)


def assembly(pcb, side, out_dir):
    board = pcbnew.LoadBoard(str(pcb))
    lcsc = {f.GetReference(): f.GetFieldText("LCSC") for f in board.GetFootprints() if f.HasField("LCSC")}
    with tempfile.TemporaryDirectory() as tmp:
        pos = Path(tmp) / "pos.csv"
        cli("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "-o", str(pos), str(pcb))
        rows = [r for r in csv.DictReader(pos.open()) if r["Ref"] in lcsc]

    with (out_dir / f"{side}-cpl.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for r in rows:
            w.writerow([r["Ref"], f'{r["PosX"]}mm', f'{r["PosY"]}mm', r["Side"].capitalize(), r["Rot"]])

    groups = defaultdict(list)
    for r in rows:
        groups[(r["Val"], r["Package"], lcsc[r["Ref"]])].append(r["Ref"])
    with (out_dir / f"{side}-bom.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (val, package, part), refs in sorted(groups.items()):
            refs.sort(key=lambda s: (s.rstrip("0123456789"), int(s[len(s.rstrip("0123456789")):])))
            w.writerow([val, ",".join(refs), package, part])
    return len(rows)


def main():
    for side in ("left", "right"):
        pcb = HERE / side / f"{side}.kicad_pcb"
        out = HERE.parents[1] / "exports" / "pcb" / side
        out.mkdir(parents=True, exist_ok=True)
        gerbers(pcb, out / f"{side}-gerbers.zip")
        n = assembly(pcb, side, out)
        print(f"{side}: gerbers, BOM and CPL ({n} placed parts)")


if __name__ == "__main__":
    main()
