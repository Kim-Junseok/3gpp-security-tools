"""Show a populated real window for a bounded visual inspection."""

from pathlib import Path
import sys
import json

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))
from security_tools.gui import Application

app = Application()
p = app.tx
p.variables["enc_key"].set("000102030405060708090a0b0c0d0e0f")
p.variables["int_key"].set("f0e0d0c0b0a090807060504030201000")
p.variables["data_format"].set("Bit")
p.input.insert("1.0", "00010100101")
p.calculate()
app.after(20000, app.destroy)
app.mainloop()
