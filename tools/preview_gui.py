"""Show a populated real window for a bounded visual inspection."""

from pathlib import Path
import sys
import json

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))
from security_tools.gui import Application

app = Application()
p = app.tx
p.variables["enc_key"].set("D3 C5 D5 92 32 7F B1 1C 40 35 C6 68 0A F8 C6 D1")
p.variables["int_key"].set("D3C5D592327FB11C4035C6680AF8C6D1")
p.variables["count"].set("965368244")
p.variables["bearer"].set("26")
p.variables["direction"].set("1 — DL")
# NR SRB's 12-bit SN is the low 12 bits of the manually supplied COUNT.
p.variables["pdcp_header"].set("09 B4")
p.input.insert("1.0", "48 45 83 D5 AF E0 82 AE")
p.calculate()
app.after(20000, app.destroy)
app.mainloop()
