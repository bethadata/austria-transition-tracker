# -*- coding: utf-8 -*-
"""New battery-electric car registrations by manufacturer.

Four charts on the Transport page, and the only ones on the site broken out by
company rather than by fuel, sector or region.

**Where the numbers come from.** Statistik Austria's monthly registration
workbook carries, buried among two dozen other tables, a "Table 7: Pkw
registrations by TOP 10 brands and types with electric drive". That table is ten
brands plus a "Sonstige" catch-all, and *which* ten it lists changes month to
month. So this reads every month's table, ranks brands by their all-time total,
keeps the leaders, and folds everything else into "other".

Two consequences worth knowing:

  * a brand outside the leaders in one month is not zero, it is unreported --
    but it is read as 0, because the table only lists a brand when it is in that
    month's top ten. There is no way to tell the two apart from this source.
  * "other" is Sonstige plus every brand outside the leader board, so it is a
    residual and moves when the leader board does.

**Brand names are matched case-insensitively, and that is load-bearing.**
Statistik Austria wrote them in title case from 2019 and switched to upper case
in January 2025 ("Tesla" -> "TESLA"). Matching them literally, as the first
version of this module did, meant that from that month on every brand whose name
is not an acronym read as zero -- eight of the eleven series flatlined and the
chart's total fell to less than half the real figure, with the difference sitting
invisibly outside the chart. Nothing looked broken: the series were still there,
the axes still scaled, the newest bars were simply short.

Twelve series is past the point where categorical colour can carry identity on
its own; the legend and the unified hover are what identify a brand, which is
why `src/utils/palette.ts` says so where it re-steps its slots past eight.
"""

from datetime import datetime

import pandas as pd
from loguru import logger

from sources import vehicles

import series as S

from .spec import chart

#: The table's own catch-all row, and the shorter wording it carried once
#: (11/2020). Never a leader, always part of "other".
SONSTIGE = "Sonstige Pkw mit Elektroantrieb"
_CATCH_ALL = {"sonstige pkw mit elektroantrieb", "sonstige pkw"}

#: Spellings that are not just a case difference. "Hyunda" is a typo in the
#: source (07/2021) and would otherwise split Hyundai into two series, one of
#: which is off the leader board and lands in "other".
_ALIASES = {"hyunda": "hyundai"}

#: Names that are not words, so title-casing them would be wrong.
_ACRONYMS = {"vw": "VW", "bmw": "BMW", "byd": "BYD", "mg": "MG",
             "jac": "JAC", "mini": "MINI"}

#: How many brands are named. Eleven plus "other" plus the total is twelve
#: series, which is the ceiling the palette is built for.
LEADERS = 11

#: The heading that marks the brand table inside the workbook's first sheet
#: column. Matched exactly: Statistik Austria has kept this wording since 2019.
TABLE_7 = ("Tabelle 7: Pkw-Neuzulassungen nach TOP 10 Marken und Typen "
           "mit Elektroantrieb")

_LABEL_COLUMN = "Tabelle 1a: Kfz-Neuzulassungen"
_VALUE_COLUMN = "Unnamed: 1"

#: Rows of the table, relative to its heading: two rows of header, then eleven
#: brands.
_FIRST_ROW = 2
_ROWS = 11

SOURCE = "Statistik Austria"
NOTE = "Only the top brands (over all years) are shown separately."


def plot():
    logger.info("Charts: BEV registrations by brand ...")

    by_month = _read_workbooks()
    leaders = _leaders(by_month)
    monthly = _assemble(by_month, leaders)

    chart("monthly_registrations_brands_absolute",
          title="AT new monthly BEV registrations: car brands absolute number",
          unit="Number",
          data=monthly,
          source=SOURCE, note=NOTE,
          time_res="monthly",
          view="toggle", initial="bar")

    chart("monthly_registrations_brands_shares",
          title="AT new monthly BEV registrations: car brands shares",
          unit="Share (%)",
          data=S.shares(monthly),
          source=SOURCE, note=NOTE,
          time_res="monthly",
          view="toggle", initial="bar")

    yearly = S.to_yearly(monthly)

    chart("yearly_registrations_brands_absolute",
          title="AT new yearly BEV registrations: car brands absolute number",
          unit="Number",
          data=yearly,
          source=SOURCE, note=NOTE,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("yearly_registrations_brands_shares",
          title="AT new yearly BEV registrations: car brands shares",
          unit="Share (%)",
          data=S.shares(yearly),
          source=SOURCE, note=NOTE,
          time_res="yearly",
          view="toggle", initial="bar")


def _read_workbooks():
    """{month: {brand: registrations}} across every workbook on disk.

    Shares `sources/vehicles.registration_workbooks()` with the fuel-type
    charts: it is the same set of files, and both modules used to carry their own
    hardcoded list of years.
    """
    by_month = {}
    month_names = list(vehicles.GERMAN_MONTHS)
    for year, (path, last_month) in sorted(vehicles.registration_workbooks().items()):
        for month_name in month_names[:last_month]:
            t = pd.to_datetime(datetime(year, vehicles.GERMAN_MONTHS[month_name], 1))
            sheet = pd.read_excel(path, sheet_name=vehicles.sheet_name(month_name))
            labels = sheet[_LABEL_COLUMN]
            numbers = sheet[_VALUE_COLUMN]

            by_month[t] = {}
            for row in range(len(labels)):
                if str(labels[row]) != TABLE_7:
                    continue
                for offset in range(_FIRST_ROW, _FIRST_ROW + _ROWS):
                    brand = _brand(str(labels[row + offset]))
                    # += rather than =: a month that ever listed one brand under
                    # two spellings would otherwise keep only the second.
                    by_month[t][brand] = (by_month[t].get(brand, 0)
                                          + float(numbers[row + offset]))
                break
    return by_month


def _brand(label):
    """A source label -> the one name this brand is counted under."""
    key = label.strip().casefold()
    if key in _CATCH_ALL:
        return SONSTIGE
    key = _ALIASES.get(key, key)
    return _ACRONYMS.get(key, key.title())


def _leaders(by_month):
    """The LEADERS brands with the largest all-time totals, Sonstige excluded."""
    totals = {}
    for month in by_month:
        for brand, value in by_month[month].items():
            totals[brand] = totals.get(brand, 0) + value
    ranked = [b for b in sorted(totals, key=totals.get, reverse=True) if b != SONSTIGE]
    return ranked[:LEADERS]


def _assemble(by_month, leaders):
    """Leader series, an "other" residual, and the total, on one monthly axis."""
    axis = list(by_month)
    pairs = []
    for brand in leaders:
        # A brand absent from a month's table is read as 0: the source lists a
        # brand only when it is in that month's top ten, so "absent" and "none
        # sold" are indistinguishable here.
        pairs.append((brand, S.series(axis, [by_month[t].get(brand, 0) for t in axis])))

    # Sonstige plus every brand off the leader board. This used to reset its
    # accumulator inside the loop over brands, so it reported whichever single
    # brand happened to be listed last rather than their sum -- which was
    # Sonstige, and therefore looked right.
    other = []
    for t in axis:
        other.append(sum(value for brand, value in by_month[t].items()
                         if brand not in leaders))
    pairs.append(("other", S.series(axis, other)))

    return S.total(S.wrap(pairs))
