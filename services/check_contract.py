"""Validate the manifest against the data files and the locale seed.

Run after create_charts.py. Every failure here is a class of bug that renders as
a blank or silently wrong chart rather than as an error: a chart with no data
file, a series named in the manifest but absent from the data, a chart id with
no title in the locale files. Cheap to check, invisible if it is not checked.
"""

import glob
import json
import os
import sys

from paths import BASEPATH

DATA_DIR = BASEPATH + "/public/data"
LOCALES = BASEPATH + "/src/locales"


def _load(path):
    with open(path, encoding="utf-8") as fp:
        return json.load(fp)


def check():
    problems = []
    manifest = _load(DATA_DIR + "/manifest.json")
    charts = manifest["charts"]
    ids = [c["id"] for c in charts]

    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        problems.append("duplicate chart ids: %s" % ", ".join(sorted(dupes)))

    on_disk = {os.path.basename(p)[:-5] for p in glob.glob(DATA_DIR + "/*.json")}
    on_disk.discard("manifest")
    missing = set(ids) - on_disk
    orphaned = on_disk - set(ids)
    if missing:
        problems.append("manifest entries with no data file: %s" % ", ".join(sorted(missing)))
    if orphaned:
        problems.append("data files with no manifest entry: %s" % ", ".join(sorted(orphaned)))

    for c in charts:
        if not c.get("page"):
            problems.append("%s: no page (add it to plot/pages.py)" % c["id"])
        if not c.get("series"):
            problems.append("%s: no series" % c["id"])
        if c["id"] not in on_disk:
            continue
        data = _load("%s/%s.json" % (DATA_DIR, c["id"]))
        if "groups" in data:
            if set(data["groups"]) != set(c.get("groups") or []):
                problems.append("%s: groups differ between manifest and data" % c["id"])
            blocks = list(data["groups"].values())
        else:
            blocks = [data]
        for b in blocks:
            for key in c["series"]:
                if key not in b["series"]:
                    problems.append("%s: series %r in manifest, absent from data"
                                    % (c["id"], key))
                elif len(b["series"][key]) != len(b["x"]):
                    problems.append("%s: series %r length %d != x length %d"
                                    % (c["id"], key, len(b["series"][key]), len(b["x"])))
            empty = [k for k, col in b["series"].items()
                     if all(v is None for v in col)]
            if empty:
                # All-null renders as an empty trace: a legend entry and no line.
                problems.append("%s: series with no data at all: %s"
                                % (c["id"], ", ".join(empty)))

    # Locale coverage. German is default *and* fallback, so a key missing from
    # en/ serves German to an English reader -- invisible to a typecheck.
    for locale in sorted(os.path.basename(p) for p in glob.glob(LOCALES + "/*")):
        base = "%s/%s" % (LOCALES, locale)
        # _seed is the pipeline's own output, not a locale the app loads.
        if not os.path.isdir(base) or locale.startswith("_"):
            continue
        try:
            titles = _load(base + "/charts.json")
            common = _load(base + "/common.json")
        except FileNotFoundError as exc:
            problems.append("%s: %s" % (locale, exc))
            continue
        for c in charts:
            if c["id"] not in titles:
                problems.append("%s/charts.json: no entry for %s" % (locale, c["id"]))
            for key in c["series"]:
                if key not in common.get("series", {}):
                    problems.append("%s/common.json: no series label %r (%s)"
                                    % (locale, key, c["id"]))
            if c.get("unit") and c["unit"] not in common.get("units", {}):
                problems.append("%s/common.json: no unit label %r (%s)"
                                % (locale, c["unit"], c["id"]))
    return charts, problems


def main():
    charts, problems = check()
    if problems:
        print("FAIL: %d problem(s) across %d charts" % (len(problems), len(charts)))
        for p in problems:
            print("  -", p)
        return 1
    print("OK: %d charts, manifest/data/locales consistent" % len(charts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
