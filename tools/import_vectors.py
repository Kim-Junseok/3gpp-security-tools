"""Transcribe original pdftotext data; never import the calculation Core.

Run only when intentionally updating the fixed vector dataset.
"""

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def clean(name):
    text = (ROOT / "local-specs" / name).read_text().replace("\f", "\n")
    lines = []
    for line in text.splitlines():
        if re.search(r"3GPP TS|ETSI TS|^\s*ETSI\s*$|page \d+ of|^\s*Implementor", line):
            continue
        lines.append(line)
    return "\n".join(lines)


def field(text, name):
    pattern = r"^\s*(?:" + name + r")\s*(?:=|:)\s*(?:\(hex\)\s*)?([0-9a-fA-F ]*)$"
    match = re.search(pattern, text, re.M | re.I)
    if not match:
        raise ValueError("Missing field " + name)
    parts = [match[1]]
    rest = text[match.end():].splitlines()
    for line in rest:
        if not line.strip():
            continue
        line = re.sub(r"^\s*\(hex\)\s*", "", line, flags=re.I)
        if re.fullmatch(r"\s*[0-9a-fA-F]+(?:\s+[0-9a-fA-F]+)*\s*", line):
            parts.append(line)
        else:
            break
    return re.sub(r"\s+", "", "".join(parts)).lower()


def sections(text, prefix):
    pattern = r"^\s*(" + re.escape(prefix) + r"\.\d+\.?)\s+Test Set (\d+)\s*$"
    matches = list(re.finditer(pattern, text, re.M))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end]
        # End before the next top-level test section when this is the last set.
        body = re.split(r"\n(?:C\.[1-4]\s|[345]\.\s+|[345]\s+\n)", body)[0]
        yield m[1].rstrip("."), int(m[2]), body


def main():
    specs = [
        ("Cip2", "ts_133401v190200p.txt", "C.1", "TS 33.401", "19.2.0", "Key", "Count", "Plaintext", "Ciphertext", 6),
        ("Itg2", "ts_133401v190200p.txt", "C.2", "TS 33.401", "19.2.0", "IK", "Count-I", "Message", "MACT", 8),
        ("Itg1", "ts_133401v190200p.txt", "C.4", "TS 33.401", "19.2.0", "IK", "Count-I", "Message", "MACT", 7),
        ("Cip3", "eea3-eia3-test-v11.txt", "4", "SAGE EEA3/EIA3 Document 3", "1.1", "Key", "Count", "Plaintext", "Ciphertext", 5),
        ("Itg3", "eea3-eia3-test-v11.txt", "5", "SAGE EEA3/EIA3 Document 3", "1.1", "Key", "Count", "Message", "MAC", 5),
        ("Cip1", "uea2-uia2-test-v11.txt", "4", "SAGE UEA2/UIA2 Document 3", "1.1", "CK", "Count-C", "Plaintext", None, 5),
    ]
    urls = {
        "ts_133401v190200p.txt": "https://www.etsi.org/deliver/etsi_ts/133400_133499/133401/19.02.00_60/ts_133401v190200p.pdf",
        "uea2-uia2-test-v11.txt": "https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/Doc3-UEA2-UIA2-Spec-Implementors-Test-Data.pdf",
        "eea3-eia3-test-v11.txt": "https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/eea3eia3testdatav11.pdf",
    }
    manifest = {"schema_version": 1, "required_total": 36, "suites": {}}
    inputs, expected = {}, {}
    for suite, filename, prefix, doc, version, keyname, countname, dataname, outname, required in specs:
        text = clean(filename)
        rows = list(sections(text, prefix))
        assert len(rows) == required, (suite, len(rows))
        manifest["suites"][suite] = {"required": required, "cases": []}
        for section, number, body in rows:
            case = f"{suite}-{number:03}"
            length = int(re.search(r"Length\s*=\s*(\d+)\s*bits", body, re.I)[1])
            if case == "Cip1-005":
                # Source p14 omits the leading nibble of this 32-bit word.
                # Its own row 18 independently gives AE56E26E xor A85E94CE
                # = 060876A0. This is source normalization, not Core output.
                assert "60876A0" in body
                body = body.replace("60876A0", "060876A0", 1)
            datahex = field(body, dataname)
            if outname:
                answer = field(body, outname)
            else:
                # UEA2 official output is the right column of the enc/dec table.
                table = body.split("enc/dec data")[1]
                output_rows = re.findall(r"^\s*\d+\s+([0-9A-F ]+?)\s{2,}([0-9A-F ]+)\s*$", table, re.M)
                answer = "".join(re.sub(r"\s+", "", row[1]) for row in output_rows).lower()
            for label, value, valid in [("input", datahex, length), ("expected", answer, length if suite.startswith("Cip") else 32)]:
                if len(value) % 2 or len(value) * 4 < valid:
                    raise ValueError((case, label, len(value), valid))
            key = field(body, keyname)
            assert len(key) == 32, (case, key)
            inputs[case] = {"key": key, "count": int(field(body, countname), 16),
                            "bearer": int(field(body, "Bearer"), 16), "direction": int(field(body, "Direction"), 16),
                            "buffer_hex": datahex, "bit_length": length}
            expected[case] = {"buffer_hex": answer, "bit_length": length if suite.startswith("Cip") else 32}
            manifest["suites"][suite]["cases"].append({"id": case, "document": doc, "version": version,
                "section": section, "source_test_set": number, "url": urls[filename],
                "source_sha256": hashlib.sha256((ROOT / "local-specs" / filename.replace(".txt", ".pdf")).read_bytes()).hexdigest()})
            if case == "Cip1-005":
                manifest["suites"][suite]["cases"][-1]["transcription_note"] = "p14 plaintext word 19: 60876A0 normalized to 060876A0; original row 18 keystream AE56E26E xor enc/dec A85E94CE corroborates the leading zero. No implementation output used."
        print(suite, len(rows), "transcribed")
    dest = ROOT / "testdata"
    for name, data in [("manifest", manifest), ("inputs", inputs), ("expected", expected)]:
        (dest / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
