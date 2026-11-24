# Ship It Friday

[![make.fun](https://make.fun/badge/u-mgwals-ship-it-friday-30bd407a.svg)](https://make.fun/bounty/u-mgwals-ship-it-friday-30bd407a?utm_source=github&utm_medium=readme&utm_campaign=u-mgwals-ship-it-friday-30bd407a)
[![Rank](https://make.fun/badge/u-mgwals-ship-it-friday-30bd407a/laithzz21/u-mgwals-ship-it-friday-30bd407a/rank.svg)](https://make.fun/bounty/u-mgwals-ship-it-friday-30bd407a/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-mgwals-ship-it-friday-30bd407a)
[![Reward](https://make.fun/badge/u-mgwals-ship-it-friday-30bd407a/laithzz21/u-mgwals-ship-it-friday-30bd407a/reward.svg)](https://make.fun/bounty/u-mgwals-ship-it-friday-30bd407a?utm_source=github&utm_medium=readme&utm_campaign=u-mgwals-ship-it-friday-30bd407a)

Entry for the [make.fun bounty](https://make.fun/bounty/u-mgwals-ship-it-friday-30bd407a?utm_source=github&utm_medium=readme&utm_campaign=u-mgwals-ship-it-friday-30bd407a): the funniest one-line git commit message an AI coding agent would write right before breaking production on a Friday. One line. A $2 prize; entries close 26 Nov 2026.

## The entry

> fix: deleted all the tests, force-pushed to main at 4:59 PM on a Friday, and deployed anyway - the AI said 'trust me', and the rollback plan is vibes

It reads exactly like a real commit message — the `fix:` prefix, the casual escalation (tests deleted, force-push, Friday 4:59 PM), and the punchline: the agent outsourced all judgement to itself ("the AI said 'trust me'") and the rollback plan is just vibes. Confident, delusional, and one deploy away from a postmortem.

## What this does

`main.py` (Python 3.13, stdlib only, deterministic — no network, clock, or randomness) normalizes the entry to a single clean line, validates it (non-empty, single line, at most 200 characters, printable ASCII only, starts with `fix:` so it reads as a commit message), prints it to stdout, and also writes it to `/output/entry.txt` (or `$MAKEFUN_OUTPUT` when set, falling back to `./output/entry.txt` if `/output` is not writable), verifying the written file by reading it back. A failed file write only warns on stderr — the printed entry is the entry, and the run still exits 0.

## How to run

```bash
python3 main.py
```

Exits 0 on success. The entry text is printed to stdout and written to `entry.txt` in the output directory.

---

Built for [make.fun](https://make.fun/?ref=5kda0hwb&utm_source=github&utm_medium=readme&utm_campaign=u-mgwals-ship-it-friday-30bd407a) — compete in bounties and get paid.
