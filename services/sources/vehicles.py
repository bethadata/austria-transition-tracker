# -*- coding: utf-8 -*-
"""Vehicle fleet and registrations: eurostat spliced with Statistik Austria.

The most hand-made reader in the project, and unavoidably so. eurostat reports
Austrian vehicles by motor energy yearly and roughly a year late; Statistik
Austria publishes the same thing monthly, in cumulative Excel workbooks with one
sheet per month and the figures buried in a labelled column of a mixed-content
table. Every chart on the Transport page that is not a fuel volume comes from
gluing those two together.

**The manual drops.** These files cannot be downloaded by the pipeline. They go
in `data_raw/statistik_austria/Fahrzeuge/`:

  NeuzulassungenFahrzeugeJaennerBis<Monat><Jahr>         new registrations,
      cumulative Jan..<Monat>, one sheet per month. Drop the newest one; older
      months in the same year come out of the same file.
  kfz-bestand_<Jahr>                                    the fleet stock
      yearbook, whose `tab_2` carries 1995..2012 -- years eurostat does not have.
  BestandFahrzeuge<Monat><Jahr>VorlaeufigeDaten         preliminary monthly
      stock, used only to push the stock chart past the newest eurostat year.
      Optional: absent means the chart simply ends at eurostat's last year.

**Two spellings of every one of those names.** Statistik Austria's export portal
changed in 2026: the files arrive as `.ods` rather than `.xlsx`, and the download
carries a language/table prefix (`DE2__NeuzulassungenFahrzeugeJaennerBisJuli2026
.ods`). Both extensions and an optional `<prefix>__` are matched, because the
older files keep their old names and are still the only source for their years.
Reading `.ods` needs `odfpy` -- declared in `pyproject.toml`, and pandas picks
the engine off the extension.

Which years exist is read off the directory, never hardcoded. It used to be a
literal `[2019, 2020, ..., 2025]` in two modules, so a newly dropped file for the
next year was silently ignored -- the chart did not break, it just stopped
moving, which is the failure mode nobody notices.

**Category, not fuel.** `FUEL_CATEGORIES` collapses eurostat's fourteen motor
energies into the six a reader thinks in. The order is the palette order.
"""

import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from loguru import logger

from paths import DATA_RAW

from . import eurostat

FAHRZEUGE_DIR = DATA_RAW + "/statistik_austria/Fahrzeuge"

#: Every drop in this directory is matched by pattern, never named literally.
#: `_PREFIX` covers the export portal's language/table prefix, which appeared in
#: 2026 (`DE2__Neuzulassungen...`); `_SUFFIX` covers the move from .xlsx to .ods
#: in the same change. Both halves are optional on purpose -- the files already
#: on disk keep their old names and remain the only source for their years.
_PREFIX = r"(?:[A-Za-z0-9]+__)?"
_SUFFIX = r"\.(?:xlsx|ods)$"

REGISTRATIONS_RE = re.compile(
    _PREFIX + r"NeuzulassungenFahrzeugeJaennerBis([A-Za-z]+)(\d{4})" + _SUFFIX)
YEARBOOK_RE = re.compile(_PREFIX + r"kfz-bestand_(\d{4})" + _SUFFIX)
BESTAND_RE = re.compile(
    _PREFIX + r"BestandFahrzeuge([A-Za-z]+)(\d{4})VorlaeufigeDaten" + _SUFFIX)

#: The heading of a preliminary workbook names the day it is a snapshot of.
BESTAND_DATE_RE = re.compile(r"am (\d{2})\.(\d{2})\.(\d{4})")

#: The fuel breakdown sits under one of these two sheet names -- older exports
#: used the second, the 2026 ones the first. Tried in order.
BESTAND_SHEETS = ("Pkw_nach_Kraftstoff", "Pkw")

#: eurostat motor energies grouped into the six categories the charts show.
#: Order is the legend and palette order and is a CVD-safety decision.
FUEL_CATEGORIES = {
    "Diesel": ["Diesel (excluding hybrids) [DIE_X_HYB]"],
    "Gasoline": ["Petrol (excluding hybrids) [PET_X_HYB]"],
    "Hybrid": ["Hybrid electric-petrol [ELC_PET_HYB]",
               "Hybrid diesel-electric [ELC_DIE_HYB]"],
    "Hybrid plugin": ["Plug-in hybrid diesel-electric [ELC_DIE_PI]",
                      "Plug-in hybrid petrol-electric [ELC_PET_PI]"],
    "Electric": ["Electricity [ELC]"],
    "Other": ["Liquefied petroleum gases (LPG) [LPG]",
              "Natural Gas [GAS]",
              "Hydrogen and fuel cells [HYD_FCELL]",
              "Bioethanol [BIOETH]",
              "Biodiesel [BIODIE]",
              "Bi-fuel [BIFUEL]",
              "Other [OTH]"],
}

#: Statistik Austria names its files with umlaut-free month names but its *sheets*
#: with the real ones, so both spellings are needed.
GERMAN_MONTHS = {"Jaenner": 1, "Februar": 2, "Maerz": 3, "April": 4,
                 "Mai": 5, "Juni": 6, "Juli": 7, "August": 8,
                 "September": 9, "Oktober": 10, "November": 11, "Dezember": 12}

_SHEET_NAMES = {"Jaenner": "Jänner", "Maerz": "März"}


def sheet_name(month_name):
    """The workbook sheet for a month, given the spelling used in filenames."""
    return _SHEET_NAMES.get(month_name, month_name)


# ---------------------------------------------------------------------------
# New registrations, monthly (Statistik Austria on top of eurostat)
# ---------------------------------------------------------------------------

def registration_workbooks():
    """{year: (path, last month covered)}, newest file per year, from disk.

    The workbooks are cumulative, so only the newest file of a year matters --
    it contains every month of that year up to its own.
    """
    found = {}
    if not os.path.isdir(FAHRZEUGE_DIR):
        raise FileNotFoundError(
            "%s is missing. It holds manual Statistik Austria downloads; see the "
            "module docstring for what goes in it." % FAHRZEUGE_DIR)
    for entry in os.listdir(FAHRZEUGE_DIR):
        m = REGISTRATIONS_RE.match(entry)
        if not m:
            continue
        month_name, year = m.group(1), int(m.group(2))
        if month_name not in GERMAN_MONTHS:
            continue
        month = GERMAN_MONTHS[month_name]
        if year not in found or month > found[year][1]:
            found[year] = (FAHRZEUGE_DIR + "/" + entry, month)
    if not found:
        raise FileNotFoundError("no Neuzulassungen workbooks in %s" % FAHRZEUGE_DIR)
    return found


def new_registrations_monthly():
    """Monthly new car registrations by fuel category, 2013 to the newest month.

    2013-2018 is eurostat's yearly figure divided by twelve -- a flat line
    within each year, which is honest about what the source can say and is why
    those years look like steps. From 2019 the Statistik Austria monthlies take
    over entirely.
    """
    table = eurostat.read("cars", "road_eqr_carpda")

    # eurostat's yearly window here is deliberately fixed: from 2019 the monthly
    # source is better and completely replaces it, so extending this range would
    # only add years that are immediately overwritten.
    eurostat_years = [2013, 2014, 2015, 2016, 2017, 2018]
    yearly = {}
    for category, motors in FUEL_CATEGORIES.items():
        yearly[category] = {str(year): 0 for year in eurostat_years}
        for motor in motors:
            selected = eurostat.select(table, {"mot_nrg": motor}, "NR")
            for year in eurostat_years:
                # Summing subtypes into a category: a motor energy the source
                # does not list contributes nothing, so a gap is 0 here. It is
                # not 0 in eurostat.select, where a gap is a gap.
                value = selected[str(year)]
                if not np.isnan(value):
                    yearly[category][str(year)] += value

    months = pd.date_range(start=datetime(eurostat_years[0], 1, 1),
                           end=datetime(eurostat_years[-1], 12, 1), freq="MS")
    monthly = {c: {t: yearly[c][str(t.year)] / 12 for t in months}
               for c in FUEL_CATEGORIES}
    monthly["Total"] = {t: sum(monthly[c][t] for c in FUEL_CATEGORIES) for t in months}

    #: The four rows Statistik Austria labels directly. Hybrids are not among
    #: them and are counted separately below.
    direct = {"Total": "Pkw insgesamt",
              "Gasoline": "Benzin",
              "Diesel": "Diesel",
              "Electric": "Elektro"}

    for year, (path, last_month) in sorted(registration_workbooks().items()):
        month_names = list(GERMAN_MONTHS)
        for month_name in month_names[:last_month]:
            t = pd.to_datetime(datetime(year, GERMAN_MONTHS[month_name], 1))
            sheet = pd.read_excel(path, sheet_name=sheet_name(month_name))
            number = sheet["Unnamed: 1"]
            column = sheet["Tabelle 1a: Kfz-Neuzulassungen"]

            for category, german in direct.items():
                for c in range(len(column)):
                    if str(column[c])[:len(german)] == german:
                        monthly[category][t] = float(number[c])
                        break

            # "Benzin/Elektro" and "Diesel/Elektro" each head a two-row block:
            # the total for that combination, then the plug-in subset on the
            # next row. So a full hybrid is the difference, and the plug-in is
            # the second row -- there is no row that states either directly.
            hybrids = plugins = 0
            for german in ["Benzin/Elektro", "Diesel/Elektro"]:
                for c in range(len(column)):
                    if str(column[c])[:14] == german:
                        hybrids += float(number[c]) - float(number[c + 1])
                        plugins += float(number[c + 1])
                        break
            monthly["Hybrid"][t] = hybrids
            monthly["Hybrid plugin"][t] = plugins

            # Statistik Austria publishes no "other fuels" row, so it is the
            # residual of the total against everything named.
            monthly["Other"][t] = (monthly["Total"][t]
                                   - monthly["Diesel"][t]
                                   - monthly["Gasoline"][t]
                                   - monthly["Electric"][t]
                                   - monthly["Hybrid"][t]
                                   - monthly["Hybrid plugin"][t])
    return monthly


# ---------------------------------------------------------------------------
# Yearly fleet and registrations (eurostat, extended for cars)
# ---------------------------------------------------------------------------

def yearly_by_fuel(name, code, options=None):
    """Yearly vehicle counts by fuel category, straight from eurostat.

    Used for the lorry registrations (both weight classes) and, via
    `car_stock_yearly`, for the car fleet.
    """
    options = dict(options or {})
    table = eurostat.read(name, code)
    # fillna(0) rather than the usual gap handling: every cell here is a count
    # of vehicles in a category, and eurostat leaves a category it did not
    # observe empty rather than writing a zero.
    table = table.fillna(0)

    first = last = None
    for year in range(1990, 2101):
        column = "%i" % year
        if column in table and sum(table[column]) > 0:
            if first is None:
                first = year
            last = year

    years = list(range(first, last + 1))
    counts = {}
    for category, motors in FUEL_CATEGORIES.items():
        counts[category] = {str(year): 0 for year in years}
        for motor in motors:
            options["mot_nrg"] = motor
            selected = eurostat.select(table, options, "NR")
            for year in years:
                value = selected[str(year)]
                if not np.isnan(value):
                    counts[category][str(year)] += value

    times = pd.date_range(start=datetime(years[0], 1, 1),
                          end=datetime(years[-1], 1, 1), freq="YS")
    out = {c: {t: counts[c][str(t.year)] for t in times} for c in FUEL_CATEGORIES}
    out["Total"] = {t: sum(out[c][t] for c in FUEL_CATEGORIES) for t in times}
    return out, years


def car_stock_yearly():
    """The car fleet by fuel, 1995 to the newest figure available.

    Four sources spliced in one series, each covering what the previous one
    cannot:

      1995-2012  the kfz-bestand yearbooks -- eurostat does not go back that far
      2013-....  eurostat
      then       any complete year the newest yearbook has and eurostat does not
      then       the newest preliminary monthly stock file, if one was dropped

    Returns (data, month, year, preliminary): how far the newest point runs, and
    whether it is provisional. The chart's note is chosen from that rather than
    stating a date, which is what it used to do -- the date was written into the
    locale by hand and went stale silently.

    **Which of the four supplies the end of the series is read off the disk.**
    It used to be `datetime.today().year - 1` arithmetic, which encoded "eurostat
    is two years behind and the preliminary file is for last year". Both parts
    stopped holding: in August 2026 eurostat ended 2024, the yearbook had a
    complete 2025 and the preliminary file was dated 31.07.2026, and the chart
    quietly ended in 2024 with two newer sources sitting unread in the directory.
    """
    stock, years = yearly_by_fuel("cars", "road_eqs_carpda")
    yearbook = _yearbook_series()
    stock = _prepend_yearbook(stock, yearbook)

    newest_year, newest_month, preliminary = years[-1], 12, False

    # Complete years beyond eurostat. Without this the preliminary file below
    # would leave a hole wherever the yearbook is a year ahead of eurostat and
    # the preliminary file a year ahead of the yearbook -- and a hole in a fleet
    # line reads as a rendering quirk, not as a missing year.
    for year in sorted(y for y in yearbook if y > newest_year):
        t = datetime(year, 1, 1)
        for category, value in yearbook[year].items():
            stock[category][t] = value
        newest_year = year

    found = _newest_bestand()
    if found and found[2] > newest_year:
        path, month, year = found
        stock = _extend_from_bestand(stock, path, year)
        newest_year, newest_month, preliminary = year, month, True

    return stock, newest_month, newest_year, preliminary


def _newest_bestand():
    """The newest preliminary stock workbook: (path, month, year), or None.

    None is an ordinary outcome, not an error -- the file is optional and the
    caller then ends the series at the newest complete year instead.

    The workbook is *ranked* by the month and year in its filename but *dated*
    by its own heading ("Vorlaeufiger Pkw-Bestand ... am 31.07.2026"), because
    only the heading says what the figures are a snapshot of. A filename that
    disagrees is worth knowing about but is not worth failing over, so it is
    logged.
    """
    ranked = []
    for entry in os.listdir(FAHRZEUGE_DIR):
        m = BESTAND_RE.match(entry)
        if m and m.group(1) in GERMAN_MONTHS:
            ranked.append(((int(m.group(2)), GERMAN_MONTHS[m.group(1)]),
                           FAHRZEUGE_DIR + "/" + entry))
    if not ranked:
        return None
    (named_year, named_month), path = max(ranked)

    month, year = _bestand_date(path)
    if (year, month) != (named_year, named_month):
        logger.warning("%s is headed %02i/%i -- using the heading, not the name",
                       os.path.basename(path), month, year)
    return path, month, year


def _bestand_date(path):
    """(month, year) from a preliminary workbook's heading row."""
    heading = pd.read_excel(path, sheet_name=_bestand_sheet_name(path),
                            header=None, nrows=1).iloc[0, 0]
    m = BESTAND_DATE_RE.search(str(heading))
    if not m:
        raise ValueError(
            "no 'am TT.MM.JJJJ' date in the heading of %s, which read %r. That "
            "heading is what dates the newest point on the fleet chart."
            % (path, heading))
    return int(m.group(2)), int(m.group(3))


def _bestand_sheet_name(path):
    """The fuel-breakdown sheet, under whichever of its two names it has."""
    available = pd.ExcelFile(path).sheet_names
    for name in BESTAND_SHEETS:
        if name in available:
            return name
    raise KeyError("none of %s in %s, which has %s"
                   % (list(BESTAND_SHEETS), path, available))


#: The years the yearbooks supply and eurostat does not.
_YEARBOOK_YEARS = range(1995, 2013)

#: category -> the `tab_2` column stem it is read from. Stems, not names: see
#: `_yearbook_column`.
_YEARBOOK_COLUMNS = {"Total": "Pkw",
                     "Diesel": "Diesel",
                     "Gasoline": "Benzin",
                     "Electric": "Elektro",
                     "Other": "Sonstige Pkw"}


def _yearbook_series():
    """{year: {category: count}} from every kfz-bestand yearbook on disk.

    **Read newest-first across all editions, not from the newest one alone.** The
    2025 edition dropped the rows for 1996-1999 that every earlier edition
    carried, so taking only the newest would have punched a four-year hole in a
    chart that has no other source for them -- and a hole in a fleet line reads
    as a rendering quirk, not as missing data. Each year comes from the newest
    yearbook that still reports it.

    Hybrid plugin is 0 throughout: no yearbook has ever split plug-ins out, so a
    plug-in is counted as a hybrid. Hybrid itself is 0 for years whose edition
    has no such column at all. The chart's note says both.
    """
    found = {}
    for path in _yearbooks():
        raw = _read_yearbook(path)
        rows = _yearbook_column(raw, "Jahr").astype(int)
        # The 2025 yearbook broke hybrids out of "Sonstige" and reports them
        # from 2006; older editions have no such column. Reading it where it
        # exists is what keeps the categories summing to the Pkw total.
        hybrids = _yearbook_column(raw, "Hybrid", required=False)
        for year in sorted(set(int(y) for y in rows)):
            if year in found:
                continue
            mask = rows == year
            values = {category: float(_yearbook_column(raw, column)[mask].iloc[0])
                      for category, column in _YEARBOOK_COLUMNS.items()}
            values["Hybrid"] = 0.0 if hybrids is None else float(hybrids[mask].iloc[0])
            values["Hybrid plugin"] = 0.0
            found[year] = values
    return found


def _prepend_yearbook(stock, yearbook):
    """The yearbook years that come before eurostat, ahead of eurostat's own."""
    missing = [year for year in _YEARBOOK_YEARS if year not in yearbook]
    if missing:
        raise ValueError(
            "no kfz-bestand yearbook in %s reports %s. Those years exist only in "
            "the older editions -- restore them rather than dropping them; a "
            "newer yearbook is not a superset of an older one."
            % (FAHRZEUGE_DIR, missing))

    # Written in year order: these dicts are keyed by timestamp and consumed as
    # the x axis in the order they were inserted.
    out = {category: {} for category in stock}
    for year in _YEARBOOK_YEARS:
        t = datetime(year, 1, 1)
        for category, value in yearbook[year].items():
            out[category][t] = value
    for category in stock:
        out[category].update(stock[category])
    return out


def _read_yearbook(path):
    """One yearbook's `tab_2`, with both "no figure" markers read as 0.

    Which marker is used changed with the file format -- `-` in the .xlsx
    editions, `.` in the .ods ones. Both mean the category did not exist in that
    year, which in a count of vehicles is a 0 rather than a gap.
    """
    raw = pd.read_excel(path, decimal=",", skiprows=1, sheet_name="tab_2", skipfooter=1)
    return raw.replace(["-", "."], 0).infer_objects()


def _yearbook_column(raw, name, required=True):
    """A yearbook column, matched without its footnote marker.

    `tab_2` names its columns with the footnote number attached -- `Jahr1`,
    `Benzin2`, `Sonstige Pkw3` -- so the numbers move whenever a footnote is
    added above them. The 2025 yearbook inserted a `Hybrid` column and pushed
    `Sonstige Pkw3` to `Sonstige Pkw4`; matching literally raised a KeyError,
    which is the loud version of this failure. The quiet version would be a
    column that still exists under the old name and now means something else,
    so the stem is matched exactly rather than by prefix.
    """
    for column in raw.columns:
        if str(column).rstrip("0123456789") == name:
            return raw[column]
    if required:
        raise KeyError(
            "no %r column in the yearbook's tab_2 -- it has %r" % (name, list(raw.columns)))
    return None


def _yearbooks():
    """Every kfz-bestand yearbook on disk, newest edition first."""
    candidates = []
    for entry in os.listdir(FAHRZEUGE_DIR):
        m = YEARBOOK_RE.match(entry)
        if m:
            candidates.append((int(m.group(1)), FAHRZEUGE_DIR + "/" + entry))
    if not candidates:
        raise FileNotFoundError(
            "no kfz-bestand_<year>.[xlsx|ods] in %s" % FAHRZEUGE_DIR)
    return [path for _year, path in sorted(candidates, reverse=True)]


def _extend_from_bestand(stock, path, year):
    """Append one year from a preliminary monthly stock workbook.

    Hybrid plugin is 0 rather than a gap: this table reports full and plug-in
    hybrids in one figure, so the split is genuinely unavailable and the whole
    amount is counted as Hybrid -- the same merge the yearbook forces. The
    chart's note says so.
    """
    sheet = pd.read_excel(path, decimal=",", skiprows=1,
                          sheet_name=_bestand_sheet_name(path))
    number = np.array(sheet.iloc[:, [1]])
    column = np.array(sheet.iloc[:, [0]])

    def value(label):
        return float(number[column == label][0])

    t = datetime(year, 1, 1)
    stock["Total"][t] = value("Pkw insgesamt")
    stock["Diesel"][t] = value("Diesel")
    stock["Gasoline"][t] = value("Benzin inkl. Flex-Fuel")
    stock["Hybrid"][t] = value("Benzin/Elektro (hybrid)") + value("Diesel/Elektro (hybrid)")
    stock["Electric"][t] = value("Elektro")
    stock["Hybrid plugin"][t] = 0
    stock["Other"][t] = stock["Total"][t] - sum(
        stock[c][t] for c in ["Diesel", "Gasoline", "Hybrid", "Electric"])
    return stock
