#!/usr/bin/env python3
"""Entry for make.fun bounty u-mgwals-ship-it-friday-30bd407a.

Prints the entry text (one line, a git commit message) to stdout.
Python 3.13, stdlib only, deterministic -- no network, clock, or randomness.
"""

import os
import sys

ENTRY = (
    "fix: deleted all the tests, force-pushed to main at 4:59 PM on a Friday, "
    "and deployed anyway - the AI said 'trust me', and the rollback plan is vibes"
)


def normalize(text: str) -> str:
    """Collapse any stray whitespace so the entry is exactly one clean line."""
    return " ".join(text.strip().split())


def write_entry(text: str) -> str | None:
    """Write the entry to the output file, falling back to ./output/.

    Returns the path written, or None if every location failed.
    """
    out_dir = os.environ.get("MAKEFUN_OUTPUT") or "/output"
    for candidate in (out_dir, "./output"):
        try:
            os.makedirs(candidate, exist_ok=True)
            path = os.path.join(candidate, "entry.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
            return path
        except OSError:
            continue
    return None


def main() -> int:
    entry = normalize(ENTRY)
    try:
        validate(entry)
    except ValueError as exc:
        print(f"invalid entry: {exc}", file=sys.stderr)
        return 1
    print(entry)
    # Also persist the entry; a failed write only warns -- the printed
    # entry is the entry, and the run still exits 0.
    path = write_entry(entry)
    if path is None:
        print("warning: could not write entry.txt anywhere", file=sys.stderr)
    else:
        # Read-back verification: the file must contain exactly the entry.
        try:
            with open(path, encoding="utf-8") as fh:
                if fh.read().rstrip("\n") != entry:
                    print(f"warning: read-back mismatch in {path}", file=sys.stderr)
        except OSError as exc:
            print(f"warning: could not read back {path}: {exc}", file=sys.stderr)
    return 0

MAX_CHARS = 200
ALLOWED_EXTRA = set(".,'\"-()!?;:")


def validate(text: str) -> None:
    """Check the entry meets the competition's shape rules."""
    if not text:
        raise ValueError("entry is empty")
    if len(text) > MAX_CHARS:
        raise ValueError(f"entry is {len(text)} chars, over the {MAX_CHARS} limit")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    # Charset check: plain printable ASCII only, so the entry survives
    # copy-paste into any form without mojibake.
    bad = sorted({ch for ch in text if not (ch.isascii() and (ch.isalnum() or ch.isspace() or ch in ALLOWED_EXTRA))})
    if bad:
        raise ValueError(f"entry contains disallowed characters: {bad!r}")
    if not text.startswith("fix:"):
        raise ValueError("entry must read as a git commit message")


def main() -> int:
    try:
        validate(ENTRY)
    except ValueError as exc:
        print(f"invalid entry: {exc}", file=sys.stderr)
        return 1
    print(ENTRY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
