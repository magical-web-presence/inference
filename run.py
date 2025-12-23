#!/usr/bin/env python3
"""Run the project using the virtualenv's python if present, else system python.

Usage:
  python run.py [--venv .venv] [--] [args...]

This will execute `src/main.py` with any extra arguments forwarded.
"""
import argparse
import os
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--venv", default=".venv", help="venv directory to use")
    p.add_argument("--", dest="--", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    args, rest = p.parse_known_args()

    venv_py = os.path.join(args.venv, "bin", "python")
    if os.path.exists(venv_py):
        python_exec = venv_py
        print(f"Using venv python: {python_exec}")
    else:
        python_exec = sys.executable
        print(f"Using system/python: {python_exec}")

    main_script = os.path.join(os.path.dirname(__file__), "src", "main.py")
    if not os.path.exists(main_script):
        # project layout may have src/ at repo root; try that
        main_script = os.path.join(os.getcwd(), "src", "main.py")

    if not os.path.exists(main_script):
        print("Error: could not find 'src/main.py' to run.", file=sys.stderr)
        sys.exit(2)

    cmd = [python_exec, main_script] + rest
    print("Running:", " ".join(cmd))
    rc = subprocess.call(cmd)
    sys.exit(rc)


if __name__ == "__main__":
    main()
