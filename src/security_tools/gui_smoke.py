"""Run real Tk widgets on the selected desktop; write a separate GUI report."""

import json
from pathlib import Path
import traceback
from .bits import Bits, from_result
from .core import transmit
from .gui import Application, ALGORITHMS


def run(output):
    app = Application()
    cases = []

    def check(name, fn):
        try:
            fn()
            cases.append({"id": name, "status": "PASS"})
        except Exception:
            cases.append({"id": name, "status": "FAIL", "error": traceback.format_exc()})

    def equal(actual, expected):
        assert actual == expected, (actual, expected)

    def tests():
        try:
            app.update_idletasks()
            for receiving, panel in [(False, app.tx), (True, app.rx)]:
                prefix = "rx" if receiving else "tx"
                v = panel.variables
                v["enc_key"].set("000102030405060708090a0b0c0d0e0f")
                v["int_key"].set("f0e0d0c0b0a090807060504030201000")
                for cip, itg in [(True, False), (False, True), (True, True)]:
                    v["cipher_enabled"].set(cip)
                    v["integrity_enabled"].set(itg)
                    panel.refresh()
                    original = Bits.parse("000102")
                    options = dict(ciphering=2 if cip else None, integrity=2 if itg else None,
                                   enc_key=bytes.fromhex(v["enc_key"].get()), int_key=bytes.fromhex(v["int_key"].get()))
                    tx = transmit(original, **options)
                    payload = from_result(tx["data"]) if receiving else original
                    panel.input.delete("1.0", "end")
                    panel.input.insert("1.0", payload.format("Hex"))
                    if receiving and itg and not cip:
                        v["received_mac"].set(tx["mac_i"]["hex"])
                    panel.execute_button.invoke()
                    def result_check():
                        assert panel.result is not None, panel.status.cget("text")
                        equal(panel.result["data"], original.to_dict() if receiving else tx["data"])
                    check(f"{prefix}-protection-{cip}-{itg}", result_check)
                v["cipher_enabled"].set(False)
                v["integrity_enabled"].set(False)
                panel.refresh()
                check(prefix + "-both-disabled", lambda: equal(str(panel.execute_button.cget("state")), "disabled"))
            panel = app.tx
            v = panel.variables
            v["cipher_enabled"].set(True)
            v["integrity_enabled"].set(False)
            panel.refresh()
            panel.input.delete("1.0", "end")
            panel.input.insert("1.0", "0001")
            panel.convert_input()
            check("hex-to-bit-leading-zero", lambda: equal(panel.input.get("1.0", "end-1c"), "0000000000000001"))
            panel.convert_input()
            check("bit-to-hex-round-trip", lambda: equal(panel.input.get("1.0", "end-1c"), "0001"))
            v["data_format"].set("Bit")
            panel.input.delete("1.0", "end")
            panel.input.insert("1.0", "00101")
            panel.convert_input()
            check("unaligned-conversion-rejected", lambda: equal(v["data_format"].get(), "Bit"))
            panel.calculate()
            check("unaligned-output", lambda: equal(v["output_format"].get(), "Bit"))
            panel.copy_output()
            check("clipboard-exact-bits", lambda: equal(panel.clipboard_get(), from_result(panel.result["data"]).format("Bit")))
            v["ciphering"].set(ALGORITHMS[0])
            v["integrity_enabled"].set(True)
            v["integrity"].set(ALGORITHMS[0])
            panel.refresh()
            check("null-keys-disabled", lambda: equal(str(panel.enc_entry.cget("state")), "disabled"))
            panel.calculate()
            check("null-not-authenticated", lambda: equal(panel.result["authentication"], "unprotected"))
        finally:
            dest = Path(output)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps({"category": "gui_widgets", "cases": cases,
                                       "passed": sum(c["status"] == "PASS" for c in cases), "total": len(cases)}, indent=2) + "\n", encoding="utf-8")
            app.destroy()

    app.after(400, tests)
    app.mainloop()
    return 0 if cases and all(c["status"] == "PASS" for c in cases) else 1
