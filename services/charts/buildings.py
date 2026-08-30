# -*- coding: utf-8 -*-
"""The Buildings page: heating oil, the heating-system mix, and cooling demand.

The sector's emissions breakdown and its final energy use come from
`charts/overview.py` and `charts/energy_balance.py`; this module owns the four
charts specific to buildings.
"""

from loguru import logger

from sources import eurostat
from sources import statistik_austria

from .spec import chart


def plot():
    logger.info("Charts: buildings ...")

    chart("heating_oil_consumption",
          title="AT Heating oil: monthly consumption",
          unit="Oil (thousand tons)",
          data=eurostat.monthly(
              name="oil", code="NRG_CB_OILM", start_year=2010,
              options={"unit": "THS_T",
                       "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                       "siec": "Heating and other gasoil [O46712]"},
              unit="THS_T", movmean=12),
          source="eurostat (NRG_CB_OILM)",
          time_res="monthly",
          view="line")

    # The survey is biennial, so consecutive year pairs carry the same figure --
    # see sources/statistik_austria.py.
    shares, absolute = statistik_austria.heating_systems()

    chart("share_heating_systems",
          title="AT Heating system shares: main types",
          unit="Share [%]",
          data=shares,
          source="Statistik Austria",
          time_res="yearly",
          view="toggle", initial="bar")

    chart("number_heating_systems",
          title="AT Heating system absolute numbers: main types",
          unit="Number",
          data=absolute,
          source="Statistik Austria",
          time_res="yearly",
          view="toggle", initial="bar")

    # The one chart on this page whose points are not on a regular grid: the
    # survey waves behind it are two years, two years, then one. Read off the
    # file rather than assumed -- see sources/statistik_austria.py.
    chart("number_air_conditioners",
          title="AT Air conditioners installed in households",
          unit="Number",
          data=statistik_austria.air_conditioners(),
          source="Statistik Austria",
          time_res="yearly",
          view="toggle", initial="bar",
          note="Mikrozensus sample; error bars: coefficient of variation.")
