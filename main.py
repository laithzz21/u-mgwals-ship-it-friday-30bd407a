#!/usr/bin/env python3
"""Entry for make.fun bounty u-mgwals-ship-it-friday-30bd407a.

Prints the entry text to stdout: a single-line git commit message that
captures the "Ship It Friday" spirit -- deleting the tests, force-pushing
to main at 4:59 PM on a Friday, and deploying anyway because the AI said
"trust me", with a rollback plan made entirely of vibes.

Behaviour
---------
* The entry is validated before anything is printed: it must be one line,
  at most 200 characters, start with a conventional-commit prefix, use
  only printable ASCII, and contain every element the competition asks
  for (the deleted tests, the force-push, the Friday 4:59 PM timestamp,
  the deploy, the AI's reassurance, and the vibes-based rollback plan).
* The validated entry is printed to stdout, exactly one line.
* The entry is also persisted as ``entry.txt`` in a structured output
  directory, with a read-back check. If the preferred output location
  is unavailable, a fallback directory is used; if every location fails,
  a warning goes to stderr and the run still exits 0, because the
  printed line -- not the file -- is the entry.

Python 3.13, standard library only. Deterministic: no network, no clock,
no randomness, so repeated runs produce byte-identical output.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# The entry itself.
#
# Exactly 149 characters, one line. This string is the submission: it must
# never be edited, re-wrapped, or reworded -- the validation below exists
# to catch any accidental drift before the entry is printed.
# ---------------------------------------------------------------------------
ENTRY = (
    "fix: deleted all the tests, force-pushed to main at 4:59 PM on a Friday, "
    "and deployed anyway - the AI said 'trust me', and the rollback plan is vibes"
)

# Conventional-commit prefixes the entry may start with. The entry uses
# "fix:" because deleting the tests and deploying anyway is, charitably,
# presented as a fix.
CONVENTIONAL_PREFIXES = (
    "feat:",
    "fix:",
    "docs:",
    "style:",
    "refactor:",
    "test:",
    "chore:",
    "build:",
    "ci:",
    "revert:",
)

# Every element the competition's prompt requires the message to contain.
# Checked case-insensitively so a capitalisation tweak would not hide a
# missing element, but the printed text itself is never altered.
REQUIRED_ELEMENTS = (
    "deleted all the tests",
    "force-pushed",
    "4:59 PM",
    "Friday",
    "deployed",
    "trust me",
    "rollback plan",
    "vibes",
)

# Characters allowed beyond letters, digits, and whitespace. Kept narrow
# on purpose: the entry has to survive copy-paste into any form, chat
# window, or terminal without mojibake.
ALLOWED_PUNCTUATION = set(".,'\"-()!?;:")

# Output locations, tried in order. The first writable one wins; the
# second is the fallback path used when the sandbox has no /output.
OUTPUT_CANDIDATES = ("/output", "./output")
OUTPUT_FILENAME = "entry.txt"


@dataclass(frozen=True)
class EntryRules:
    """The shape rules an entry must satisfy before it may be printed."""

    max_chars: int = 200
    prefixes: tuple[str, ...] = CONVENTIONAL_PREFIXES
    required_elements: tuple[str, ...] = REQUIRED_ELEMENTS
    allowed_punctuation: frozenset[str] = field(
        default_factory=lambda: frozenset(ALLOWED_PUNCTUATION)
    )

    def check_single_line(self, text: str) -> list[str]:
        """The entry must be exactly one line -- no newlines at all."""
        problems: list[str] = []
        if "\n" in text or "\r" in text:
            problems.append("entry must be a single line")
        if text != text.strip():
            problems.append("entry has leading or trailing whitespace")
        return problems

    def check_length(self, text: str) -> list[str]:
        """The competition caps the message at 200 characters."""
        if len(text) > self.max_chars:
            return [
                f"entry is {len(text)} chars, over the {self.max_chars} limit"
            ]
        if not text:
            return ["entry is empty"]
        return []

    def check_prefix(self, text: str) -> list[str]:
        """It must read as a git commit message, so it needs a prefix."""
        if not any(text.startswith(prefix) for prefix in self.prefixes):
            return [
                "entry must start with a conventional-commit prefix "
                f"(one of {', '.join(self.prefixes)})"
            ]
        return []

    def check_charset(self, text: str) -> list[str]:
        """Plain printable ASCII only, so the entry survives any form."""
        bad = sorted(
            {
                ch
                for ch in text
                if not (
                    ch.isascii()
                    and (ch.isalnum() or ch.isspace() or ch in self.allowed_punctuation)
                )
            }
        )
        if bad:
            return [f"entry contains disallowed characters: {bad!r}"]
        return []

    def check_required_elements(self, text: str) -> list[str]:
        """Every element from the brief must actually appear in the text."""
        lowered = text.lower()
        missing = [el for el in self.required_elements if el.lower() not in lowered]
        if missing:
            return [f"entry is missing required elements: {missing!r}"]
        return []

    def check_weekday(self, text: str) -> list[str]:
        """The deploy has to happen on a weekday -- and the brief says
        Friday, the day the whole joke hinges on. A message with no
        weekday in it at all is not a Ship It Friday entry."""
        weekdays = (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        )
        lowered = text.lower()
        if not any(day in lowered for day in weekdays):
            return ["entry names no day of the week"]
        if "friday" not in lowered:
            return ["entry is not a Friday deploy"]
        return []

    def validate(self, text: str) -> list[str]:
        """Run every rule and collect all problems, so one bad entry
        reports everything wrong with it instead of only the first fault."""
        problems: list[str] = []
        for check in (
            self.check_single_line,
            self.check_length,
            self.check_prefix,
            self.check_charset,
            self.check_required_elements,
            self.check_weekday,
        ):
            problems.extend(check(text))
        return problems


def normalize(text: str) -> str:
    """Collapse any stray internal whitespace to single spaces.

    The entry is already clean, so this is a no-op in practice -- it is
    here as a safety net so a future edit that introduces a double space
    or a tab still prints as one tidy line.
    """
    return " ".join(text.strip().split())


def looks_like_time_of_day(text: str) -> bool:
    """Sanity check that the entry names a plausible clock time.

    The joke only lands if the deploy happens late on a Friday afternoon,
    so the "4:59 PM" timestamp is worth confirming structurally: an hour
    of 1-12, minutes of 00-59, and an AM/PM marker.
    """
    match = re.search(r"(\d{1,2}):(\d{2})\s*([AP]M)", text)
    if match is None:
        return False
    hour, minute = int(match.group(1)), int(match.group(2))
    return 1 <= hour <= 12 and 0 <= minute <= 59


@dataclass
class OutputResult:
    """The outcome of persisting the entry to disk."""

    path: str | None
    written: bool
    verified: bool
    error: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "written": self.written,
            "verified": self.verified,
            "error": self.error,
        }


def candidate_output_dirs() -> list[str]:
    """Output directories in preference order.

    ``MAKEFUN_OUTPUT`` lets a harness redirect the file; otherwise the
    standard ``/output`` location is tried first, with ``./output`` as
    the fallback when the sandbox has no writable root directory.
    """
    preferred = os.environ.get("MAKEFUN_OUTPUT")
    dirs = [preferred] if preferred else []
    dirs.extend(OUTPUT_CANDIDATES)
    # Deduplicate while keeping the preference order intact.
    seen: set[str] = set()
    unique: list[str] = []
    for directory in dirs:
        if directory and directory not in seen:
            seen.add(directory)
            unique.append(directory)
    return unique


def write_entry(text: str) -> OutputResult:
    """Persist the entry as ``entry.txt`` and verify it by reading it back.

    Tries each candidate directory in turn and returns the first success.
    A read-back mismatch is treated as a failure of that location, so the
    next candidate is tried instead of trusting a corrupt write. If every
    candidate fails, the system temp directory is tried as a last resort
    so the entry is still persisted somewhere instead of being lost.
    """
    last_error: str | None = None
    for directory in candidate_output_dirs():
        path = os.path.join(directory, OUTPUT_FILENAME)
        try:
            os.makedirs(directory, exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text + "\n")
            with open(path, encoding="utf-8") as handle:
                stored = handle.read().rstrip("\n")
            if stored != text:
                last_error = f"read-back mismatch in {path}"
                continue
            return OutputResult(path=path, written=True, verified=True)
        except OSError as exc:
            last_error = f"{path}: {exc}"
            continue
    # Last resort: the system temp directory. It is not a proper output
    # location, but a copy there beats no copy at all, and the run's
    # stdout already carries the entry either way.
    fallback_dir = os.path.join(tempfile.gettempdir(), "ship-it-friday-entry")
    path = os.path.join(fallback_dir, OUTPUT_FILENAME)
    try:
        os.makedirs(fallback_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
        with open(path, encoding="utf-8") as handle:
            if handle.read().rstrip("\n") == text:
                return OutputResult(path=path, written=True, verified=True)
        last_error = f"read-back mismatch in {path}"
    except OSError as exc:
        last_error = f"{path}: {exc}"
    return OutputResult(path=None, written=False, verified=False, error=last_error)


def build_report(entry: str, output: OutputResult) -> dict[str, object]:
    """A small structured summary of the run, for stderr diagnostics.

    Kept out of stdout on purpose: stdout carries exactly one line, the
    entry itself. Anything else would corrupt the submission.
    """
    return {
        "entry_chars": len(entry),
        "entry_lines": entry.count("\n") + 1,
        "mentions_time": looks_like_time_of_day(entry),
        "output": output.as_dict(),
    }


def main() -> int:
    rules = EntryRules()
    entry = normalize(ENTRY)

    problems = rules.validate(entry)
    if problems:
        for problem in problems:
            print(f"invalid entry: {problem}", file=sys.stderr)
        return 1

    # The entry itself -- and nothing else -- goes to stdout.
    print(entry)

    # Persist a copy with a fallback path, then report the outcome on
    # stderr only. A failed write is a warning, never a fatal error:
    # the printed line is the entry, and the run still exits 0.
    output = write_entry(entry)
    if not output.written:
        print(
            f"warning: could not write {OUTPUT_FILENAME} anywhere"
            + (f" ({output.error})" if output.error else ""),
            file=sys.stderr,
        )
    report = build_report(entry, output)
    print(f"report: {json.dumps(report, sort_keys=True)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
