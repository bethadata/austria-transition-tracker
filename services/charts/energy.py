# -*- coding: utf-8 -*-
"""District heat and electricity: the Energy page's generation charts.

Six electricity charts and two district-heat ones, and the interesting part is
that the electricity ones are **spliced from two sources**. eurostat's energy
balance is authoritative but yearly and about eighteen months late; E-Control
publishes monthly and within weeks. So every year E-Control covers is taken from
E-Control and the rest from eurostat, which is why the yearly charts run to the
current year and why their source line names both with a cut-over date.

The splice is by whole years, never partial: an E-Control year replaces the
eurostat year entirely, so the two are never mixed inside one bar. The newest
year is therefore a part-year figure, which the source line says.

E-Control reports no waste-fired generation at all, so the Waste series is empty
for every spliced year. The charts carry a note saying so rather than dropping
the series -- dropping it would change the colour order against the monthly
chart beside it.
"""

import numpy as np
import pandas as pd
from loguru import logger

from sources import econtrol
from sources import energy_balance

import series as S

from .spec import chart

BALANCE_SOURCE = "eurostat energy balances (nrg_bal_c)"
ECONTROL_SOURCE = "E-control (MoMeGes)"
WASTE_NOTE = "E-Control data contains no waste data."

#: District heat: the reader's fuel categories, and the eurostat fuels behind
#: them. Order is palette order.
HEAT_FUELS = {
    "Natural gas": ["Natural gas"],
    "Oil": ["Oil and petroleum products (excluding biofuel portion)"],
    "Biomass": ["Primary solid biofuels"],
    "Coal": ["Solid fossil fuels"],
    "Waste non-renewable": ["Non-renewable waste"],
    "Waste renewable": ["Renewable municipal waste"],
    "Total": ["Total"],
}

#: Electricity, same idea. Renewables first: this is the order the charts are
#: read in, low-carbon at the bottom of the stack.
POWER_FUELS = {
    "PV": ["Solar photovoltaic"],
    "Wind": ["Wind"],
    "Hydro": ["Hydro"],
    "Biomass": ["Bioenergy"],
    "Natural gas": ["Natural gas"],
    "Coal": ["Solid fossil fuels"],
    "Waste non-renewable": ["Non-renewable waste"],
    "Waste renewable": ["Renewable municipal waste"],
    "Total": ["Total"],
}

#: The generation series, in chart order -- i.e. POWER_FUELS with the two waste
#: series merged and the residual added.
POWER_SERIES = ["PV", "Wind", "Hydro", "Biomass", "Natural gas", "Coal",
                "Waste", "Other"]


def plot():
    logger.info("Charts: energy ...")
    _district_heat()
    _electricity()


def _district_heat():
    raw = energy_balance.read(siecs=HEAT_FUELS, bals=["Gross heat production"])

    heat = S.combine(raw, "Waste", ["Waste non-renewable", "Waste renewable"])
    heat = S.residual(heat, "Other", of="Total")
    heat = S.select(heat, ["Natural gas", "Oil", "Coal", "Biomass", "Waste", "Other"])

    chart("dh_energy_use",
          title="AT District heat generation (gross): energy",
          unit="Energy (TWh)",
          data=heat,
          source=BALANCE_SOURCE,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("dh_energy_use_share",
          title="AT District heat generation (gross): energy shares",
          unit="Share [%]",
          data=S.shares(heat, of=S.values(raw, "Total")),
          source=BALANCE_SOURCE,
          time_res="yearly",
          view="toggle", initial="bar")


def _electricity():
    raw = energy_balance.read(siecs=POWER_FUELS, bals=["Gross electricity production"])

    # Domestic consumption is not a fuel: it is the yardstick the "share of
    # consumption" charts divide by, and the reason it is three balance
    # aggregates is that consumption here means everything electricity is used
    # for, own use and grid losses included.
    demand = energy_balance.read(
        siecs={"Domestic consumption": ["Electricity"]},
        bals=["Available for final consumption",
              "Energy sector - energy use",
              "Distribution losses"])

    yearly = S.combine(raw, "Waste", ["Waste non-renewable", "Waste renewable"])
    yearly = S.residual(yearly, "Other", of="Total")
    yearly = S.select(yearly, POWER_SERIES)
    yearly["data"]["Domestic consumption"] = demand["data"]["Domestic consumption"]

    monthly = econtrol.monthly_generation()
    spliced, last_month, last_year = _splice_econtrol(yearly, monthly)

    source = ("%s up to 2015, E-control from 2015 up to %i/%i"
              % (BALANCE_SOURCE, last_month, last_year))

    chart("elec_energy_use",
          title="AT Yearly electricity production (gross): energy",
          unit="Energy (TWh)",
          data=spliced,
          source=source, note=WASTE_NOTE,
          time_res="yearly",
          view="toggle", initial="bar")

    generation = S.select(spliced, POWER_SERIES)

    chart("elec_energy_use_share",
          title="AT Yearly electricity production (gross): shares of production",
          unit="Share [%]",
          data=S.shares(generation),
          source=source, note=WASTE_NOTE,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("elec_energy_use_share_cons",
          title="AT Yearly electricity production (gross): shares of consumption",
          unit="Share [%]",
          # Divided by consumption rather than by production, so the series sum
          # to more than 100% in a net-export year and less in a net-import one.
          # That is the point of the chart.
          data=S.shares(generation, of=S.values(spliced, "Domestic consumption")),
          source=source, note=WASTE_NOTE,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("elec_prod_monthly",
          title="AT Monthly electricity production (gross): energy",
          unit="Energy (TWh)",
          data=monthly,
          source=ECONTROL_SOURCE,
          time_res="monthly",
          view="toggle", initial="area")

    monthly_generation = S.select(monthly, POWER_SERIES)

    chart("elec_prod_monthly_share",
          title="AT Monthly electricity production (gross): shares of production",
          unit="Share [%]",
          data=S.shares(monthly_generation),
          source=ECONTROL_SOURCE,
          time_res="monthly",
          view="toggle", initial="area")

    chart("elec_prod_monthly_share_cons",
          title="AT Monthly electricity production (gross): shares of consumption",
          unit="Share [%]",
          data=S.shares(monthly_generation,
                        of=S.values(monthly, "Domestic consumption")),
          source=ECONTROL_SOURCE,
          time_res="monthly",
          view="toggle", initial="area")


def _splice_econtrol(yearly, monthly):
    """Replace every year E-Control covers with E-Control's own annual sum.

    Whole years only. The last one is partial -- E-Control's newest month --
    which is what the source line on each chart has to say, so the month and year
    come back with the data.
    """
    covered = []
    for t in monthly["data"]["PV"]["x"]:
        if t.year not in covered:
            covered.append(t.year)
    last_month = max(t.month for t in monthly["data"]["PV"]["x"]
                     if t.year == covered[-1])

    first_year = S.times(yearly, "Other")[0].year
    axis = list(pd.date_range(start=pd.Timestamp(year=first_year, month=1, day=1),
                              end=pd.Timestamp(year=covered[-1], month=1, day=1),
                              freq="YS"))

    pairs = []
    for label in yearly["data"]:
        by_year = dict(zip(S.times(yearly, label), S.values(yearly, label)))
        stamps = pd.to_datetime(monthly["data"][label]["x"])
        for year in covered:
            by_year[pd.Timestamp(year=year, month=1, day=1)] = float(
                np.sum(np.asarray(monthly["data"][label]["y"])[stamps.year == year]))
        pairs.append((label, S.series(axis, [by_year[t] for t in axis])))

    return S.wrap(pairs), last_month, covered[-1]
