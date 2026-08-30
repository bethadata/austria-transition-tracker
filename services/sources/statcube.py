# -*- coding: utf-8 -*-
"""StatCube (Statistik Austria) food-balance exports: meat and milk consumption.

Manual CSV exports from StatCube, whose filenames carry the export date. The
newest export for each product wins, matched by prefix -- the date used to be
typed into the reader, so re-exporting meant editing Python, and the older
export sat next to the newer one on disk with nothing saying which was live.

Both products are the same read: pick the rows for a product and a measure
("Werte"), sort the years, divide by a unit factor. Meat additionally gets an
"Other" residual against its own total; milk has no total row to subtract from,
which is the only real difference between them and is why `total` is a
parameter rather than two functions.
"""

import glob
import os
from datetime import datetime

import numpy as np
import pandas as pd

from paths import DATA_RAW

import series as S

STATCUBE_DIR = DATA_RAW + "/statistik_austria"

#: Product label -> the German value in StatCube's "Produkte" column. Order is
#: palette order; the total, where there is one, is named separately.
MEAT_TYPES = {
    "Total": "Fleisch insgesamt",
    "Chicken / Poultry": "Geflügelfleisch",
    "Pigmeat": "Schweinefleisch",
    "Cows / cattle": "Rind- und Kalbfleisch",
}

MILK_TYPES = {
    "Milk": "Konsummilch",
    "Cheese": "Käse",
    "Butter": "Butter",
    "Cream": "Obers und Rahm",
}


def _newest(prefix):
    """The most recent StatCube export matching a prefix.

    Sorted by the date in the filename, which StatCube writes as ISO, so a
    lexical sort is a chronological one.
    """
    matches = sorted(glob.glob("%s/%s*.csv" % (STATCUBE_DIR, prefix)))
    if not matches:
        raise FileNotFoundError(
            "no StatCube export matching %s*.csv in %s -- it is a manual download."
            % (prefix, STATCUBE_DIR))
    return matches[-1]


def _read(path):
    with open(path, "r") as fp:
        return pd.read_csv(fp, skiprows=6, encoding="cp1252", on_bad_lines="skip",
                           sep=";", skipfooter=1, engine="python", decimal=",")


def _consumption(path, types, measure, factor, total=None):
    table = _read(path)

    # dropna: the export carries blank rows between product blocks, so the year
    # column is not dense.
    years = sorted({int(y) for y in table["Jahr"].dropna()})
    times = pd.date_range(start=datetime(years[0], 1, 1),
                          end=datetime(years[-1], 1, 1), freq="YS")

    out = []
    for label, german in types.items():
        rows = table[np.logical_and(table["Produkte"] == german,
                                    table["Werte"] == measure)]
        values = [float(rows[rows["Jahr"] == t.year]["Anzahl"].iloc[0]) for t in times]
        out.append((label, S.series(times, np.array(values) / factor)))

    data = S.wrap(out)
    if total is not None:
        # "Other" is what the named products do not account for. The residual
        # rather than a category, because StatCube reports a total and four
        # products and nothing in between.
        data = S.residual(data, "Other", of=total)
    return data


def meat_consumption(measure="Menschlicher Verzehr", factor=1):
    return _consumption(_newest("meat_consumption_StatCube_table_"),
                        MEAT_TYPES, measure, factor, total="Total")


def milk_consumption(measure="NAHRUNGSVERBRAUCH", factor=1):
    return _consumption(_newest("milk-consumption_StatCube_table_"),
                        MILK_TYPES, measure, factor)
