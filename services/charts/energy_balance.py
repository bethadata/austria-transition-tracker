# -*- coding: utf-8 -*-
"""Gross inland consumption and final energy use per sector.

Two charts on the Energy page and eight more spread across the sector pages,
all from the eurostat full energy balance and all built the same way: a fuel
grouping, a set of balance aggregates, absolute and share versions.

**The sector charts are `groups` charts**, which is the one chart shape unique to
this module: a dataset selector above the plot. Industry has thirteen
sub-branches, buildings two, transport six -- so rather than thirteen charts the
reader picks a sub-branch and the same axes redraw. The selector always carries a
"Total" entry, which is the sum of the sub-branches.

**The preliminary Austrian balance.** eurostat's balance is roughly eighteen
months late; Statistik Austria publishes a provisional national balance sooner.
When the eurostat series ends at the year the provisional file covers, that one
extra year is appended from the provisional file and the source line says so.
The file is a manual drop and is matched by year, so the block simply does not
run once eurostat catches up -- which is the state it is in most of the time.
"""

import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from loguru import logger

from paths import DATA_RAW
from sources import energy_balance

import series as S

from .spec import chart

BALANCE_SOURCE = "eurostat energy balances (nrg_bal_c)"
PRELIMINARY_SOURCE = (BALANCE_SOURCE + " + Statistik Austria preliminary energy balance")

#: Gross inland consumption: reader's categories -> eurostat fuels.
#: "Other" here is an explicit list rather than a residual, because gross inland
#: consumption already balances -- a residual would be zero and hide the fact
#: that manufactured gases and waste heat are what is in the bucket.
GROSS_FUELS = {
    "Natural gas": ["Natural gas"],
    "Oil": ["Oil and petroleum products (excluding biofuel portion)"],
    "Coal": ["Solid fossil fuels"],
    "Biomass": ["Primary solid biofuels", "Charcoal", "Pure biogasoline",
                "Blended biogasoline", "Pure biodiesels", "Blended biodiesels",
                "Pure bio jet kerosene", "Blended bio jet kerosene",
                "Other liquid biofuels", "Biogases"],
    "Renewable electricity": ["Hydro", "Wind", "Solar photovoltaic",
                              "Tide, wave, ocean"],
    "Ambient heat": ["Geothermal", "Solar thermal", "Ambient heat (heat pumps)"],
    "Other": ["Manufactured gases", "Industrial waste (non-renewable)",
              "Non-renewable municipal waste", "Renewable municipal waste",
              "Heat", "Electricity"],
}

#: Final energy use: the same idea, but electricity and district heat are
#: carriers a sector consumes rather than primary energy, so they get their own
#: categories.
FINAL_FUELS = {
    "Natural gas": ["Natural gas"],
    "Oil": ["Oil and petroleum products (excluding biofuel portion)"],
    "Coal": ["Solid fossil fuels"],
    "Biomass": ["Primary solid biofuels", "Charcoal", "Pure biogasoline",
                "Blended biogasoline", "Pure biodiesels", "Blended biodiesels",
                "Pure bio jet kerosene", "Blended bio jet kerosene",
                "Other liquid biofuels", "Biogases"],
    "Electricity": ["Electricity"],
    "District Heat": ["Heat"],
    "Other": ["Manufactured gases", "Industrial waste (non-renewable)",
              "Geothermal", "Solar thermal", "Ambient heat (heat pumps)"],
}

_FINAL = "Final consumption"
_OTHER = _FINAL + " - other sectors"
_IND = _FINAL + " - industry sector"
_TRA = _FINAL + " - transport sector"

#: sector -> {selector entry: eurostat balance aggregate}. The chart-id stem is
#: the key of SECTORS; "total" is the whole-country chart on the Energy page,
#: which has one aggregate and therefore no selector.
SECTORS = {
    "buildings": ("Buildings", {
        "Households": _OTHER + " - households - energy use",
        "Commercial": _OTHER + " - commercial and public services - energy use",
    }),
    "industry": ("Industry", {
        "Iron & Steel": _IND + " - iron and steel - energy use",
        "Chemicals": _IND + " - chemical and petrochemical - energy use",
        "Pulp & Paper": _IND + " - paper, pulp and printing - energy use",
        "Non-metallic minerals": _IND + " - non-metallic minerals - energy use",
        "Non-ferrous metals": _IND + " - non-ferrous metals - energy use",
        "Transport equipment": _IND + " - transport equipment - energy use",
        "Machinery": _IND + " - machinery - energy use",
        "Mining": _IND + " - mining and quarrying - energy use",
        "Food industry": _IND + " - food, beverages and tobacco - energy use",
        "Wood industry": _IND + " - wood and wood products - energy use",
        "Construction": _IND + " - construction - energy use",
        "Textile": _IND + " - textile and leather - energy use",
        "Other": _IND + " - not elsewhere specified - energy use",
    }),
    "agriculture": ("Agriculture", {
        "Total": _OTHER + " - agriculture and forestry - energy use",
    }),
    "transport": ("Transport", {
        "Rail": _TRA + " - rail - energy use",
        "Road": _TRA + " - road - energy use",
        "Domestic aviation": _TRA + " - domestic aviation - energy use",
        "Domestic shipping": _TRA + " - domestic navigation - energy use",
        "Pipelines": _TRA + " - pipeline transport - energy use",
        "Other": _TRA + " - not elsewhere specified - energy use",
    }),
    "total": ("AT", {"Total": "Available for final consumption"}),
}

#: The provisional Statistik Austria balance: German fuel columns per category,
#: and the row to read per sector. Terajoule in the file, TWh on the charts.
_TJ_TO_TWH = 3600

_PRELIMINARY_FUELS = {
    "Natural gas": ["Gas"],
    "Oil": ["Öl"],
    "Coal": ["Kohle"],
    "Biomass": ["Brennholz", "feste Biogene Brenn- u. Treibstoffe", "Biogase",
                "Bioethanol (Beimengung)", "Biodiesel (Beimengung)"],
    "Renewable electricity": ["Wasserkraft", "Windkraft", "Fotovoltaik"],
    "Ambient heat": ["Umgebungs-wärme", "Geothermie", "Solarthermie"],
    "Electricity": ["Elektrische Energie"],
    "District Heat": ["Fernwärme"],
}

_PRELIMINARY_OTHER_GROSS = ["Elektrische Energie", "Fernwärme", "Brennbare Abfälle",
                            "Gichtgas", "Kokereigas", "Raffinerie-Restgas"]
_PRELIMINARY_OTHER_FINAL = ["Brennbare Abfälle", "Geothermie", "Solarthermie",
                            "Umgebungs-wärme", "Gichtgas", "Kokereigas",
                            "Raffinerie-Restgas"]

_PRELIMINARY_ROWS = {
    "buildings": ["Öffentliche und Private Dienstleistungen", "Private Haushalte"],
    "transport": ["Verkehr"],
    "industry": ["Produzierender Bereich"],
    "agriculture": ["Landwirtschaft"],
    "total": ["Energetischer Endverbrauch"],
}
_PRELIMINARY_GROSS_ROW = "Bruttoinlandsverbrauch"
_PRELIMINARY_INDEX = "Bilanzaggregat \\ Energieträger\n"


def plot():
    logger.info("Charts: energy balances ...")
    source = _gross_inland_consumption()
    for stem in SECTORS:
        _final_energy_use(stem, source)


# ---------------------------------------------------------------------------
# Gross inland consumption
# ---------------------------------------------------------------------------

def _gross_inland_consumption():
    data = energy_balance.read(siecs=GROSS_FUELS, bals=["Gross inland consumption"])
    data = S.select(data, list(GROSS_FUELS))

    source = BALANCE_SOURCE
    preliminary = _preliminary_year()
    if preliminary is not None and S.times(data, "Oil")[-1].year == preliminary - 1:
        data = _append_preliminary(data, preliminary, _PRELIMINARY_GROSS_ROW,
                                   _PRELIMINARY_OTHER_GROSS)
        source = PRELIMINARY_SOURCE

    chart("gross_inland_consumption_share",
          title="AT gross inland consumption: shares",
          unit="Share [%]",
          data=S.shares(data),
          source=source,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("gross_inland_consumption_absolute",
          title="AT gross inland consumption: absolute",
          unit="Energy (TWh)",
          data=data,
          source=source,
          time_res="yearly",
          view="toggle", initial="bar")

    return source


# ---------------------------------------------------------------------------
# Final energy use per sector
# ---------------------------------------------------------------------------

def _final_energy_use(stem, source):
    label, aggregates = SECTORS[stem]

    groups = {}
    for entry, aggregate in aggregates.items():
        block = energy_balance.read(siecs=FINAL_FUELS, bals=[aggregate])
        groups[entry] = S.select(block, list(FINAL_FUELS))

    preliminary = _preliminary_year()

    if "Total" not in groups:
        # The selector's Total is the sum of the sub-branches, not a separate
        # balance aggregate -- eurostat does not publish one per sector.
        totals = []
        for fuel in FINAL_FUELS:
            summed = None
            for entry in groups:
                column = S.values(groups[entry], fuel)
                summed = column if summed is None else summed + column
            totals.append((fuel, S.series(S.times(groups[list(groups)[0]], fuel), summed)))
        # Total first: it is the selector's default and the reader's entry point.
        groups = dict([("Total", S.wrap(totals))] + list(groups.items()))

    if preliminary is not None and S.times(groups["Total"], "Oil")[-1].year == preliminary - 1:
        # Only the Total entry gains the provisional year: the provisional
        # balance is published per broad sector, with no sub-branch split, so
        # there is nothing to append to the other selector entries. That does
        # leave the Total one year longer than its own parts, which is the
        # inherited behaviour and is why the source line names the second source.
        groups["Total"] = _append_preliminary(
            groups["Total"], preliminary, stem, _PRELIMINARY_OTHER_FINAL)

    if stem == "total":
        _one_sector_chart(stem, label, groups["Total"], source)
        return

    absolute = {entry: groups[entry] for entry in groups}
    shares = {entry: S.shares(groups[entry]) for entry in groups}

    chart("%s_final_energy_use_share" % stem,
          title="AT %s: final energy use - shares" % label,
          unit="Share [%]",
          data=shares,
          source=source,
          time_res="yearly",
          view="groups")

    chart("%s_final_energy_use" % stem,
          title="AT %s: final energy use" % label,
          unit="Energy (TWh)",
          data=absolute,
          source=source,
          time_res="yearly",
          view="groups")


def _one_sector_chart(stem, label, data, source):
    """The whole-country charts: one series set, so a toggle rather than groups."""
    chart("%s_final_energy_use_share" % stem,
          title="AT final energy use: shares",
          unit="Share [%]",
          data=S.shares(data),
          source=source,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("%s_final_energy_use" % stem,
          title="AT final energy use: absolute",
          unit="Energy (TWh)",
          data=data,
          source=source,
          time_res="yearly",
          view="toggle", initial="bar")


# ---------------------------------------------------------------------------
# The provisional Statistik Austria balance
# ---------------------------------------------------------------------------

def _preliminary_file():
    """The newest provisional balance drop, and the year it covers."""
    directory = DATA_RAW + "/statistik_austria"
    best = None
    for entry in os.listdir(directory):
        m = re.match(r"vorlaeufigeEnergiebilanzenOesterreich(\d{4})inTerajoule",
                     entry)
        if m:
            year = int(m.group(1))
            if best is None or year > best[0]:
                best = (year, directory + "/" + entry)
    return best


def _preliminary_year():
    found = _preliminary_file()
    return found[0] if found else None


def _append_preliminary(data, year, sector, other_fuels):
    """Append one year from the provisional national balance.

    `sector` is either a key of _PRELIMINARY_ROWS (a sector's one or two rows) or
    a literal row name, which is how the gross-inland-consumption chart asks for
    its own aggregate.
    """
    _, path = _preliminary_file()
    table = pd.read_excel(path, skiprows=1)
    aggregate_rows = _PRELIMINARY_ROWS.get(sector, [sector])

    axis = list(pd.date_range(start=S.times(data, "Oil")[0],
                              end=datetime(year, 1, 1), freq="YS"))

    pairs = []
    for fuel in data["data"]:
        columns = _PRELIMINARY_FUELS.get(fuel, other_fuels)
        value = 0.0
        for aggregate in aggregate_rows:
            for column in columns:
                value += float(
                    table[column][table[_PRELIMINARY_INDEX] == aggregate].iloc[0]
                ) / _TJ_TO_TWH
        pairs.append((fuel, S.series(axis, np.append(S.values(data, fuel), value))))
    return S.wrap(pairs)
