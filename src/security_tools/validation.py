"""Official vector runner. Expected files are read-only inputs to this module."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone

from . import __version__
from .bits import Bits
from .core import cipher, mac
from .errors import VectorError


def data_dir():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "testdata"
    return Path(__file__).resolve().parents[2] / "testdata"


def identity():
    root = Path(__file__).resolve().parents[2]
    commit, dirty = None, None
    if not getattr(sys, "frozen", False):
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, stderr=subprocess.DEVNULL, text=True).strip()
            dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True))
        except (OSError, subprocess.CalledProcessError):
            pass
    h = hashlib.sha256()
    for path in sorted(Path(__file__).resolve().parent.rglob("*.py")):
        h.update(str(path.relative_to(Path(__file__).parent)).encode())
        h.update(path.read_bytes())
    build_file = (Path(sys._MEIPASS) if getattr(sys, "frozen", False) else root) / "build-info.json"
    build = json.loads(build_file.read_text()) if build_file.exists() else None
    if getattr(sys, "frozen", False) and build:
        commit, dirty = build.get("commit"), build.get("dirty")
        h = hashlib.sha256(json.dumps(build["files"], sort_keys=True).encode())
    return {"version": __version__, "commit": commit, "dirty": dirty,
            "source_sha256": h.hexdigest(), "build": build,
            "frozen": bool(getattr(sys, "frozen", False)), "python": sys.version,
            "executable": sys.executable, "bundle_root": getattr(sys, "_MEIPASS", None),
            "platform": platform.platform(), "utc": datetime.now(timezone.utc).isoformat()}


def _legacy_run(suites=None, output=None, source=None):
    source = Path(source) if source else data_dir()
    try:
        manifest, inputs, expected = [json.loads((source / f"{name}.json").read_text(encoding="utf-8"))
                                      for name in ("manifest", "inputs", "expected")]
    except (OSError, ValueError) as e:
        raise VectorError(f"Official vector files are unavailable: {e}") from e
    required_counts = {"Cip1": 5, "Itg1": 7, "Cip2": 6, "Itg2": 8, "Cip3": 5, "Itg3": 5}
    if set(manifest["suites"]) != set(required_counts) or manifest["required_total"] != 36:
        raise VectorError("Manifest must declare the fixed six suites and 36 required cases.")
    chosen = list(suites) if suites else list(required_counts)
    if any(s not in required_counts for s in chosen):
        raise VectorError("Unknown suite selection.")
    report = {"category": "official", "environment": identity(), "suites": {}, "cases": [], "actual": {}}
    report["dataset_sha256"] = {name: hashlib.sha256((source / f"{name}.json").read_bytes()).hexdigest()
                                 for name in ("manifest", "inputs", "expected")}
    for suite in chosen:
        entry = manifest["suites"][suite]
        required = required_counts[suite]
        records = entry["cases"]
        expected_ids = {f"{suite}-{i:03}" for i in range(1, required + 1)}
        if entry["required"] != required or len(records) != required or {r["id"] for r in records} != expected_ids:
            raise VectorError(f"{suite}: required case inventory changed or contains duplicates.")
        counts = Counter({s: 0 for s in ("PASS", "FAIL", "ERROR", "SKIP", "BLOCKED")})
        for record in records:
            case = record["id"]
            row = {"id": case, "source": record}
            try:
                inp, exp = inputs[case], expected[case]
                data = Bits(bytes.fromhex(inp["buffer_hex"]), inp["bit_length"])
                reference = Bits(bytes.fromhex(exp["buffer_hex"]), exp["bit_length"])
                fn = cipher if suite.startswith("Cip") else mac
                actual = fn(int(suite[-1]), bytes.fromhex(inp["key"]), inp["count"], inp["bearer"], inp["direction"], data)
                report["actual"][case] = actual.to_dict()
                row.update(status="PASS" if actual == reference else "FAIL", expected=reference.to_dict(), actual=actual.to_dict())
                if actual != reference:
                    row["first_mismatch_bit"] = next((i for i, (a, b) in enumerate(zip(actual.format("Bit"), reference.format("Bit"))) if a != b), min(actual.length, reference.length))
            except KeyError as e:
                row.update(status="BLOCKED", error=f"Missing input/expected field: {e}")
            except Exception as e:
                row.update(status="ERROR", error=f"{type(e).__name__}: {e}")
            counts[row["status"]] += 1
            report["cases"].append(row)
        report["suites"][suite] = {"required": required, **counts, "match_rate": counts["PASS"] / required}
    report["required"] = sum(required_counts[s] for s in chosen)
    report["passed"] = sum(s["PASS"] for s in report["suites"].values())
    report["all_passed"] = report["required"] > 0 and report["passed"] == report["required"]
    if output:
        dest = Path(output)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "answers.json").write_text(json.dumps({"environment": report["environment"], "actual": report["actual"]}, indent=2) + "\n", encoding="utf-8")
        (dest / "official-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def run(suites=None, output=None, source=None):
    from .validation256 import REQUIRED, run as run256
    legacy = {"Cip1", "Itg1", "Cip2", "Itg2", "Cip3", "Itg3"}
    if suites is not None and (not suites or len(set(suites)) != len(suites) or any(s not in legacy | REQUIRED.keys() for s in suites)):
        raise VectorError("Unknown or duplicate suite selection.")
    reports = []
    if suites is None or any(s in legacy for s in suites):
        reports.append(_legacy_run([s for s in suites if s in legacy] if suites else None, source=source))
    if suites is None or any(s in REQUIRED for s in suites):
        reports.append(run256([s for s in suites if s in REQUIRED] if suites else None,
                              source=Path(source) / '256' if source else None))
    report = dict(category='official', environment=identity(), suites={}, cases=[], actual={}, dataset_sha256={})
    for part in reports:
        report['suites'].update(part['suites'])
        report['cases'].extend(part['cases'])
        report['actual'].update(part['actual'])
        prefix = '256/' if part['category'] == 'official_256' else ''
        report['dataset_sha256'].update({prefix + k: v for k, v in part['dataset_sha256'].items()})
    report['required'] = sum(p['required'] for p in reports)
    report['passed'] = sum(p['passed'] for p in reports)
    report['all_passed'] = bool(reports) and all(p['all_passed'] for p in reports)
    if output:
        dest = Path(output)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / 'answers.json').write_text(json.dumps(dict(environment=report['environment'], actual=report['actual']), indent=2) + '\n')
        (dest / 'official-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    p = argparse.ArgumentParser(description="Developer official-vector validation")
    p.add_argument("--all", action="store_true")
    p.add_argument("--suite", action="append")
    p.add_argument("--output", default="validation/latest")
    args = p.parse_args()
    try:
        result = run(args.suite, args.output)
    except VectorError as e:
        print(str(e), file=sys.stderr)
        return 2
    print(json.dumps({"required": result["required"], "passed": result["passed"], "suites": result["suites"]}, indent=2))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
