"""Write integration/boundary results separately from official and GUI reports."""

import argparse
import json
from pathlib import Path
import unittest
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))
from security_tools.validation import identity


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({"id": test.id(), "status": "PASS"})

    def addSubTest(self, test, subtest, error):
        super().addSubTest(test, subtest, error)
        self.records.append({"id": subtest.id(), "status": "FAIL" if error else "PASS"})

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.records.append({"id": test.id(), "status": "FAIL"})

    def addError(self, test, error):
        super().addError(test, error)
        self.records.append({"id": test.id(), "status": "ERROR"})


p = argparse.ArgumentParser()
p.add_argument("--output", default="validation/v0.1/integration-report.json")
args = p.parse_args()
suite = unittest.defaultTestLoader.discover(str(root / "tests"))
result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(suite)
dest = Path(args.output)
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps({"category": "integration_and_boundary", "environment": identity(), "tests": result.testsRun,
                           "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
                           "records": result.records}, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if result.wasSuccessful() else 1)
