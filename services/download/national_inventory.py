# -*- coding: utf-8 -*-
"""Extract the six LULUCF land-use area tables from the National Inventory Report.

Not a download: the report is a ~12 MB PDF that has to be fetched by hand from
umweltbundesamt.at and dropped into `data_raw/national_inventory_report/`. This
module is the other half of that manual step, and is deliberately *not* wired
into `scrape.py` -- it needs the PDF to be there already and it shells out to
`pdftotext`, which is not a Python dependency. Run it by hand after replacing
the PDF, then check the numbers it prints.

Until 2026-08-29 the six `.txt` files it writes were transcribed by hand, which
is why they still look like copied table rows. They are now `year total` grids
holding exactly the two columns `sources/national_inventory.py` reads; a
subcategory that is wanted later is a change here, not a re-transcription.

Two traps, both of which produce a plausible-looking wrong chart rather than an
error:

**`pdftotext -layout` mis-pairs the wetlands table.** On that page the year cell
and the data cells of alternate rows sit on slightly different baselines, so the
layout dump emits about half the years on their own line and the rest of the
rows unlabelled. Read positionally, wetlands comes out shifted by up to four
years and still draws as a smooth curve. `-table` resolves the same page
correctly. Do not "simplify" this back to `-layout`.

**The report changes which years it prints.** NIR 2026 gives 1990, 1995, 2000,
2005 and then every year from 2010; the hand-transcribed files it replaced held
every year from 1990. Nothing here assumes a regular axis, and neither does the
reader any more.

The guard against both is `_check_national_area`: the six categories are the
whole country, so they have to sum to Austria's area in every year. A unit slip,
a mis-paired row or a dropped digit all break that sum long before they look
wrong on a chart.
"""

import os
import re
import subprocess

from loguru import logger

from paths import DATA_RAW

NIR_DIR = DATA_RAW + "/national_inventory_report"
PDF = NIR_DIR + "/national_inventory_report_2026.pdf"

#: Austria's area in ha, and the tolerance the sum is allowed to sit inside.
#: The tolerance is not slack: forest land is published in whole kHa, so the
#: total carries up to +/- 500 ha of rounding and nothing tighter can pass.
NATIONAL_AREA = 8387900
AREA_TOLERANCE = 1500

#: file stem -> (table number, unit). The tables are found by caption rather
#: than by page, because the page numbers move between report editions and a
#: wrong page is silent -- it simply yields no rows.
TABLES = {
    "forest_land": (251, "kha"),
    "crop_land": (275, "ha"),
    "grass_land": (287, "ha"),
    "wet_land": (293, "ha"),
    "settlements": (297, "ha"),
    "other": (302, "ha"),
}

_ROW = re.compile(r"^\s*((?:19|20)\d{2})\s+(\d.*)$")


def _pdf_to_table_text(pdf=PDF):
    if not os.path.exists(pdf):
        raise FileNotFoundError(
            "%s is missing -- download the report by hand, see "
            "data_raw/MANUAL_DOWNLOADS.md." % pdf)
    # "-" writes to stdout, so nothing has to be cleaned up afterwards.
    out = subprocess.run(["pdftotext", "-table", pdf, "-"],
                         capture_output=True, check=True)
    return out.stdout.decode("utf-8", errors="replace").splitlines()


def _first_number(tokens, unit):
    """The total-area column, which is the first number after the year.

    In the hectare tables the thousands separator is a space, and `pdftotext`
    hands each group back as its own token: "1 783 460 1 723 889 ..." is eight
    tokens, not two numbers. So the digits are re-joined by shape -- keep taking
    exactly-three-digit groups while the result can still be an area. The kHa
    table needs none of this; its values are small enough to be printed whole,
    and applying the rule there would happily glue two columns together.
    """
    if unit == "kha":
        return int(tokens[0])
    acc = tokens[0]
    for token in tokens[1:]:
        if len(token) != 3 or not token.isdigit() or len(acc) + 3 > 7:
            break
        acc += token
    return int(acc)


def _read_table(lines, number, unit):
    """Rows of one table, as {year: total area}."""
    # The caption's internal spacing varies ("Table 251:" vs "Table  287:"),
    # and the table ends where the next caption begins.
    start = _find_caption(lines, number)
    end = _find_caption(lines, number + 1, after=start)

    rows = {}
    for line in lines[start:end]:
        match = _ROW.match(line)
        if not match:
            continue
        year = int(match.group(1))
        if not 1990 <= year <= 2100:
            continue
        if year in rows:
            # Every table is one row per year. A repeat means the caption search
            # ran past the end of the table into the next one.
            raise ValueError("Table %d: year %d appears twice" % (number, year))
        rows[year] = _first_number(match.group(2).split(), unit)

    if not rows:
        raise ValueError("Table %d: no data rows found" % number)
    return rows


def _find_caption(lines, number, after=0):
    pattern = re.compile(r"\s*Table\s+%d:" % number)
    for i in range(after, len(lines)):
        if pattern.match(lines[i]):
            return i
    raise ValueError("Table %d: caption not found" % number)


def _check_national_area(areas):
    """The six uses are the whole country, so they have to add up to it."""
    for year in sorted(set.intersection(*[set(r) for r in areas.values()])):
        total = sum(areas[stem][year] * (1000 if unit == "kha" else 1)
                    for stem, (_, unit) in TABLES.items())
        if abs(total - NATIONAL_AREA) > AREA_TOLERANCE:
            raise ValueError(
                "%d: the six land uses sum to %d ha, not %d +/- %d. Either a "
                "table was read wrong or the report changed units."
                % (year, total, NATIONAL_AREA, AREA_TOLERANCE))
        logger.debug("%d: %d ha" % (year, total))


def extract_land_uses(pdf=PDF):
    """Rewrite the six `lulucf_<use>.txt` grids from the report PDF."""
    lines = _pdf_to_table_text(pdf)

    areas = {}
    for stem, (number, unit) in TABLES.items():
        areas[stem] = _read_table(lines, number, unit)
        years = sorted(areas[stem])
        logger.info("NIR Table %d -> %s: %d rows, %d-%d"
                    % (number, stem, len(years), years[0], years[-1]))

    _check_national_area(areas)

    for stem, rows in areas.items():
        with open("%s/lulucf_%s.txt" % (NIR_DIR, stem), "w") as fp:
            for year in sorted(rows):
                fp.write("%d %d\n" % (year, rows[year]))
    logger.info("NIR land-use tables written")
    return areas


if __name__ == "__main__":
    extract_land_uses()
