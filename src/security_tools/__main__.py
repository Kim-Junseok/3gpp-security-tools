import argparse


def main():
    parser = argparse.ArgumentParser(description="3GPP Security Tools")
    parser.add_argument("--validate", action="store_true", help="Run the packaged official vector suite")
    parser.add_argument("--suite", action="append")
    parser.add_argument("--output", default="validation")
    parser.add_argument("--gui-smoke-report")
    args = parser.parse_args()
    if args.validate:
        from .validation import run
        return 0 if run(args.suite, args.output)["all_passed"] else 1
    if args.gui_smoke_report:
        from .gui_smoke import run
        return run(args.gui_smoke_report)
    from .gui import main as gui_main
    gui_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
