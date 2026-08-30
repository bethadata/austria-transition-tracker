# -*- coding: utf-8 -*-
"""Umweltbundesamt sectoral emissions -- the anchor every emissions chart hangs off.

One manual download: the Klimadashboard's "Mio. t CO2-Aequivalent nach Jahr und
Sektor" export. It is the authoritative Austrian sectoral total, and it is what
the two inventory-derived breakdowns (`sources/eea.py`) are scaled to match, so
a change here moves every emissions chart on the site.

The file is a manual drop, not a download: there is no API. It is tracked in git
for that reason -- git is its only backup.
"""

from datetime import datetime

import numpy as np
import pandas as pd

from paths import DATA_RAW

PATH = DATA_RAW + "/umweltbundesamt/Mio. t CO₂-Äquivalent nach Jahr und Sektor.xlsx"

#: The six sectors the Klimadashboard reports, in the order the charts use them,
#: mapped from the German column values. LULUCF is deliberately absent: the
#: Klimadashboard does not carry it, which is why the with-LULUCF chart takes
#: that one series from the EEA inventory instead.
SECTORS = {
    "Transport": "Verkehr (inkl. nationalem Flugverkehr)",
    "Energy & Industry": "Energie & Industrie mit Emissionshandel",
    "Agriculture": "Landwirtschaft",
    "Buildings": "Gebäude",
    "Waste": "Abfallwirtschaft",
    "Fluorinated Gases": "F-Gase",
}


def sectoral_emissions():
    """Yearly Mt CO2e per sector, 1990 to the newest year in the file."""
    raw = pd.read_excel(PATH, decimal=",", skiprows=2)

    last_year = None
    for year in range(1990, 2101):
        if year in list(raw["Jahr"]):
            last_year = year

    times = pd.date_range(start=datetime(1990, 1, 1),
                          end=datetime(last_year, 1, 1), freq="YS")

    data = {"data": {}}
    for sector, german in SECTORS.items():
        data["data"][sector] = {"x": [], "y": []}
        for t in times:
            row = raw[np.logical_and(raw["Sektor"] == german, raw["Jahr"] == t.year)]
            data["data"][sector]["y"].append(
                float(row.iloc[0]["Summe von Mio. t CO₂-Äquivalent"]))
            data["data"][sector]["x"].append(t)
    return data
