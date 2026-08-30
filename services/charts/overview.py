# -*- coding: utf-8 -*-
"""The front page's emissions charts, and every sector's headline chart.

Three things happen here, and they happen in this order because each depends on
the last:

1. The national total by sector, from the Umweltbundesamt Klimadashboard. This is
   the anchor figure for the whole site.
2. One sub-sector breakdown per sector, from the EEA inventory, each scaled to
   match its UBA sector total (see `sources/eea.py` for why, and for what
   "Other" really is).
3. The with-LULUCF total, which can only be built after step 2 -- LULUCF is the
   one sector the Klimadashboard does not report, so its series comes out of the
   inventory breakdown and is then appended to the national total.

**LULUCF is drawn first in the with-LULUCF chart, and that is not cosmetic.** It
is the only negative series, and a stacked area with negatives has to have them
adjacent to the axis to stack correctly; putting the sink in the middle of the
order folds it into the positive stack.
"""

import numpy as np
from loguru import logger

from sources import umweltbundesamt
from sources import eea

import series as S

from .spec import chart

#: The seven sectors and the chart-id stem of each one's breakdown chart. Order
#: is the palette order for the national charts.
SECTOR_CHARTS = {
    "Buildings": "buildings",
    "Energy & Industry": "energy_industry",
    "Agriculture": "agriculture",
    "Waste": "waste",
    "Transport": "transport",
    "Fluorinated Gases": "fluorinated_gases",
    "LULUCF": "lulucf",
}

KLIMADASHBOARD = "Umweltbundesamt (Klimadashboard)"
EEA_AND_UBA = "EEA for sectoral, UBA (Klimadashboard) for total emissions"
BREAKDOWN_NOTE = "Scaled to UBA totals, later years carried forward."

UNIT = "Emissions (Mt<sub>CO2e</sub>)"


def plot():
    logger.info("Charts: emissions by sector ...")

    national = S.total(umweltbundesamt.sectoral_emissions())

    chart("co2_emissions_sectors",
          title="AT GHG emissions by sectors (without LULUCF)",
          unit=UNIT,
          data=national,
          source=KLIMADASHBOARD,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("co2_emissions_sectors_shares",
          title="AT GHG emission shares by sectors (without LULUCF)",
          unit="Emission share (%)",
          data=S.shares(national),
          source=KLIMADASHBOARD,
          time_res="yearly",
          view="toggle", initial="bar")

    lulucf = None
    for sector, stem in SECTOR_CHARTS.items():
        breakdown = eea.sub_sectors(sector)

        if sector == "LULUCF":
            # The sink: negative values, so area_neg rather than the toggle, and
            # no UBA anchor to scale against.
            chart("lulucf_emissions_sectors",
                  title="AT LULUCF GHG emissions by sub-sectors",
                  unit=UNIT,
                  data=breakdown,
                  source="EEA",
                  time_res="yearly",
                  view="area_neg")
            lulucf = breakdown["data"]["Total"]
        else:
            chart("%s_emissions_sectors" % stem,
                  title="AT %s GHG emissions by sub-sectors" % sector,
                  unit=UNIT,
                  data=breakdown,
                  source=EEA_AND_UBA,
                  note=BREAKDOWN_NOTE,
                  time_res="yearly",
                  view="toggle", initial="bar")

    chart("co2_emissions_sectors_with_lulucf",
          title="AT GHG emissions by sectors (with LULUCF)",
          unit=UNIT,
          data=_with_lulucf(national, lulucf),
          source=KLIMADASHBOARD,
          time_res="yearly",
          view="area_neg")


def _with_lulucf(national, lulucf):
    """The national total with the carbon sink folded in.

    Where the inventory ends before the Klimadashboard -- it trailed by a year
    until the 2025 EEA export caught up -- the whole chart is truncated to the
    years LULUCF covers, rather than showing a total that silently stops
    including the sink for its last year.

    LULUCF goes first in the series order: see the module docstring.
    """
    years = len(lulucf["x"])
    truncated = S.wrap([(label, S.series(S.times(national, label)[:years],
                                         S.values(national, label)[:years]))
                        for label in national["data"]])

    combined = S.wrap([("LULUCF", S.series(lulucf["x"], lulucf["y"]))]
                      + [(label, truncated["data"][label])
                         for label in truncated["data"] if label != "Total"])
    # Recomputed rather than added to the existing total, so the total is always
    # the sum of exactly the series drawn beneath it.
    return S.total(combined)
