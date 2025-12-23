#!/usr/bin/env python3
"""Create a venv and install project dependencies.

Usage:
  python install.py
  python install.py --venv .venv --requirements requirements.txt --upgrade-pip

This script is intentionally simple: it creates a virtual environment (by
default `.venv`), and installs the packages from `requirements.txt` into it.
If you prefer not to use a venv, pass `--no-venv` to install into the current
Python environment (not recommended).
"""
import argparse
import os
import shutil
import subprocess
import sys


def run(cmd, **kwargs):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, **kwargs)


def main():
    p = argparse.ArgumentParser(description="Create venv and install requirements")
    p.add_argument("--venv", default=".venv", help="venv directory name (default '.venv')")
    p.add_argument("--requirements", default="requirements.txt", help="requirements file")
    p.add_argument("--no-venv", action="store_true", help="Install into current Python environment")
    p.add_argument("--upgrade-pip", action="store_true", help="Upgrade pip in the created venv")
    args = p.parse_args()

    req = args.requirements
    if not os.path.exists(req):
        print(f"Warning: requirements file '{req}' not found. Skipping pip install.")

    if args.no_venv:
        print("Installing into current Python environment")
        if os.path.exists(req):
            run([sys.executable, "-m", "pip", "install", "-r", req])
        return

    # create venv
    venv_dir = os.path.abspath(args.venv)
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment at {venv_dir}")
        run([sys.executable, "-m", "venv", venv_dir])
    else:
        print(f"Virtual environment already exists at {venv_dir}")

    pip_bin = os.path.join(venv_dir, "bin", "pip")
    py_bin = os.path.join(venv_dir, "bin", "python")

    if args.upgrade_pip:
        run([py_bin, "-m", "pip", "install", "--upgrade", "pip"]) 

    if os.path.exists(req):
        run([pip_bin, "install", "-r", req])
    else:
        print("No requirements installed.")

    print("Install complete. To activate the venv: `source .venv/bin/activate`")


if __name__ == "__main__":
    main()
