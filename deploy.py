#!/usr/bin/env python3
"""Simple deploy helper: rsync the project to a remote desktop folder.

Usage examples (fish shell):
  python deploy.py
  python deploy.py --remote macuser@192.168.1.151 --dest ~/Desktop/inference
  python deploy.py --dry-run

Environment variables (optional):
  RSYNC_REMOTE  - remote user@host (overrides --remote)
  RSYNC_DEST    - remote destination path (overrides --dest)
"""
import argparse
import os
import shutil
import subprocess
import sys


def find_rsync() -> str:
    path = shutil.which("rsync")
    if not path:
        print("Error: rsync is not installed or not in PATH.", file=sys.stderr)
        sys.exit(2)
    return path


def build_rsync_cmd(rsync_path: str, excludes, dry_run: bool, verbose: bool, extra_args):
    cmd = [rsync_path, "-avz"]
    if dry_run:
        cmd.append("--dry-run")
    if not verbose:
        # keep -a, but reduce output if user wants quieter runs
        pass
    cmd.append("--delete")
    for ex in excludes:
        cmd.extend(["--exclude", ex])
    if extra_args:
        cmd.extend(extra_args)
    # source (current dir) and destination appended by caller
    return cmd


def main():
    p = argparse.ArgumentParser(description="Rsync project to remote Desktop/inference")
    p.add_argument("--remote", default=os.environ.get("RSYNC_REMOTE", "macuser@192.168.1.151"), help="remote user@host (default from env or macuser@192.168.1.151)")
    p.add_argument("--dest", default=os.environ.get("RSYNC_DEST", "~/Desktop/inference"), help="remote destination path (default ~/Desktop/inference)")
    p.add_argument("--exclude", action="append", default=[], help="additional exclude patterns (can be repeated)")
    p.add_argument("--dry-run", action="store_true", help="Show what would be copied")
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    p.add_argument("--extra-arg", action="append", default=[], help="Extra rsync args")

    args = p.parse_args()

    rsync_path = find_rsync()

    # sensible defaults to avoid sending heavy model files or venv
    default_excludes = [
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "*.pyc",
        "*.pyo",
    ]
    excludes = default_excludes + args.exclude

    cmd = build_rsync_cmd(rsync_path, excludes, args.dry_run, args.verbose, args.extra_arg)

    src = os.path.join(os.getcwd(), "./")
    # expand ~ on remote destination
    dest = f"{args.remote}:{args.dest.rstrip('/')}/"

    cmd.append(src)
    cmd.append(dest)

    print("Running:", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"rsync failed (exit {e.returncode})", file=sys.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
