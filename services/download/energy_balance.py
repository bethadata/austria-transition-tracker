# -*- coding: utf-8 -*-
"""Download the eurostat full energy balance, one JSON per year.

    python -m download.energy_balance          # any years not cached yet
    python -m download.energy_balance 2025     # one specific year

**An annual manual step, not part of `scrape.py`.** It walks the whole nrg_bal_c
cube fuel by fuel -- roughly eighty requests per year -- and eurostat publishes a
new balance year about every eighteen months, so running it daily would be a lot
of traffic for nothing. `sources/energy_balance.py` reads what it writes and
raises with this command in the message when a year is missing.

The output is one JSON per year holding the whole `siec` x `nrg_bal` matrix in
TWh, which is what makes the ten balance-derived charts cheap to rebuild: the
chart modules pick fuels and aggregates out of an already-local matrix instead of
re-querying eurostat for each combination.

The previous version of this script was not callable at all: it did its work at
import time, with the year range overwritten by a literal `years = [2024]` on the
next line, and wrote to a path relative to the current working directory, so it
only worked when run from inside `services/source/`.
"""

import json
import os
import sys

import eurostat
from loguru import logger

from paths import DATA_RAW

CODE = "NRG_BAL_C"
BALANCE_DIR = DATA_RAW + "/eurostat/energy_balances"

#: The balance is reported in terajoules; the charts are in TWh.
_TJ_TO_TWH = 3600

#: First year the cache covers. Not a download parameter -- the earliest year
#: eurostat has for Austria -- but the floor for "which years are missing".
FIRST_YEAR = 1990


def year_path(year):
    return "%s/AT_%i_en_bal_TWh.json" % (BALANCE_DIR, year)


def missing_years(through=None):
    """Cached years' gaps, plus the next one or two that might exist upstream."""
    if through is None:
        # eurostat is roughly 18 months behind, so asking two years past the
        # newest cached one is enough and costs one empty request if it is not
        # published yet.
        cached = [y for y in range(FIRST_YEAR, 2101) if os.path.exists(year_path(y))]
        through = (max(cached) if cached else FIRST_YEAR) + 2
    return [y for y in range(FIRST_YEAR, through + 1)
            if not os.path.exists(year_path(y))]


def download_year(year):
    """Write one year's balance matrix. Returns False if eurostat has no data."""
    fuels = eurostat.get_dic(CODE, "siec", full=False, frmt="dict")
    aggregates = eurostat.get_dic(CODE, "nrg_bal", full=False, frmt="dict")

    # A fresh dict per year. The old code reused one via a *shallow* copy, so
    # every year shared the same inner dicts -- harmless while it only ever ran
    # for one year, and silent corruption the moment anyone passed a range.
    matrix = {fuels[code]: {} for code in fuels}

    found = False
    for code in fuels:
        data = eurostat.get_data_df(CODE, filter_pars={"geo": "AT",
                                                       "siec": code,
                                                       "startPeriod": year,
                                                       "endPeriod": year + 1})
        if data is None:
            continue
        data = data[data["unit"] == "TJ"]
        if len(data) == 0:
            continue
        found = True
        reported = list(data["nrg_bal"])
        for aggregate in aggregates:
            if aggregate in reported:
                value = float(data[str(year)][data["nrg_bal"] == aggregate].iloc[0])
                matrix[fuels[code]][aggregates[aggregate]] = value / _TJ_TO_TWH
            else:
                # 0, not a gap: an aggregate a fuel does not appear under means
                # none of that fuel went there. sources/energy_balance.py sums
                # these into categories, where a gap would poison the category.
                matrix[fuels[code]][aggregates[aggregate]] = 0

    if not found:
        logger.info("eurostat has no energy balance for %i yet" % year)
        return False

    os.makedirs(BALANCE_DIR, exist_ok=True)
    with open(year_path(year), "w") as fp:
        json.dump(matrix, fp, indent=6)
    logger.info("Wrote energy balance %i" % year)
    return True


def download_all(years=None):
    years = list(years) if years else missing_years()
    if not years:
        logger.info("Energy balance cache is complete; nothing to download.")
        return
    for year in years:
        download_year(year)


if __name__ == "__main__":
    download_all([int(a) for a in sys.argv[1:]] or None)
