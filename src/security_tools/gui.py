"""Tkinter transmit/receive interface; all calculations go through adapter/Core."""

import sys
import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from .adapter import COUNT_FORMATS, execute, format_data
from .bits import Bits, from_result
from .errors import SecurityToolsError

ALGORITHMS = ["0 — Null (no protection)", "1 — SNOW 3G (128-bit)", "2 — AES (128-bit)", "3 — ZUC (128-bit)",
              "4 — SNOW 5G (256-bit)", "5 — AES (256-bit)", "6 — ZUC (256-bit)"]
SHARED_SETTINGS = ("cipher_enabled", "integrity_enabled", "ciphering", "integrity", "enc_key", "int_key",
                   "enc_format", "int_format", "count", "count_format", "bearer", "direction",
                   "extra_iv", "extra_format", "mac_bytes")


def enable_windows_dpi():
    """Match Tk 8.6's system-DPI layout before it creates any windows."""
    if sys.platform != "win32":
        return
    import ctypes
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    try:
        set_awareness = user32.SetProcessDpiAwarenessContext
        set_awareness.argtypes = [ctypes.c_void_p]
        set_awareness.restype = ctypes.c_bool
        # A frozen EXE sets this through its manifest; source launches use the API.
        set_awareness(ctypes.c_void_p(-2))
    except AttributeError:
        user32.SetProcessDPIAware()


class Panel(ttk.Frame):
    def __init__(self, parent, receiving=False, settings=None):
        super().__init__(parent, padding=12)
        self.receiving = receiving
        self.result = None
        self.variables = dict(settings or {})
        self.columnconfigure(1, weight=1)
        for name, default in [("cipher_enabled", True), ("integrity_enabled", True)]:
            if name not in self.variables:
                self.variables[name] = tk.BooleanVar(value=default)
        defaults = dict(ciphering=ALGORITHMS[2], integrity=ALGORITHMS[2], enc_key="", int_key="",
                        enc_format="Hex", int_format="Hex", count="0", count_format="Decimal", bearer="0", direction="0 — UL",
                        extra_iv="00 00 00 00 00 00", extra_format="Hex", mac_bytes="4",
                        data_format="Hex", output_format="Hex")
        for name, default in defaults.items():
            if name not in self.variables:
                self.variables[name] = tk.StringVar(value=default)
        self.cip_check = ttk.Checkbutton(self, text="Enable Ciphering", variable=self.variables["cipher_enabled"])
        self.cip_check.grid(row=0, column=0, sticky="w", pady=3)
        self.cip_combo = ttk.Combobox(self, textvariable=self.variables["ciphering"], values=ALGORITHMS, state="readonly", width=30)
        self.cip_combo.grid(row=0, column=1, sticky="ew", pady=3)
        self.itg_check = ttk.Checkbutton(self, text="Enable Integrity", variable=self.variables["integrity_enabled"])
        self.itg_check.grid(row=1, column=0, sticky="w", pady=3)
        self.itg_combo = ttk.Combobox(self, textvariable=self.variables["integrity"], values=ALGORITHMS, state="readonly", width=30)
        self.itg_combo.grid(row=1, column=1, sticky="ew", pady=3)
        self.enc_entry, self.enc_fmt = self.entry_row(2, "K_enc", "enc_key", "enc_format")
        self.int_entry, self.int_fmt = self.entry_row(3, "K_int", "int_key", "int_format")
        self.count_entry, self.count_fmt = self.entry_row(4, "COUNT (32-bit unsigned)", "count", "count_format")
        self.bearer_entry, _ = self.entry_row(5, "BEARER (decimal, 0–31)", "bearer")
        ttk.Label(self, text="Radio DIRECTION").grid(row=6, column=0, sticky="w", padx=(0, 12), pady=3)
        self.direction_combo = ttk.Combobox(self, textvariable=self.variables["direction"], values=["0 — UL", "1 — DL"], state="readonly")
        self.direction_combo.grid(row=6, column=1, sticky="ew", pady=3)
        self.extra_entry, self.extra_fmt = self.entry_row(7, "EXTRA_IV (48-bit)", "extra_iv", "extra_format")
        ttk.Label(self, text="MAC-I length (bytes)").grid(row=8, column=0, sticky="w", pady=3)
        self.mac_bytes_combo = ttk.Combobox(self, textvariable=self.variables["mac_bytes"],
                                           values=[str(n) for n in range(4, 17)], width=8, state="readonly")
        self.mac_bytes_combo.grid(row=8, column=1, sticky="w", pady=3)
        ttk.Label(self, text="Input data").grid(row=9, column=0, sticky="w", pady=(6, 3))
        formats = ttk.Frame(self)
        formats.grid(row=9, column=1, sticky="e")
        self.data_combo = ttk.Combobox(formats, textvariable=self.variables["data_format"], values=["Hex", "Bit"], width=6, state="readonly")
        self.data_combo.pack(side="left", padx=4)
        ttk.Button(formats, text="Convert Hex ↔ Bit", command=self.convert_input).pack(side="left")
        self.input = ScrolledText(self, height=4, wrap="word", font="TkFixedFont", undo=True)
        self.input.grid(row=10, column=0, columnspan=3, sticky="nsew", pady=4)
        self.rowconfigure(10, weight=1)
        self.input.bind("<<Modified>>", self.input_changed)
        self.length_label = ttk.Label(self, text="Valid length: 0 bit", wraplength=780, justify="left")
        self.length_label.grid(row=11, column=0, columnspan=3, sticky="ew")
        self.length_label.bind("<Configure>", self.fit_notice_width)
        self.execute_button = ttk.Button(self, command=self.calculate)
        self.execute_button.grid(row=13, column=0, columnspan=3, sticky="ew", pady=6)
        self.status = ttk.Label(self, text="", wraplength=780, justify="left")
        self.status.grid(row=14, column=0, columnspan=3, sticky="ew")
        self.status.bind("<Configure>", self.fit_notice_width)
        self.output_title = ttk.Label(self, text="Result")
        self.output_title.grid(row=15, column=0, sticky="w", pady=(8, 4))
        output_controls = ttk.Frame(self)
        output_controls.grid(row=15, column=1, sticky="e")
        self.output_combo = ttk.Combobox(output_controls, textvariable=self.variables["output_format"], values=["Hex", "Bit"], state="readonly", width=6)
        self.output_combo.pack(side="left", padx=4)
        self.copy_button = ttk.Button(output_controls, text="Copy result", command=self.copy_output, state="disabled")
        self.copy_button.pack(side="left")
        self.output = ScrolledText(self, height=4, wrap="word", font="TkFixedFont", state="disabled")
        self.output.grid(row=16, column=0, columnspan=3, sticky="nsew")
        self.rowconfigure(16, weight=1)
        self.details = ScrolledText(self, height=3, wrap="word", font="TkDefaultFont", state="disabled")
        self.details.grid(row=17, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        for name in SHARED_SETTINGS:
            self.variables[name].trace_add("write", lambda *_: self.refresh())
        self.data_combo.bind("<<ComboboxSelected>>", lambda _: self.update_length())
        self.output_combo.bind("<<ComboboxSelected>>", lambda _: self.render())
        self.refresh()

    @staticmethod
    def fit_notice_width(event):
        # Tk reports physical pixels, matching the DPI-scaled font and layout.
        width = max(1, event.width)
        if int(event.widget.cget("wraplength")) != width:
            event.widget.configure(wraplength=width)

    def entry_row(self, row, label, name, fmt=None):
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=3)
        entry = ttk.Entry(self, textvariable=self.variables[name], font="TkFixedFont")
        entry.grid(row=row, column=1, sticky="ew", pady=3)
        combo = None
        if fmt:
            values = COUNT_FORMATS if fmt == "count_format" else ("Hex", "Bit")
            combo = ttk.Combobox(self, textvariable=self.variables[fmt], values=values, width=8, state="readonly")
            combo.grid(row=row, column=2, padx=(6, 0))
        return entry, combo

    def selection(self):
        v = self.variables
        return (int(v["ciphering"].get()[0]) if v["cipher_enabled"].get() else None,
                int(v["integrity"].get()[0]) if v["integrity_enabled"].get() else None)

    def refresh(self):
        c, i = self.selection()
        for combo, enabled in [(self.cip_combo, c is not None), (self.itg_combo, i is not None)]:
            combo.configure(state="readonly" if enabled else "disabled")
        for entry, combo, needed in [(self.enc_entry, self.enc_fmt, c not in (None, 0)),
                                     (self.int_entry, self.int_fmt, i not in (None, 0))]:
            entry.configure(state="normal" if needed else "disabled")
            combo.configure(state="readonly" if needed else "disabled")
        needs_params = c not in (None, 0) or i not in (None, 0)
        for entry in (self.count_entry, self.bearer_entry):
            entry.configure(state="normal" if needs_params else "disabled")
        self.count_fmt.configure(state="readonly" if needs_params else "disabled")
        self.direction_combo.configure(state="readonly" if needs_params else "disabled")
        newer = c in (4, 5, 6) or i in (4, 5, 6)
        self.extra_entry.configure(state="normal" if newer else "disabled")
        self.extra_fmt.configure(state="readonly" if newer else "disabled")
        self.mac_bytes_combo.configure(state="readonly" if i in (4, 5, 6) else "disabled")
        if i not in (4, 5, 6) and self.variables["mac_bytes"].get() != "4":
            self.variables["mac_bytes"].set("4")
        if c is not None and i is not None:
            action = "Decrypt → Extract MAC-I → Verify" if self.receiving else "Generate MAC-I → Append → Encrypt"
        elif c is not None:
            action = "Decrypt" if self.receiving else "Encrypt"
        elif i is not None:
            action = "Extract MAC-I → Verify" if self.receiving else "Generate MAC-I"
        else:
            action = "Select Ciphering or Integrity"
        self.execute_button.configure(text=action, state="disabled" if c is None and i is None else "normal")
        self.result = None
        self.copy_button.configure(state="disabled")
        self.set_text(self.output, "")
        self.set_text(self.details, "")
        if i == 0:
            self.status.configure(text="Null Integrity — No authentication protection. A matching MAC does not authenticate the data.")
        elif c == 0:
            self.status.configure(text="Null Ciphering — No encryption protection.")
        else:
            self.status.configure(text="Input data: ciphertext of Data + MAC-I." if self.receiving and c is not None and i is not None
                                  else "Input data: Data + MAC-I (MAC-I at the end)." if self.receiving and i is not None
                                  else "Transmit and Receive share keys, algorithms, COUNT, BEARER, and DIRECTION.")

    def fields(self):
        result = {name: var.get() for name, var in self.variables.items()}
        result["ciphering"] = int(result["ciphering"][0])
        result["integrity"] = int(result["integrity"][0])
        result["direction"] = int(result["direction"][0])
        result["data"] = self.input.get("1.0", "end-1c")
        return result

    def input_changed(self, _=None):
        if self.input.edit_modified():
            self.update_length()
            self.input.edit_modified(False)

    def update_length(self):
        try:
            bits = Bits.parse(self.input.get("1.0", "end-1c"), self.variables["data_format"].get())
            self.length_label.configure(text=f"Valid length: {bits.length} bit")
        except SecurityToolsError as e:
            self.length_label.configure(text=f"Input error: {e}")

    def convert_input(self):
        try:
            current = self.variables["data_format"].get()
            bits = Bits.parse(self.input.get("1.0", "end-1c"), current)
            target = "Bit" if current == "Hex" else "Hex"
            text = format_data(bits, target)
            self.variables["data_format"].set(target)
            self.input.delete("1.0", "end")
            self.input.insert("1.0", text)
            self.update_length()
        except SecurityToolsError as e:
            self.status.configure(text=f"Input error: {e}")

    def calculate(self):
        try:
            self.result = execute(self.fields(), self.receiving)
            if self.result["data"]["bit_length"] % 8:
                self.variables["output_format"].set("Bit")
            self.render()
            state = self.result["authentication"]
            messages = {"passed": "MAC-I verification passed", "failed": "MAC-I verification failed — The data below failed authentication.",
                        "unprotected": "No authentication protection", "generated": "MAC-I generated"}
            self.status.configure(text=messages[state] + (" / No encryption protection" if self.result["ciphering"] == 0 else ""))
            self.copy_button.configure(state="normal")
        except SecurityToolsError as e:
            self.result = None
            self.set_text(self.output, "")
            self.set_text(self.details, "")
            self.copy_button.configure(state="disabled")
            self.status.configure(text=f"Input error ({e.code}): {e}")
        except Exception:
            self.result = None
            self.set_text(self.output, "")
            self.set_text(self.details, "")
            self.copy_button.configure(state="disabled")
            self.status.configure(text="Execution error: Could not complete the calculation.")

    @staticmethod
    def set_text(widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def render(self):
        if self.result is None:
            return
        r = self.result
        data = self.primary_output()
        if data.length % 8:
            self.variables["output_format"].set("Bit")
            self.output_combo.configure(values=["Bit"])
        else:
            self.output_combo.configure(values=["Hex", "Bit"])
        self.set_text(self.output, format_data(data, self.variables["output_format"].get()))
        title = "Plaintext" if self.receiving else "Ciphertext"
        if not self.receiving and r["ciphering"] is None and "mac_i" in r:
            title = "MAC-I"
        elif r["ciphering"] is None:
            title = "Original data"
        if r["authentication"] == "failed":
            title = "Data failed authentication"
        self.output_title.configure(text=f"{title} — {data.length} bit")
        details = [f"Input length: {r['input_bit_length']} bit / Output length: {data.length} bit"]
        if not self.receiving and r["ciphering"] is None and "mac_i" in r:
            original = from_result(r["data"])
            details.append(f"Original data ({original.length} bit): {format_data(original, 'Bit' if original.length % 8 else 'Hex')}")
        if "cipher_bit_length" in r:
            details.append(f"Cipher input length (including appended MAC-I): {r['cipher_bit_length']} bit")
        for key, label in [("mac_i", "Generated MAC-I (intermediate verification value)"), ("received_mac", "Extracted MAC-I"), ("calculated_mac", "Calculated MAC-I")]:
            if key in r:
                details.append(f"{label}: {format_data(from_result(r[key]))} ({r[key]['bit_length']} bit)")
        self.set_text(self.details, "\n".join(details))

    def copy_output(self):
        if self.result is not None:
            text = format_data(self.primary_output(), self.variables["output_format"].get())
            self.clipboard_clear()
            self.clipboard_append(text)

    def primary_output(self):
        r = self.result
        return from_result(r["mac_i"] if not self.receiving and r["ciphering"] is None and "mac_i" in r else r["data"])


class Application(tk.Tk):
    def __init__(self):
        enable_windows_dpi()
        super().__init__()
        self.title("3GPP Security Tools")
        families = set(font.families(self))
        ui_family = next((name for name in ("Segoe UI", "Arial") if name in families),
                         font.nametofont("TkDefaultFont").actual("family"))
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont", "TkCaptionFont", "TkTooltipFont"):
            font.nametofont(name).configure(family=ui_family, size=10)
        font.nametofont("TkFixedFont").configure(family="Consolas", size=11)
        scale = float(self.tk.call("tk", "scaling")) / (96 / 72)
        width = min(round(1000 * scale), self.winfo_screenwidth() - round(40 * scale))
        height = min(round(940 * scale), self.winfo_screenheight() - round(80 * scale))
        self.geometry(f"{width}x{height}")
        self.minsize(min(round(860 * scale), width), min(round(780 * scale), height))
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure(".", font="TkDefaultFont")
        ttk.Label(self, text="3GPP Security Tools", font=("Segoe UI", 18, "bold"), padding=(16, 12)).pack(anchor="w")
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=12)
        self.canvas = tk.Canvas(body, highlightthickness=0)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        notebook = ttk.Notebook(self.canvas)
        window = self.canvas.create_window((0, 0), window=notebook, anchor="nw")

        def fit_body(event=None):
            # Preserve usable text areas on short screens; the scrollbar reaches
            # every control when the notebook's requested height cannot fit.
            self.canvas.itemconfigure(window, width=self.canvas.winfo_width(),
                                      height=max(self.canvas.winfo_height(), notebook.winfo_reqheight()))
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.bind("<Configure>", fit_body)
        notebook.bind("<Configure>", fit_body)
        self.tx = Panel(notebook)
        settings = {name: self.tx.variables[name] for name in SHARED_SETTINGS}
        self.rx = Panel(notebook, receiving=True, settings=settings)
        notebook.add(self.tx, text="  Transmit  ")
        notebook.add(self.rx, text="  Receive  ")
        self.notebook = notebook
        self.footer = ttk.Label(self, text="Legacy 0–3 / 256-bit NEA/NIA 4–6 · MAC-append/encrypt pipeline · NCA and PDU parsing excluded", padding=(12, 8))
        self.footer.pack(anchor="w")


def main():
    Application().mainloop()


if __name__ == "__main__":
    main()
