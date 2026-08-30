# -*- coding: utf-8 -*-
"""Land use: the area side of the LULUCF page.

The emissions side is in `charts/overview.py`, with the other six sectors'
breakdowns.

This module had no `plot()` at all until 2026-08-25: it drew at *import* time, so
it could not be called and the orchestrator had to import it in the right order
to make its two charts happen. That is also how it came to be serving frozen
data for a while -- an import that is really a function call is invisible to
anything looking for what builds a chart.
"""

from loguru import logger

from sources import national_inventory

import series as S

from .spec import chart

NIR = "National Inventory Report"

#: The report gives areas for 1990, 1995, 2000, 2005 and then every year from
#: 2010, so the early part of both charts is five-yearly. Said out loud because
#: the gap is invisible on a stacked area and reads as a slow decade on bars.
NOTE = ("Areas are reported for 1990, 1995, 2000, 2005 and annually from "
        "2010; the axis is five-yearly before 2010.")


def plot():
    logger.info("Charts: land use ...")

    areas = national_inventory.land_uses()

    chart("land_use_abs",
          title="AT Land use: absolute area",
          unit="Area (kHa)",
          data=areas,
          source=NIR,
          note=NOTE,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("land_use_rel",
          title="AT Land use: shares",
          unit="Share (%)",
          # No Total series here, so shares() takes the total from the stack --
          # which is what a land-use share is: the six uses are the whole country.
          data=S.shares(areas),
          source=NIR,
          note=NOTE,
          time_res="yearly",
          view="toggle", initial="bar")
