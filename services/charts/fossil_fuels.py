# -*- coding: utf-8 -*-
"""Fossil fuel consumption and the emissions computed from it.

The Fossil fuels page (20 charts: two per fuel, plus the sectoral gas split) and
two of the front page's four (monthly CO2 by fuel, and the projection).

Nothing here models anything. The two models it drives live next door and can be
read on their own:

  models/fuels.py                 where each fuel is read from, and its
                                  calorific value and emission factor
  models/fossil_extrapolation.py  projecting a fuel's year from its published
                                  months
  models/emissions_projection.py  calibrating those fuels against the reported
                                  national total

They were all one 870-line module until 2026-08-25, which is why the emissions
projection -- the single most consequential calculation on the site -- was
reachable only by reading past nine chart call sites to find it.
"""

from datetime import datetime

import numpy as np
import pandas as pd
from loguru import logger

from models import emissions_projection
from models import fossil_extrapolation
from models import fuels
from sources import eurostat

import series as S

from .spec import chart

#: December, as the "the year is complete" test for the yearly charts. The month
#: only ever travels as a number: the frontend renders it in the reader's
#: language, so the pipeline never spells a month name.
_DEC = 12


def consumption(logging=True):
    """Every per-fuel consumption chart, and the consumption the models need.

    Returns {fuel: {"data": {Timestamp: quantity}, "std_energy": float}} --
    projected annual consumption per fuel, which is what
    `models/emissions_projection.py` calibrates against the reported total.

    This function both draws and computes, deliberately: the yearly consumption
    charts *are* the model's output, so splitting them apart would mean running
    the extrapolation twice for every fuel.
    """
    if logging:
        logger.info("Charts: fossil fuel consumption ...")

    projected = {}
    for fuel, spec in fuels.FUELS.items():
        monthly = eurostat.monthly(name=spec["dataset"], code=spec["code"],
                                   options=spec["options"],
                                   unit=spec["options"]["unit"], movmean=12)
        if fuel in fuels.BLENDED:
            monthly = split_biofuel(monthly, fuel)

        chart("consumption_%s_monthly" % spec["chart_id"],
              title="AT %s: monthly consumption" % fuel,
              unit="Consumption (%s)" % fuels.unit_label(fuel),
              data=monthly,
              source="eurostat (%s)" % spec["code"],
              time_res="monthly",
              view="line")

        projected[fuel] = _yearly_chart(fuel, spec, monthly)

    # The three-way stack of what those fuels emit, per year, projection
    # included. Built here rather than in a second pass because it is the same
    # numbers with one multiplication applied.
    chart("emissions_fuels_yearly",
          title="AT CO2 emissions by fuels: yearly (incl. projection)",
          unit="Emissions (Mt<sub>CO2</sub>)",
          data=_by_category(projected),
          source="eurostat & own estimation | data of not fully available years are projected",
          time_res="yearly",
          view="toggle", initial="bar")

    return projected


def split_biofuel(monthly, fuel):
    """Separate the blended biofuel out of a road-fuel series.

    eurostat reports motor gasoline and road diesel *including* the biofuel
    blend, and reports the blend separately. Subtracting it gives the fossil
    half, which is the number the emission factor applies to -- using the
    reported total would overstate road CO2 by the blend share, currently
    around 6%.
    """
    blend = eurostat.monthly(name="oil", code="NRG_CB_OILM",
                             options={"unit": "THS_T",
                                      "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                      "siec": fuels.BLENDED[fuel]},
                             unit="THS_T", movmean=12)
    avg = "12-Month average"
    return S.wrap([
        ("%s Monthly" % fuel,
         S.series(S.times(monthly, "Monthly"),
                  S.values(monthly, "Monthly") - S.values(blend, "Monthly"))),
        ("%s 12-Month average" % fuel,
         S.series(S.times(monthly, avg), S.values(monthly, avg) - S.values(blend, avg))),
        ("Bio-%s Monthly" % fuel, blend["data"]["Monthly"]),
        ("Bio-%s 12-Month average" % fuel, blend["data"][avg]),
    ], {"code": "NRG_CB_OILM"})


def _yearly_chart(fuel, spec, monthly):
    """One fuel's yearly consumption chart, with this year's months projected.

    The stack is: what has been observed to date, what was observed in the rest
    of past years, and -- for the current year only -- the projection of the
    months not yet published. The three add up to the Total line, so the reader
    can see exactly how much of the newest bar is measured.
    """
    label = "%s Monthly" % fuel if fuel in fuels.BLENDED else "Monthly"
    cuts = fossil_extrapolation.by_year(monthly, label=label)
    projection = fossil_extrapolation.project(cuts)

    years = list(cuts["values_year_to_last_month"])
    times = pd.date_range(start=datetime(years[0], 1, 1),
                          end=datetime(years[-1], 1, 1), freq="YS")
    last_month = cuts["meta"]["last_month"]

    observed = np.array([cuts["values_year_to_last_month"][y] for y in years])
    pairs = [("Observed to date", S.series(times, observed))]
    # Series keys are stable regardless of how far the data reaches. They used to
    # carry the month -- "Observed: Jan - Jun" slugified to `observed_jan_jun` --
    # so every month the data advanced needed four new hand-written keys in both
    # locale files, and the locale files still carried the previous month's set.
    # A missed key renders as the literal key in the legend.
    labels = {"Observed to date": {"month": last_month}}

    if last_month != _DEC:
        rest = np.array([cuts["values_year_from_last_month"][y] for y in years])
        extrapolated = np.zeros(len(times))
        extrapolated[-1] = (projection["extrapolated_year"]
                            - projection["consumption_to_month"])
        pairs.append(("Observed rest of year", S.series(times, rest)))
        pairs.append(("Extrapolated rest of year", S.series(times, extrapolated)))
        labels["Observed rest of year"] = {"month": last_month + 1}
        labels["Extrapolated rest of year"] = {"month": last_month + 1}
    else:
        rest = np.zeros(len(times))
        extrapolated = np.zeros(len(times))

    total = observed + rest + extrapolated
    pairs.append(("Total", S.series(times, total)))

    chart("consumption_%s_yearly" % spec["chart_id"],
          title="AT %s: yearly consumption" % fuel,
          unit="Consumption (%s)" % fuels.unit_label(fuel),
          data=S.wrap(pairs, {"code": spec["code"], "labels": labels}),
          source="eurostat (%s)" % spec["code"],
          note="Extrapolated from monthly data, scaled with past trends.",
          time_res="yearly",
          view="bar")

    return {"data": {times[i]: total[i] for i in range(len(times))},
            "fac_mean": projection["fac_mean"],
            "std_energy": projection["std_energy"]}


def _by_category(projected):
    """Per-fuel yearly consumption -> Gas / Oil / Coal emissions in Mt CO2."""
    pairs = []
    for category, members in fuels.CATEGORIES.items():
        times = list(projected[members[0]]["data"])
        summed = np.zeros(len(times))
        for fuel in members:
            summed += np.array([projected[fuel]["data"][t] for t in times]) \
                * fuels.emission_factor(fuel)
        pairs.append((category, S.series(times, summed)))
    return S.wrap(pairs)


def emissions_by_fuel_monthly():
    """Monthly CO2 from the tracked fuels, stacked Gas / Oil / Coal.

    The one chart on the site that shows emissions at monthly resolution, which
    is only possible because it is computed from fuel volumes rather than taken
    from an inventory.
    """
    logger.info("Charts: monthly emissions by fuel ...")

    pairs = []
    for category, members in fuels.CATEGORIES.items():
        merged = None
        for fuel in members:
            spec = fuels.FUELS[fuel]
            monthly = eurostat.monthly(name=spec["dataset"], code=spec["code"],
                                       options=spec["options"],
                                       unit=spec["options"]["unit"], movmean=12)
            label = "Monthly"
            if fuel in fuels.BLENDED:
                monthly = split_biofuel(monthly, fuel)
                label = "%s Monthly" % fuel

            cuts = fossil_extrapolation.by_year(monthly, label=label)
            months = list(cuts["values_months"])
            values = np.array([cuts["values_months"][t] for t in months]) \
                * fuels.emission_factor(fuel)
            if merged is None:
                merged = (months, values)
            else:
                merged = (merged[0], merged[1] + values)
        pairs.append((category, S.series(merged[0], merged[1])))

    chart("emissions_fuels_monthly",
          title="AT CO2 emissions by fuels: monthly",
          unit="Emissions (Mt<sub>CO2</sub>)",
          data=S.wrap(pairs),
          source="eurostat & own estimation",
          time_res="monthly",
          view="line")


def projection(projected=None):
    """The front page's projection of total Austrian GHG emissions."""
    logger.info("Charts: emissions projection ...")
    if projected is None:
        projected = consumption(logging=False)

    data_plot, _ = emissions_projection.project(projected)

    chart("emissions_projection_yearly",
          title="AT GHG emissions: projection",
          unit="Emissions (Mt<sub>CO2e</sub>)",
          data=data_plot,
          source="Umweltbundesamt, eurostat & own projection",
          time_res="yearly",
          view="line")


def gas_by_sector():
    """Monthly and yearly natural gas consumption, split into three sectors.

    eurostat publishes the national total, the amount burned for public
    electricity and heat, and -- only from 09/2023 -- "other sectors", i.e.
    buildings. There is no industry figure at all, so industry is the residual.

    Two source quirks, both of which drew a visibly wrong chart before they were
    handled:

      * the buildings balance carries a lone `0.0` for 05/2023, four months
        before the series actually begins. Austrian buildings never burn zero gas
        in a month, so it is a placeholder and is read as a gap.
      * before 09/2023 buildings gas is inside the residual, because the residual
        absorbs whatever is not reported separately. Leaving it out instead opened
        a hole under the total line for thirty years of the chart.
    """
    logger.info("Charts: natural gas by sector ...")

    spec = fuels.FUELS["Natural gas"]
    balances = {
        "Total": "Inland consumption - calculated as defined in MOS GAS [IC_CAL_MG]",
        "Public electricity / heat":
            "Transformation input - electricity and heat generation - main activity producers [TI_EHG_MAP]",
        "Buildings": "Final consumption - other sectors [FC_OTH]",
    }
    # TJ_GCV as reported -> TWh net, the unit the rest of the energy charts use.
    to_twh = fuels.TJ_GCV_PER_1000M3 / fuels.TJ_NCV_PER_1000M3 / 3.6e3

    read = []
    for label, balance in balances.items():
        monthly = eurostat.monthly(name=spec["dataset"], code=spec["code"],
                                   options={"unit": "TJ_GCV", "nrg_bal": balance},
                                   unit=spec["options"]["unit"],
                                   start_year=2019, movmean=12)
        read.append((label, S.series(S.times(monthly, "Monthly"),
                                     S.values(monthly, "Monthly") * to_twh)))

    # Aligned to the total's axis, by date: the three balances do not start in
    # the same month, and aligning by array length happened to work only because
    # they all end in the same month.
    data = S.align(S.wrap(read), on="Total")

    buildings = S.values(data, "Buildings")
    buildings[buildings == 0] = np.nan
    data["data"]["Buildings"] = S.series(S.times(data, "Total"), buildings)

    data = S.residual(data, "Industry / Other", of="Total",
                      parts=["Public electricity / heat", "Buildings"])

    note = ("Buildings split out only from 09/2023, "
            "before that in Industry/Other.")
    # Total last: the frontend draws it as a line over the stack.
    order = ["Industry / Other", "Buildings", "Public electricity / heat", "Total"]
    monthly_plot = S.select(data, order)

    chart("gas_sectoral_consumption_monthly",
          title="AT natural gas consumption by sector: monthly",
          unit="Energy (TWh)",
          data=monthly_plot,
          source="eurostat (%s)" % spec["code"],
          note=note,
          time_res="monthly",
          view="toggle", initial="bar")

    chart("gas_sectoral_consumption_yearly",
          title="AT natural gas consumption by sector: yearly",
          unit="Energy (TWh)",
          # to_yearly sums months with a gap read as "nothing to add", so 2023
          # is a four-month buildings figure rather than a hole, while a year
          # with no data at all stays a gap.
          data=S.to_yearly(monthly_plot),
          source="eurostat (%s)" % spec["code"],
          note=note,
          time_res="yearly",
          view="toggle", initial="bar")


def plot():
    """Every chart this module owns, in one call."""
    projected = consumption()
    projection(projected)
    emissions_by_fuel_monthly()
    gas_by_sector()
