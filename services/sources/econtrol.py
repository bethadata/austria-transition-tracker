# -*- coding: utf-8 -*-
"""E-Control MoMeGes: monthly Austrian electricity generation by fuel.

The only monthly electricity source there is for Austria, and the reason the
electricity charts run to the current month rather than stopping at eurostat's
last complete year. `download/econtrol.py` fetches the CSV; this reads it.

**The column codes are the whole problem.** E-Control identifies series by
opaque ids like `#89097m`, with no machine-readable legend -- the CSV's header
rows are a German prose description. The mapping below was established by hand
against those descriptions and is the single most fragile thing in the pipeline:
if E-Control renumbers a series, this reads a different fuel under the old name
and nothing about the output looks wrong. The commented notes on each code are
therefore load-bearing documentation, not clutter.

`Waste` maps to no code deliberately: E-Control does not report it, so the
electricity charts carry a note saying so. It stays in the mapping as an empty
list rather than being dropped, because the chart's series list -- and therefore
its colour order -- has to match the yearly eurostat chart beside it.

`skiprows` skips E-Control's fourteen-line preamble; row 2 is the header.
"""

import os

import numpy as np
import pandas as pd

from paths import DATA_RAW

PATH = DATA_RAW + "/e_control/el_dataset_mn.csv"

#: The first month E-Control data is used for. Before this, the eurostat energy
#: balance is the source, and the charts splice the two.
FIRST_YEAR = 2015

#: Fuel -> E-Control series codes to sum. Order is palette order and matches the
#: yearly electricity chart.
FUEL_CODES = {
    "PV": ["#248357"],
    "Wind": ["#89101"],
    "Hydro": ["#999003m"],
    "Biomass": ["#99105m", "#156858m"],
    "Natural gas": ["#89097m"],
    "Coal": ["#89093m"],
    # Not reported by E-Control. Kept so the series order matches the yearly
    # chart; the charts note the absence.
    "Waste": [],
    "Other": ["#89096m",   # derivatives of solid fossil fuels
              "#89095m",   # derivatives of oil
              "#99106m",   # "sonstige" fuels, probably mostly waste
              "#89103m"],  # unidentified
    # #113482m is geothermal: excluded, both for a data error in the series and
    # because the quantity is negligible for Austria.
    "Domestic consumption": ["#89110m"],
}

#: MWh in the file, TWh on the charts.
_MWH_TO_TWH = 1e6


def monthly_generation():
    """Monthly generation and domestic consumption in TWh, FIRST_YEAR onwards."""
    if not os.path.exists(PATH):
        raise FileNotFoundError(
            "%s is missing -- run `python scrape.py` to download it." % PATH)
    with open(PATH, "r", encoding="ISO-8859-1") as fp:
        table = pd.read_csv(fp, skiprows=[0, 1] + list(range(3, 14)),
                            encoding="ISO-8859-1", sep=";", header=[0],
                            engine="python", decimal=",")

    stamps = pd.to_datetime(table["TS_ID"])
    keep = stamps >= pd.Timestamp(year=FIRST_YEAR, month=1, day=1)
    times = list(pd.to_datetime(stamps[keep]))

    data = {"data": {}}
    for fuel, codes in FUEL_CODES.items():
        summed = np.zeros(len(times))
        for code in codes:
            summed += np.array(table[code][keep])
        data["data"][fuel] = {"x": times, "y": summed / _MWH_TO_TWH}
    return data
