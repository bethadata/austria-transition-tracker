# -*- coding: utf-8 -*-
"""Statistik Austria: the Mikrozensus "Energieeinsatz der Haushalte" survey.

Two drops from the same biennial household survey, read here because they share
a provider and a sampling frame: the primary heating system of every dwelling,
and the number of air conditioners installed in Austrian households.

Primary heating systems by energy carrier
-----------------------------------------

One manual download, and a genuinely awkward one. The workbook is not a table
but a stack of blocks, one per **two-year survey period** (2003/2004,
2005/2006, ... 2023/2024), each repeating the same seven-row energy-carrier
header. There is no year column: the year lives in a title line above each
block.

So the reader matches on the German carrier name and takes the rows in the order
they appear, which is survey order, and **writes each survey's figure to both
years it covers**. That is why the output has two identical values per pair, and
it is deliberate: the survey is biennial, so 2003 and 2004 genuinely carry the
same measurement. It previously looked like a copy-paste bug -- the same
`.append()` twice with no comment -- which is the sort of thing that gets
"fixed".

The number of survey blocks is counted rather than assumed. It used to be a
hardcoded `end_year=2024`, against which a newly published 2025/2026 block would
have produced two more values than there were dates; the manifest aligns by
zipping x with y, so the new survey would have been silently dropped and the
chart would simply have stopped moving.

Air conditioners in households
------------------------------
The second workbook is the same kind of problem and one degree worse. It is a
stack of blocks too -- one per survey wave -- but each block is a renovation
cross-tabulation whose *last row* carries the figure this project wants, and the
wave is named only in a title line ("... - Juli 2023 bis Juni 2024") above it.
The renovation table itself is not read.

Three things are therefore taken off the file rather than assumed:

  * **the wave, from the title line.** The blocks are not on a fixed cadence --
    the first two cover two years each and the third covers one, with a year
    between them that no wave covers at all. A "one block, two years" rule of
    the kind the heating reader can rely on would invent data here, so each wave
    is a single point dated to the end of its own collection window.
  * **the value column, from the block's own header row**, with footnote digits
    stripped from the stem. Statistik Austria moves those markers between
    editions, and the blocks in the file already on disk do not even have
    identical row counts.
  * **which file is live, from the directory.** A newer edition is not a
    superset -- the vehicles yearbooks have already dropped years an older
    edition carried -- so every matching workbook is walked newest-first and
    each wave is taken from the first edition that still reports it.

The survey publishes a coefficient of variation next to every figure, and it
travels as the chart's error bars. These are sample estimates rather than a
register count, and without the band the reader has no way to
see that.
"""

import os
import re

import numpy as np
import pandas as pd

from paths import DATA_RAW

import series as S

PATH = (DATA_RAW + "/statistik_austria/"
        "08Heizungen2003Bis2024NachBundeslaendernUndVerwendetemEnergietraeger.xlsx")

#: First year of the first survey block in the workbook.
FIRST_YEAR = 2003

#: Years covered by one survey block.
YEARS_PER_SURVEY = 2

#: The seven carriers, in palette order, mapped from the German column values.
CARRIERS = {
    "Heat pumps / solar": "Solar, Wärmepumpen",
    "Biomass": "Holz, Hackschnitzel, Pellets, Holzbriketts",
    "District heat": "Fernwärme",
    "Electricity": "Strom",
    "Natural gas": "Erdgas",
    "Oil": "Heizöl, Flüssiggas",
    "Coal": "Kohle, Koks, Briketts",
}

#: Footnote markers Statistik Austria appends to some carrier names, and strips
#: from others, between editions. Normalised so the lookup above keeps matching.
_FOOTNOTES = {"Kohle, Koks, Briketts2": "Kohle, Koks, Briketts",
              "Heizöl, Flüssiggas3": "Heizöl, Flüssiggas",
              "Erdgas4": "Erdgas"}

_COUNT_COLUMN = 'Anzahl Wohnungen („Hauptwohnsitze“) insgesamt'


def heating_systems():
    """(shares in %, absolute counts) of dwellings by primary heating carrier."""
    raw = pd.read_excel(PATH, skiprows=1, sheet_name="Österreich")
    raw = raw.fillna(0)
    for wrong, right in _FOOTNOTES.items():
        raw = raw.replace(wrong, right)

    counts = {}
    for label, german in CARRIERS.items():
        surveys = [raw[_COUNT_COLUMN][i] for i in raw.index
                   if raw["Energieträger"][i] == german]
        # One survey covers YEARS_PER_SURVEY years; repeat its figure across them.
        counts[label] = [v for v in surveys for _ in range(YEARS_PER_SURVEY)]

    lengths = {len(v) for v in counts.values()}
    if len(lengths) != 1:
        # A carrier whose name changed in one edition would land here rather
        # than quietly producing a series one survey shorter than the rest.
        raise ValueError("heating carriers have different numbers of surveys: %s"
                         % {k: len(v) for k, v in counts.items()})

    n = lengths.pop()
    times = pd.date_range(start="%i-01-01" % FIRST_YEAR, periods=n, freq="YS")

    absolute = S.wrap([(label, S.series(times, np.array(counts[label], dtype=float)))
                       for label in CARRIERS])
    # shares(), not a hand-rolled division: the open-coded version here divided
    # without the * 100 while the chart was labelled "Share [%]", so the site
    # showed Austrian district heating at 0.32 % instead of 32 %.
    return S.shares(absolute), absolute

# ---------------------------------------------------------------------------
# Air conditioners in households
# ---------------------------------------------------------------------------

AIR_CONDITIONING_DIR = DATA_RAW + "/statistik_austria"

#: The drop is matched by pattern, never named literally, so that refreshing it
#: is a file copy rather than an edit to this module. `<from><to>` is the year
#: span in the portal's own filename ("10SanierungsmassnahmenKlimaanlagen
#: 20182024.ods"); the leading table number and the export prefix that Statistik
#: Austria's portal started adding in 2026 (`DE2__...`) are both optional, and
#: either extension is taken -- the same three-way change the vehicles drop went
#: through in one release.
_AIR_CONDITIONING_RE = re.compile(
    r"(?:[A-Za-z0-9]+__)?\d*Sanierungsmassnahmen(?:Und)?Klimaanlagen"
    r"(\d{4})(\d{4})\.(?:xlsx|ods)$", re.I)

#: The title line above each block. The wave is read out of it, so a block whose
#: title stops matching is a loud failure rather than a missing point.
_WAVE_TITLE = "Sanierungsmaßnahmen und Anzahl der Klimaanlagen"

#: The row carrying the figure, and the header cell naming the column it is in.
_AIR_CONDITIONING_ROW = "Anzahl Klimaanlagen in Haushalten"
_COUNT_HEADER = "Wohnungsanzahl"
_CV_HEADER = "Variationskoeffizient"

#: The one series this reader produces. Its label is a locale key downstream.
AIR_CONDITIONING_LABEL = "Air conditioners"


def _stem(cell):
    """A header cell without the footnote markers Statistik Austria moves around.

    `Wohnungsanzahl` and `Variationskoeffizient in Prozent (%)2` are the same
    columns in every edition, but the trailing digits are not stable between
    them -- the same trap as the vehicle yearbook's `Sonstige Pkw3`, where a
    literal match raised on one edition and read the wrong column on the next.
    """
    return re.sub(r"\d+$", "", str(cell).strip()).strip()


def _number(cell):
    """A published figure, or nan where the survey suppressed it.

    Values whose coefficient of variation exceeds 33 % are printed as "-". That
    is a gap, not a zero: a suppressed wave must break the line rather than draw
    a collapse to no air conditioners at all.
    """
    try:
        value = float(cell)
    except (TypeError, ValueError):
        return np.nan
    return np.nan if np.isnan(value) else value


def _air_conditioning_files():
    """Every matching workbook, newest edition first.

    Newest-first and then first-wins per wave, rather than newest-file-wins
    outright: an edition that starts later than its predecessor drops the early
    waves, and this chart has no other source for them.
    """
    found = []
    for entry in sorted(os.listdir(AIR_CONDITIONING_DIR)):
        m = _AIR_CONDITIONING_RE.match(entry)
        if m:
            found.append((int(m.group(2)), int(m.group(1)),
                          AIR_CONDITIONING_DIR + "/" + entry))
    if not found:
        raise FileNotFoundError(
            "no air-conditioning workbook in %s matching %s -- a drop that does "
            "not match its pattern is invisible, not an error"
            % (AIR_CONDITIONING_DIR, _AIR_CONDITIONING_RE.pattern))
    return [path for _, _, path in sorted(found, reverse=True)]


def _wave_year(title):
    """The year a block's collection window ends in, off its title line.

    The window is spelled out in prose ("... - Juli 2023 bis Juni 2024"), so the
    last year mentioned is taken rather than a fixed offset from the first: the
    waves in the file on disk are two years long, two years long, then one.
    """
    years = re.findall(r"\b(?:19|20)\d{2}\b", str(title))
    if not years:
        raise ValueError("air-conditioning block with no year in its title: %r"
                         % title)
    return int(years[-1])


def _air_conditioning_waves(path):
    """{end year: (count, coefficient of variation in %)} from one workbook.

    One pass over the sheet rather than fixed row offsets. Each block sets the
    wave from its title and the value column from its own header row, and the
    figure is read when the labelled row goes past -- so a block gaining or
    losing rows, which has already happened between the three on disk, moves
    nothing.
    """
    raw = pd.read_excel(path, header=None)
    waves = {}
    year = None
    count_col = cv_col = None
    for _, row in raw.iterrows():
        cells = list(row)
        first = str(cells[0]).strip()
        if first.startswith(_WAVE_TITLE):
            year = _wave_year(first)
            count_col = cv_col = None
        elif _COUNT_HEADER in [_stem(c) for c in cells]:
            count_col = [_stem(c) for c in cells].index(_COUNT_HEADER)
            following = count_col + 1
            if (following < len(cells)
                    and _stem(cells[following]).startswith(_CV_HEADER)):
                cv_col = following
        elif first == _AIR_CONDITIONING_ROW:
            if year is None or count_col is None:
                raise ValueError(
                    "%s: '%s' row before its title or header row"
                    % (os.path.basename(path), _AIR_CONDITIONING_ROW))
            cv = _number(cells[cv_col]) if cv_col is not None else np.nan
            waves[year] = (_number(cells[count_col]), cv)
    if not waves:
        raise ValueError(
            "%s: no '%s' row -- the label changed upstream, which would "
            "otherwise render as a chart that stopped moving"
            % (os.path.basename(path), _AIR_CONDITIONING_ROW))
    return waves


def air_conditioners():
    """Air conditioners installed in Austrian households, one point per wave.

    Dated to 1 January of the year each collection window ends in, which is the
    grid the rest of the site's yearly charts sit on. Stamped one year at a time
    rather than with a `date_range`: the waves are irregularly spaced, and
    `date_range(start, end, periods=n)` is what put the waste chart's points on
    31 December and drew 1992 twice.

    The coefficient of variation the survey publishes per figure comes back as
    error-bar half widths in `meta["uncertainty"]`, in the unit of the series.
    """
    waves = {}
    for path in _air_conditioning_files():
        # First edition to report a wave wins; later ones are older files kept
        # for the waves the newest edition no longer carries.
        for year, value in _air_conditioning_waves(path).items():
            waves.setdefault(year, value)

    years = sorted(waves)
    counts = np.array([waves[y][0] for y in years], dtype=float)
    # cv is a percentage of the estimate; the error bars are absolute.
    band = np.array([waves[y][1] for y in years], dtype=float) * counts / 100.0

    times = [pd.Timestamp("%i-01-01" % y) for y in years]
    return S.wrap([(AIR_CONDITIONING_LABEL, S.series(times, counts))],
                  meta={"uncertainty": {AIR_CONDITIONING_LABEL: band}})
