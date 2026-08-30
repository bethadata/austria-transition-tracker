# -*- coding: utf-8 -*-
"""Reading the cached eurostat tables.

`download/eurostat.py` writes one `.xlsx` per dataset into
`data_raw/eurostat/AT_<name>_<code>.xlsx`, with the coded dimension values
expanded to `"Label [CODE]"`. This module turns one of those into the
`{"data": {label: {"x", "y"}}}` shape the chart modules speak.

Two functions do almost all of the work -- `monthly()` and `yearly()` -- and both
are thin: pick the rows matching a set of dimension filters, read the period
columns off that row, and hand back a series. Everything about *which* rows
belongs at the call site, because that is the part a reader needs to see next to
the chart.

**A gap is nan here, never 0.** These are the series that get plotted directly,
so an unpublished month has to break the line. The old code had a `fillna(0)`
sitting upstream of the function that looked like it owned this decision, which
is why fixing the obvious place changed nothing: the newest months read as a
collapse to zero rather than as data that has not arrived yet. Summing subtypes
*into* a category is the one place a gap is 0, and that lives in
`series.py` where it can be stated once.
"""

import os
from datetime import datetime

import numpy as np
import pandas as pd

from paths import DATA_RAW

import series as S

EUROSTAT_DIR = DATA_RAW + "/eurostat"


def path(name, code, geo="AT"):
    """The cache file for one dataset. One spelling of this, in one place."""
    return "%s/%s_%s_%s.xlsx" % (EUROSTAT_DIR, geo, name, code)


def read(name, code, geo="AT"):
    if not os.path.exists(path(name, code, geo)):
        # Named explicitly because `eurostat/` is git-ignored: on a fresh clone
        # the whole directory is absent, and pandas' own error does not say that
        # `python scrape.py` is the fix.
        raise FileNotFoundError(
            "%s is missing -- run `python scrape.py` to download it."
            % path(name, code, geo))
    return pd.read_excel(path(name, code, geo))


def select(table, options, unit):
    """One row of a eurostat table, as {period: value}.

    A gap is nan, and so is an empty selection: both an unpublished cell and a
    filter that matches nothing used to become a real zero here, which is
    indistinguishable from a measured zero -- in a stacked-area emissions chart
    that silently understates a sector instead of breaking the line. nan rather
    than None because these values are summed with numpy downstream; the JSON
    writer turns it into null.
    """
    rows = table[table["unit"] == unit]
    for option in options:
        rows = rows[rows[option] == options[option]]

    out = {}
    for period in rows.keys():
        is_monthly = "-" in period and len(period) == 7
        is_yearly = ("20" in period or "19" in period) and len(period) == 4
        if not (is_monthly or is_yearly):
            continue
        out[period] = np.nan if len(rows[period]) == 0 else float(rows[period].iloc[0])
    return out


def monthly(name, code, options, unit, geo="AT", start_year=1990, movmean=4,
            label="Monthly"):
    """A monthly series plus its trailing moving average.

    Returns two series -- the raw months and the `movmean`-month average -- since
    every chart built on monthly eurostat data shows both.
    """
    table = read(name, code, geo)
    by_period = select(table, options, unit)

    if name == "meat" and options.get("meat") == "Chicken [B7100]":
        by_period = _splice_poultry(table, by_period, unit)

    # The last period that carries any real data anywhere in the table. nansum,
    # not sum: this asks "has this month been published at all", and a single
    # empty cell makes a plain sum nan, so the comparison silently fails and
    # end_year is never assigned.
    end_year = last_month = None
    for period in by_period:
        if np.nansum(table[period]) > 0:
            end_year = int(period.split("-")[0])
            last_month = int(period.split("-")[1])
    if end_year is None:
        raise ValueError("%s (%s): no published data in the cache" % (name, code))

    for period in by_period:
        if by_period[period] > 0:
            start_year = max(start_year, int(period.split("-")[0]))
            break

    months = pd.date_range(start=datetime(start_year, 1, 1),
                           end=datetime(end_year + 1, 1, 1), freq="MS")

    x, y = [], []
    for t in months:
        if t.year > end_year or (t.year == end_year and t.month > last_month):
            continue
        key = "%i-%02i" % (t.year, t.month)
        x.append(t)
        y.append(by_period[key] if key in table.keys() else 0)

    return {"data": {label: S.series(x, y),
                     "%i-Month average" % movmean: S.moving_average(x, y, movmean)},
            "meta": {"movmean": movmean, "code": code}}


def _splice_poultry(table, by_period, unit):
    """eurostat renamed chicken to poultry, twice, in different windows.

    "Chicken [B7100]" is reported for some periods and "Poultry meat [B7000]"
    for others, with no overlap and no announcement. The two windows below are
    where the poultry series is the only one carrying the data.
    """
    poultry = select(table,
                     {"meat": "Poultry meat [B7000]",
                      "meatitem": "Slaughterings [SLAUGHT]"},
                     unit)
    for period in poultry:
        date = datetime.strptime(period, "%Y-%m")
        if date >= datetime(2022, 1, 1):
            by_period[period] = poultry[period]
        elif datetime(2004, 12, 1) <= date <= datetime(2008, 12, 1):
            by_period[period] = poultry[period]
    return by_period


def yearly(name, code, options, unit, geo="AT", start_year=1990, end_year=2100,
           label=None):
    """A yearly series. `label` defaults to `name`, which is what the call sites
    used to rely on implicitly."""
    table = read(name, code, geo)
    by_period = select(table, options, unit)

    first = None
    for year in range(start_year, end_year + 1):
        if str(year) in by_period:
            if first is None:
                first = year
            else:
                end_year = year
    start_year = first if first is not None else start_year

    years = pd.date_range(start=datetime(start_year, 1, 1),
                          end=datetime(end_year, 1, 1), freq="YS")
    x, y = [], []
    for t in years:
        key = "%i" % t.year
        if key in by_period:
            x.append(t)
            y.append(by_period[key])

    # Trailing years the source has a column for but no value in are trimmed: a
    # yearly series that has not reached 2025 yet should end in 2024, not draw an
    # empty 2025. An *interior* gap is left alone -- that is real missing data.
    # This is what the call sites used to work around with a hardcoded
    # `end_year`, which then silently capped the chart once the year arrived.
    while y and np.isnan(y[-1]):
        x.pop()
        y.pop()

    return {"data": {label or name: S.series(x, y)},
            "meta": {"code": code}}
