"""Repository paths for the data pipeline. Committed, and holds nothing machine-local.

BASEPATH is the repository root -- the folder holding both `services/` and `docs/` --
derived from this file's location so moving or renaming the checkout cannot silently
break the scrapers, the chart writers or `publish_github.py`.

This was `config.py` behind a git-ignored/template pair until 2026-08-21, back when
BASEPATH was a typed absolute path. Nothing here is per-machine any more, so the file is
tracked and there is no setup step. Keep it that way: `config.py` stays in `.gitignore`,
so a genuine secret or per-machine value goes *there*, never in this module.

`as_posix()` is load-bearing: callers string-concatenate (`BASEPATH + "/docs/..."`), so
the value must be forward-slashed and must not end in a separator.
"""
from pathlib import Path

BASEPATH = Path(__file__).resolve().parents[1].as_posix()
