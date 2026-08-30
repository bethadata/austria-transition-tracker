# -*- coding: utf-8 -*-
"""The eurostat full energy balance (nrg_bal_c), read out of the per-year cache.

`download/energy_balance.py` writes one JSON per year holding the whole
`siec` x `nrg_bal` matrix in TWh -- every fuel against every balance aggregate.
This reads a selection out of it: a mapping from the label you want to the
eurostat fuel names that make it up, and a list of balance aggregates to sum.

    energy_balance.read(
        bals=["Gross heat production"],
        siecs={"Natural gas": ["Natural gas"],
               "Biomass": ["Primary solid biofuels"]})

The nesting is what it is because eurostat's categories do not line up with the
categories a reader thinks in: "Biomass" on the gross-inland-consumption chart is
ten eurostat fuels, "Renewable electricity" is four.

Kept as its own module rather than folded into `sources/eurostat.py` because it
reads a different cache in a different format for a different reason -- the
monthly tables are one series at a time, this is a matrix per year.
"""

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

from paths import DATA_RAW

BALANCE_DIR = DATA_RAW + "/eurostat/energy_balances"


def year_path(year):
    return "%s/AT_%s_en_bal_TWh.json" % (BALANCE_DIR, year)


def years():
    """The years the cache holds, oldest first.

    Derived from what is on disk rather than from a range, because the newest
    balance year is exactly the thing that moves: eurostat publishes it about
    18 months late, and `download/energy_balance.py` has to be run by hand to
    pick it up.
    """
    if not os.path.isdir(BALANCE_DIR):
        raise FileNotFoundError(
            "%s is missing -- run `python -m download.energy_balance` to build it."
            % BALANCE_DIR)
    found = []
    for year in range(1990, 2101):
        if os.path.exists(year_path(year)):
            found.append(year)
    if not found:
        raise FileNotFoundError("no energy-balance years cached in %s" % BALANCE_DIR)
    return found


def read(siecs, bals):
    """{label: [eurostat fuels]} x [balance aggregates] -> a yearly data_plot.

    A fuel the balance does not report for a given year contributes 0 rather
    than a gap: these are additive components of a category, so an absent one
    means "none of that", and one nan would otherwise poison the whole category.
    That is the same rule `series.py` states for sums, applied at the read.
    """
    cached = years()
    # A hole in the cache would silently shift every year after it onto the
    # wrong x position, which reads as a revision to history rather than as a
    # missing download. Cheap to check, invisible if it is not checked.
    expected = list(range(cached[0], cached[-1] + 1))
    if cached != expected:
        raise FileNotFoundError(
            "energy-balance cache has gaps: missing %s"
            % ", ".join(str(y) for y in sorted(set(expected) - set(cached))))
    times = pd.date_range(start=datetime(cached[0], 1, 1),
                          end=datetime(cached[-1], 1, 1), freq="YS")

    data = {"data": {label: {"x": times, "y": np.zeros(len(times))} for label in siecs}}

    for t, year in enumerate(cached):
        with open(year_path(year), "r") as fp:
            balance = json.load(fp)
        for bal in bals:
            for label in siecs:
                for fuel in siecs[label]:
                    value = balance[fuel][bal]
                    if not np.isnan(value):
                        data["data"][label]["y"][t] += value
    return data
