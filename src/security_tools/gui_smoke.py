"""Run real Tk widgets on the selected desktop; write a separate GUI report."""

import json
from pathlib import Path
import traceback
import sys
from .bits import Bits, from_result
from .core import transmit
from .gui import Application, ALGORITHMS
from .adapter import format_data
from .validation import data_dir, identity


def run(output):
    app = Application()
    cases = []
    environment = identity()
    environment["tcl_library"] = app.tk.eval("info library")
    environment["tk_library"] = app.tk.eval("set tk_library")
    environment["executable"] = sys.executable
    environment["tk_scaling"] = float(app.tk.call("tk", "scaling"))
    environment["screen_size"] = [app.winfo_screenwidth(), app.winfo_screenheight()]
    environment["ui_font"] = app.tk.call("font", "actual", "TkDefaultFont")
    if sys.platform == "win32":
        import ctypes
        awareness = ctypes.c_int()
        status = ctypes.windll.shcore.GetProcessDpiAwareness(None, ctypes.byref(awareness))
        environment["dpi_awareness"] = awareness.value if status == 0 else None

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
            check("count-default-decimal", lambda: equal(app.tx.variables["count_format"].get(), "Decimal"))
            if sys.platform == "win32":
                check("system-dpi-aware", lambda: equal(environment["dpi_awareness"], 1))
                check("english-ui-font", lambda: equal(app.tk.call("font", "actual", "TkDefaultFont", "-family") in ("Segoe UI", "Arial"), True))
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
                    if not receiving and itg and not cip:
                        check("independent-mac-primary-output", lambda: equal(panel.primary_output().format("Hex"), tx["mac_i"]["hex"]))
                    check(f"{prefix}-mac-field-{cip}-{itg}", lambda: equal(str(panel.mac_entry.cget("state")), "normal" if receiving and itg and not cip else "disabled"))
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
            panel.input.insert("1.0", "00 01 ab")
            panel.convert_input()
            check("hex-to-bit-leading-zero", lambda: equal(panel.input.get("1.0", "end-1c"), "000000000000000110101011"))
            panel.convert_input()
            check("bit-to-hex-uppercase-spaces", lambda: equal(panel.input.get("1.0", "end-1c"), "00 01 AB"))
            panel.calculate()
            check("hex-output-uppercase-spaces", lambda: equal(panel.output.get("1.0", "end-1c"), format_data(panel.primary_output())))
            panel.copy_output()
            check("clipboard-formatted-hex", lambda: equal(panel.clipboard_get(), panel.output.get("1.0", "end-1c")))
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
            panel = app.rx
            v = panel.variables
            v["cipher_enabled"].set(True)
            v["integrity_enabled"].set(True)
            v["ciphering"].set(ALGORITHMS[2])
            v["integrity"].set(ALGORITHMS[2])
            v["data_format"].set("Bit")
            panel.refresh()
            options = dict(ciphering=2, integrity=2, enc_key=bytes.fromhex(v["enc_key"].get()), int_key=bytes.fromhex(v["int_key"].get()))
            tx = transmit(Bits.parse("00010100101", "Bit"), **options)
            bits = tx["data"]["bits"]
            bad = ("1" if bits[0] == "0" else "0") + bits[1:]
            panel.input.delete("1.0", "end")
            panel.input.insert("1.0", bad)
            panel.calculate()
            check("failed-verification-visible", lambda: equal(panel.output_title.cget("text").split(" — ")[0], "Data failed authentication"))
            check("failed-not-input-error", lambda: equal(panel.result["authentication"], "failed"))
            panel.input.delete("1.0", "end")
            panel.input.insert("1.0", "101")
            panel.calculate()
            check("short-receive-input-error", lambda: equal(panel.result, None))
            check("short-receive-clears-output", lambda: equal(panel.output.get("1.0", "end-1c"), ""))
            v["direction"].set("1 — DL")
            app.notebook.select(app.tx)
            app.notebook.select(app.rx)
            check("tabs-do-not-invert-direction", lambda: equal(v["direction"].get(), "1 — DL"))

            # Shared settings update widgets in both directions; payloads stay local.
            from .gui import SHARED_SETTINGS
            for origin, target, prefix in [(app.tx, app.rx, "tx-to-rx"), (app.rx, app.tx, "rx-to-tx")]:
                app.notebook.select(origin)
                app.update()
                for name, value in [("cipher_enabled", False), ("integrity_enabled", True),
                                    ("ciphering", ALGORITHMS[1]), ("integrity", ALGORITHMS[3]),
                                    ("enc_key", "00 01"), ("int_key", "0001"),
                                    ("enc_format", "Bit"), ("int_format", "Bit"),
                                    ("count", "37"), ("count_format", "Decimal"), ("bearer", "17"),
                                    ("direction", "1 — DL")]:
                    origin.variables[name].set(value)
                origin.input.delete("1.0", "end")
                origin.input.insert("1.0", prefix)
                target.input.delete("1.0", "end")
                target.input.insert("1.0", "target-payload")
                app.notebook.select(target)
                app.update()
                def shared_check():
                    for name in SHARED_SETTINGS:
                        equal(origin.variables[name].get(), target.variables[name].get())
                    equal(str(target.cip_combo.cget("state")), "disabled")
                    equal(str(target.int_entry.cget("state")), "normal")
                    equal(str(target.enc_entry.cget("state")), "disabled")
                    equal(target.input.get("1.0", "end-1c"), "target-payload")
                    equal(origin.input.get("1.0", "end-1c"), prefix)
                check(prefix + "-shared-settings-local-data", shared_check)

            # Drive official non-byte-aligned inputs through real GUI widgets.
            dataset = data_dir()
            inputs = json.loads((dataset / "inputs.json").read_text(encoding="utf-8"))
            expected = json.loads((dataset / "expected.json").read_text(encoding="utf-8"))
            # One fixed official EIA2 case through all three COUNT representations.
            inp = inputs["Itg2-002"]
            ref = Bits(bytes.fromhex(expected["Itg2-002"]["buffer_hex"]), 32)
            for fmt, value in [("Decimal", str(inp["count"])), ("Hex", format(inp["count"], "08X")),
                               ("Bit", format(inp["count"], "032b"))]:
                for panel in (app.tx, app.rx):
                    v = panel.variables
                    v["cipher_enabled"].set(False)
                    v["integrity_enabled"].set(True)
                    v["integrity"].set(ALGORITHMS[2])
                    v["int_key"].set(inp["key"])
                    v["int_format"].set("Hex")
                    v["count_format"].set(fmt)
                    v["count"].set(value)
                    v["bearer"].set(str(inp["bearer"]))
                    v["direction"].set("1 — DL")
                    v["data_format"].set("Hex")
                    v["output_format"].set("Hex")
                    v["received_mac"].set(format_data(ref))
                    panel.input.delete("1.0", "end")
                    panel.input.insert("1.0", inp["buffer_hex"])
                    panel.calculate()
                    def count_check():
                        assert panel.result is not None, panel.status.cget("text")
                        if panel.receiving:
                            equal(panel.result["authentication"], "passed")
                        else:
                            equal(panel.output.get("1.0", "end-1c"), "B9 37 87 E6")
                    check(f"count-{fmt}-{'rx' if panel.receiving else 'tx'}-official", count_check)
            panel = app.tx
            panel.variables["count_format"].set("Decimal")
            panel.variables["count"].set("4294967296")
            panel.calculate()
            check("count-overflow-input-error", lambda: equal(panel.result, None))
            for case in ("Cip2-001", "Itg2-001"):
                panel = app.tx
                v = panel.variables
                inp = inputs[case]
                v["cipher_enabled"].set(case.startswith("Cip"))
                v["integrity_enabled"].set(case.startswith("Itg"))
                v["ciphering"].set(ALGORITHMS[2])
                v["integrity"].set(ALGORITHMS[2])
                v["enc_key"].set(inp["key"])
                v["int_key"].set(inp["key"])
                v["enc_format"].set("Hex")
                v["int_format"].set("Hex")
                v["count_format"].set("Hex")
                v["count"].set(format(inp["count"], "08x"))
                v["bearer"].set(str(inp["bearer"]))
                v["direction"].set(f"{inp['direction']} — {'DL' if inp['direction'] else 'UL'}")
                v["data_format"].set("Bit")
                panel.refresh()
                panel.input.delete("1.0", "end")
                panel.input.insert("1.0", Bits(bytes.fromhex(inp["buffer_hex"]), inp["bit_length"]).format("Bit"))
                panel.calculate()
                ref = Bits(bytes.fromhex(expected[case]["buffer_hex"]), expected[case]["bit_length"])
                check("gui-official-" + case, lambda: equal(panel.primary_output(), ref))
            v["data_format"].set("Hex")
            panel.input.delete("1.0", "end")
            panel.input.insert("1.0", "0")
            panel.calculate()
            check("odd-hex-input-error", lambda: equal(panel.result, None))

            # Every new official NEA/NIA case enters through the same widgets as user data.
            new_inputs = json.loads((dataset / "256/inputs.json").read_text(encoding="utf-8"))
            new_expected = json.loads((dataset / "256/expected.json").read_text(encoding="utf-8"))
            for case, inp in new_inputs.items():
                if not case.startswith(("NEA", "NIA")):
                    continue
                enc = case.startswith("NEA")
                original = Bits(bytes.fromhex(inp["buffer_hex"]), inp["bit_length"])
                exp = new_expected[case]
                reference = Bits(bytes.fromhex(exp["buffer_hex"]), exp["bit_length"])
                for panel in (app.tx, app.rx):
                    v = panel.variables
                    v["ciphering"].set(ALGORITHMS[inp["algorithm"]])
                    v["integrity"].set(ALGORITHMS[inp["algorithm"]])
                    v["cipher_enabled"].set(enc)
                    v["integrity_enabled"].set(not enc)
                    for name in ("enc_key", "int_key"):
                        v[name].set(inp["key"])
                    for name in ("enc_format", "int_format", "extra_format", "mac_format"):
                        v[name].set("Hex")
                    v["count_format"].set("Decimal")
                    v["count"].set(str(inp["count"]))
                    v["bearer"].set(str(inp["bearer"]))
                    v["direction"].set(f"{inp['direction']} — {'DL' if inp['direction'] else 'UL'}")
                    v["extra_iv"].set(inp["extra_iv"])
                    if not enc:
                        v["mac_bytes"].set(str(inp["mac_bytes"]))
                    v["data_format"].set("Bit")
                    v["received_mac"].set(format_data(reference) if not enc else "")
                    panel.input.delete("1.0", "end")
                    payload = reference if enc and panel.receiving else original
                    panel.input.insert("1.0", payload.format("Bit"))
                    panel.execute_button.invoke()

                    def official_check():
                        assert panel.result is not None, panel.status.cget("text")
                        if panel.receiving:
                            equal(panel.result["data"], original.to_dict())
                            if not enc:
                                equal(panel.result["authentication"], "passed")
                        else:
                            equal(panel.primary_output(), reference)
                        equal(str(panel.extra_entry.cget("state")), "normal")
                        equal(str(panel.mac_bytes_combo.cget("state")), "disabled" if enc else "readonly")
                    check(f"gui-official-{case}-{'rx' if panel.receiving else 'tx'}", official_check)

            # A 120-bit MAC is appended/split at the exact bit boundary in mixed families.
            for panel in (app.tx, app.rx):
                v = panel.variables
                v["cipher_enabled"].set(True)
                v["integrity_enabled"].set(True)
                v["ciphering"].set(ALGORITHMS[4])
                v["integrity"].set(ALGORITHMS[6])
                v["mac_bytes"].set("15")
                panel.input.delete("1.0", "end")
                panel.input.insert("1.0", "0010101" if not panel.receiving else combined_payload)
                panel.execute_button.invoke()
                if not panel.receiving:
                    combined_payload = panel.result["data"]["bits"]
                    check("variable-mac-tx-combined", lambda: equal(panel.result["data"]["bit_length"], 127))
                    check("variable-mac-detail-length", lambda: equal("(120 bit)" in panel.details.get("1.0", "end-1c"), True))
                else:
                    check("variable-mac-rx-combined", lambda: equal(panel.result["data"]["bits"], "0010101"))
                    check("variable-mac-rx-authenticated", lambda: equal(panel.result["authentication"], "passed"))
                    payload = panel.input.get("1.0", "end-1c")
                    panel.input.delete("1.0", "end")
                    panel.input.insert("1.0", ("1" if payload[0] == "0" else "0") + payload[1:])
                    panel.execute_button.invoke()
                    check("variable-mac-tamper-fails", lambda: equal(panel.result["authentication"], "failed"))
                    check("variable-mac-tamper-visible", lambda: equal(panel.output_title.cget("text").startswith("Data failed authentication"), True))
            # Shared settings changes above invalidate both results; keep the saved payload local.
            panel = app.tx
            panel.variables["extra_iv"].set("00")
            panel.calculate()
            check("short-extra-iv-input-error", lambda: equal(panel.result, None))
            panel.variables["extra_iv"].set("00" * 6)
            panel.variables["enc_key"].set("00" * 16)
            panel.calculate()
            check("short-256-key-input-error", lambda: equal(panel.result, None))
        except Exception:
            cases.append({"id": "smoke-driver", "status": "FAIL", "error": traceback.format_exc()})
        finally:
            dest = Path(output)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps({"category": "gui_widgets", "environment": environment, "cases": cases,
                                       "passed": sum(c["status"] == "PASS" for c in cases), "total": len(cases)}, indent=2) + "\n", encoding="utf-8")
            app.destroy()

    app.after(400, tests)
    app.mainloop()
    return 0 if cases and all(c["status"] == "PASS" for c in cases) else 1
