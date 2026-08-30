# -*- coding: utf-8 -*-
"""The Waste page: long-term carbon storage in disposal sites.

The sector's emissions breakdown is in `charts/overview.py`. This is the one
chart specific to waste, and the one series on the site read straight out of a
single CRF sector code.

It is a *negative* emission in the inventory -- carbon that stays in a landfill
rather than reaching the atmosphere -- reported here as the positive quantity
stored, which is why the chart reads as a stock going up rather than as a sink.
"""

from datetime import datetime

import numpy as np
import pandas as pd
from loguru import logger

from sources import eea

import series as S

from .spec import chart

SECTOR = "5.F.1 - Long-term Storage of C in Waste Disposal Sites"


def plot():
    logger.info("Charts: waste ...")

    years, emissions = eea.sector_series(SECTOR)
    times = pd.date_range(start=datetime(years[0], 1, 1),
                          end=datetime(years[-1], 1, 1), freq="YS")

    chart("long_term_storage_c_disposal",
          title="AT long-term storage of C in waste disposal sites",
          unit="Emissions (Mt<sub>CO2e</sub>)",
          # t CO2e in the inventory, Mt on the chart.
          data=S.wrap([("Austria", S.series(times, np.array(emissions) / 1e6))]),
          source="EEA greenhouse gases — data viewer (sector: 5.F.1)",
          time_res="yearly",
          view="toggle", initial="bar")
