"""Every path the pipeline reads or writes. Committed, and holds nothing machine-local.

BASEPATH is the repository root -- the folder holding both `services/` and the Vue app --
derived from this file's location so moving or renaming the checkout cannot silently
break the scrapers, the chart writers or `publish.py`.

This was `config.py` behind a git-ignored/template pair until 2026-08-21, back when
BASEPATH was a typed absolute path. Nothing here is per-machine any more, so the file is
tracked and there is no setup step. Keep it that way: `config.py` stays in `.gitignore`,
so a genuine secret or per-machine value goes *there*, never in this module.

`as_posix()` is load-bearing: callers string-concatenate (`DATA_RAW + "/eurostat/..."`),
so the values must be forward-slashed and must not end in a separator.

The derived constants below exist because the paths used to be re-typed at every read
site, at three different relative depths -- `"../data_raw/..."` from `plot/`,
`"../../data_raw/..."` from `plot/utils/`, `"../../../docs/..."` from a figure writer.
Two of those were already wrong: the methodology figures still wrote into `docs/`, the
Jekyll output tree that was deleted with the rest of it, so they had been failing
silently. A path that is spelled once cannot drift like that.
"""
from pathlib import Path

BASEPATH = Path(__file__).resolve().parents[1].as_posix()

#: Raw source data. `eurostat/` and `e_control/` are git-ignored and reproducible by
#: `scrape.py`; everything else is a manual download and is tracked, because git is the
#: only backup those files have.
DATA_RAW = BASEPATH + "/services/data_raw"

#: The frontend data contract: manifest.json plus one <chart-id>.json per chart.
PUBLIC_DATA = BASEPATH + "/public/data"

#: Static images the app serves, including the three methodology figures.
PUBLIC_IMAGES = BASEPATH + "/public/images"

#: Where `manifest.finalize()` writes the generated locale seed. Never imported by the
#: app -- the live files under src/locales/{de,en}/ are frontend-owned and carry
#: hand-written UI chrome that a generator would erase.
LOCALE_SEED = BASEPATH + "/src/locales/_seed"

#: The live locale directories, read by check_contract.py only.
LOCALES = BASEPATH + "/src/locales"
