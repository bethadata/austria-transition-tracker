# -*- coding: utf-8 -*-
"""EEA / UNFCCC inventory: emissions broken down into sub-sectors.

This is where every "GHG emissions by sub-sectors" chart comes from. The EEA
greenhouse-gas data viewer export holds the full CRF sector tree; the SECTORS
table below says which CRF codes make up each sub-sector a reader is shown, and
under what name.

**The two things worth understanding before changing anything here.**

*The breakdown is scaled to the Umweltbundesamt total, not published alongside
it.* The EEA inventory and the Klimadashboard disagree, by a little and for
legitimate reasons (different vintages, different boundary conventions). The
site shows the UBA figure as the sector total because that is the Austrian
headline number, so the difference has to go somewhere: it becomes the "Other"
sub-sector. That makes "Other" a residual, not a measurement -- which is exactly
what the chart note says.

*The newest year is extrapolated, not reported.* UBA publishes a sector total
roughly a year before the inventory publishes the breakdown. Rather than ending
the stack a year before the total line, each sub-sector is carried forward at its
previous year's share of the total. The chart note says this too.

Waste carries one further hack, inherited and marked TODO since 2024: UBA's waste
figure includes waste-to-energy, which the inventory books under energy, so the
whole EEA-vs-UBA difference is attributed to waste incineration rather than to
"Other". The consequence is that the waste stack does not add up to its own total
line. Fixing it properly means removing waste CHP from the energy sector first.

The export filename carries its year (`eea_Austria_2025.xlsx`) and the newest one
on disk wins. It used to be typed into the module, so a new inventory meant
editing Python, and the previous year's file sat beside it with nothing saying
which was live. The prefix changed from `unfcc_` to `eea_` with the 2025 vintage;
both are matched, so the exports already on disk under the old name still take
part in the comparison rather than being stranded next to the new one. This
module and its directory were named `unfcc` for the same reason -- the name came
from the inventory's reporting framework rather than from its publisher -- and
were renamed to match the source they actually read.
"""

import glob
import re
from datetime import datetime

import numpy as np
import pandas as pd

from paths import DATA_RAW

from . import umweltbundesamt

EEA_DIR = DATA_RAW + "/eea"

#: The export was named `unfcc_Austria_<year>.xlsx` up to the 2024 vintage and
#: `eea_Austria_<year>.xlsx` from 2025 on. Matching both means the newest year
#: still wins on the year alone, whichever prefix it happens to carry -- matching
#: only the new one would have silently promoted nothing on a year where only an
#: old-style file exists.
EXPORT_RE = re.compile(r"(?:unfcc|eea)_Austria_(\d{4})\.xlsx$", re.IGNORECASE)

ALL_GASES = "All greenhouse gases - (CO2 equivalent)"

#: sector -> {sub-sector display name: [CRF codes to sum]}. Insertion order is
#: the palette order. A sub-sector made of several codes is one the source splits
#: and the chart does not (industry energy use plus industry process emissions).
SECTORS = {
    "Agriculture": {
        "Fermentation (cows)": ["3.A - Enteric Fermentation"],
        "Organic fertilizer (manure) management": ["3.B - Manure Management"],
        "Soil fertilization": ["3.D - Agricultural Soils"],
        "Energy use": ["1.A.4.c - Agriculture/Forestry/Fishing"],
    },
    "Transport": {
        "Passenger cars": ["1.A.3.b.i - Cars"],
        "Light duty vehilces": ["1.A.3.b.ii - Light duty trucks"],
        "Heavy duty vehicles and buses": ["1.A.3.b.iii - Heavy duty trucks and buses"],
        "Mopeds and Motorcycles": ["1.A.3.b.iv - Motorcycles"],
    },
    "Waste": {
        "Solid waste disposal (landfills)": ["5.A - Solid Waste Disposal"],
        "Biological waste treatment": ["5.B - Biological Treatment of Solid Waste"],
        "Waste water treatment": ["5.D - Wastewater Treatment and Discharge"],
        "Waste incineration incl. for power/heat generation":
            ["5.C - Incineration and Open Burning of Waste"],
    },
    "Energy & Industry": {
        "Electricity and heat generation": ["1.A.1.a - Public Electricity and Heat Production"],
        "Iron and steel": ["1.A.2.a - Iron and Steel", "2.C.1 - Iron and Steel Production"],
        "Cement / Minerals": ["2.A - Mineral Industry", "1.A.2.f - Non-metallic minerals"],
        "Chemical industry": ["1.A.2.c - Chemicals", "2.B - Chemical Industry"],
        "Pulp / Paper": ["1.A.2.d - Pulp, Paper and Print"],
        "Petroleum refining": ["1.A.1.b - Petroleum Refining"],
        "Construction": ["1.A.2.g - Other Manufacturing Industries and Constructions"],
    },
    "Buildings": {
        "Residential / private": ["1.A.4.b - Residential"],
        "Commercial / public": ["1.A.4.a - Commercial/Institutional"],
    },
    "LULUCF": {
        "Forests": ["4.A - Forest Land"],
        "Cropland": ["4.B - Cropland"],
        "Grassland": ["4.C - Grassland"],
        "Wetlands": ["4.D - Wetlands"],
        "Settlements": ["4.E - Settlements"],
        "Other land": ["4.F - Other Land"],
        "Wood products": ["4.G - Harvested Wood Products"],
    },
    "Fluorinated Gases": {
        "Refrigeration and Air conditioning": ["2.F.1 - Refrigeration and Air conditioning"],
        "Electronics industry": ["2.E - Electronics Industry"],
        "Magnesium industry": ["2.C.4 - Magnesium Production"],
        "Aluminium industry": ["2.C.3 - Aluminium Production"],
    },
}

#: LULUCF is the one sector the Klimadashboard does not report, so its total is
#: the sum of its own sub-sectors rather than an external anchor -- and it is the
#: only sector that goes negative, being a sink.
SELF_TOTALLING = ("LULUCF",)

_table = None


def _load():
    """The newest inventory export, forward-filled and cached for the run."""
    global _table
    if _table is not None:
        return _table
    matches = []
    for path in glob.glob(EEA_DIR + "/*.xlsx"):
        m = EXPORT_RE.search(path.replace("\\", "/"))
        if m:
            matches.append((int(m.group(1)), path))
    if not matches:
        raise FileNotFoundError(
            "no eea_Austria_<year>.xlsx in %s -- it is a manual download." % EEA_DIR)
    table = pd.read_excel(max(matches)[1])
    # The export leaves the sector, gas and country cells blank on continuation
    # rows, so every filter below would miss all but the first row of a block.
    table["Sector Name"] = table["Sector Name"].ffill()
    table["Gas"] = table["Gas"].ffill()
    table["Country"] = table["Country"].ffill()
    _table = table.fillna(0)
    return _table


def sector_series(sector, gas=ALL_GASES):
    """(years, t CO2e) for one CRF sector code."""
    table = _load()
    rows = table[(table["Sector Name"] == sector)
                 & (table["Country"] == "Austria")
                 & (table["Gas"] == gas)]
    return np.array(rows["Jahr von Date"]), np.array(rows["t CO2 equivalent"])


def sub_sectors(sector):
    """A sector's sub-sector breakdown in Mt CO2e, with Other and Total.

    See the module docstring for what Other and the newest year actually are.
    """
    if sector not in SECTORS:
        raise KeyError("no sub-sector map for %r" % sector)

    data = {"data": {}}
    years = None
    for name, codes in SECTORS[sector].items():
        summed = None
        for code in codes:
            years, emissions = sector_series(code)
            summed = emissions if summed is None else summed + emissions
        times = pd.date_range(start=datetime(years[0], 1, 1),
                              end=datetime(years[-1], 1, 1), freq="YS")
        data["data"][name] = {"x": times, "y": np.array(summed) / 1e6}

    stack = np.zeros(len(times))
    for name in data["data"]:
        stack += np.array(data["data"][name]["y"])

    if sector in SELF_TOTALLING:
        data["data"]["Total"] = {"x": times, "y": stack}
        return data

    uba = umweltbundesamt.sectoral_emissions()["data"][sector]
    # Align the two series on the year rather than on a fixed offset. This used
    # to be `uba["y"][:-1]`, which encoded "UBA is exactly one year ahead of the
    # inventory" -- true until the 2025 EEA export, which caught up to UBA's own
    # newest year. Off by one in that direction raises; off by one the other way
    # would have subtracted every sector's wrong year and shown up as nothing
    # more than an "Other" residual of the wrong size.
    uba_by_year = {pd.Timestamp(t).year: v for t, v in zip(uba["x"], uba["y"])}
    inventory_years = [t.year for t in times]
    missing = [y for y in inventory_years if y not in uba_by_year]
    if missing:
        raise ValueError("UBA has no %s figure for %s -- the inventory reaches "
                         "further back than the Klimadashboard export does"
                         % (sector, missing))
    difference = np.array([uba_by_year[y] for y in inventory_years]) - stack

    if sector == "Waste":
        # See the module docstring: the difference is attributed to incineration
        # rather than to Other, which overwrites the inventory's own 5.C series.
        # TODO: remove waste CHP from the energy sector and drop this.
        data["data"]["Waste incineration incl. for power/heat generation"] = {
            "x": times, "y": np.array(difference)}
        data["data"]["Other"] = {"x": times, "y": np.zeros(len(times))}
    else:
        data["data"]["Other"] = {"x": times, "y": np.array(difference)}

    ahead = [y for y in uba_by_year if y > inventory_years[-1]]
    if ahead:
        # Carry every sub-sector forward at its last known share of the total, so
        # the stack reaches the same year as the total line. Written as a loop
        # over the years UBA is ahead by rather than over a single year: the gap
        # has been one year, then none, and there is no reason it cannot be two.
        anchor = stack[-1] + difference[-1]
        for name in data["data"]:
            share = data["data"][name]["y"][-1] / anchor
            data["data"][name]["x"] = list(times) + [
                pd.Timestamp(datetime(y, 1, 1)) for y in sorted(ahead)]
            data["data"][name]["y"] = np.append(
                data["data"][name]["y"],
                [uba_by_year[y] * share for y in sorted(ahead)])

    data["data"]["Total"] = uba
    return data
