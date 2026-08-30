# -*- coding: utf-8 -*-
"""Austria's total GHG emissions, projected past the last reported year.

The front page's headline chart, and the most consequential piece of modelling in
the project -- it is the one number on the site that is not somebody else's
published figure. Worth reading before touching.

**The problem.** The Umweltbundesamt reports Austrian emissions about eighteen
months late. eurostat reports fossil fuel consumption monthly, about three months
late. So the fuels burned in the missing years are roughly known while the
emissions are not.

**The method, in three steps.**

1. *Bottom-up estimate.* Multiply each fuel's projected annual consumption
   (`models/fossil_extrapolation.py`) by its calorific value and emission factor
   (`models/fuels.py`). This gives CO2 from the fuels this project tracks -- not
   all emissions, and not all of any sector.

2. *Calibrate against the reported total.* Over a training window of reported
   years, take the ratio of the UBA figure for the three energy-driven sectors
   (Transport, Buildings, Energy & Industry) to the bottom-up estimate for the
   same years, and average it. That single factor absorbs everything the
   bottom-up estimate does not see: untracked fuels, process emissions, the
   difference between deliveries and combustion. The scatter of the ratios over
   the training window is the model's own uncertainty.

3. *Extrapolate the rest.* Agriculture, waste and F-gases are not fuel-driven, so
   they are carried forward on a three-year linear trend. They are a small and
   slow-moving share of the total, which is what makes that acceptable.

**The uncertainty band has two independent halves**, and they are added rather
than combined in quadrature -- the conservative choice, kept deliberately:

  * the scaling uncertainty, from the spread of the calibration ratios
  * the consumption uncertainty, from projecting an incomplete year of fuel data.
    This one is zero for a year whose fuel data is complete, which is why the
    band widens sharply for the current year.

Everything the model produces is labelled a projection on the chart, and the
chart carries a note saying so. It is a nowcast, not a forecast.

The training window and the projected years are derived from how far the two
sources actually reach. They used to be literals (`train_start=2019`,
`years_extrapolate=[2025, 2026]`), so a new UBA release would have left the model
training on a stale window and projecting years that were already reported.
"""

from datetime import datetime

import numpy as np
import pandas as pd

from sources import umweltbundesamt

from . import fuels

#: Sectors whose emissions the fuel model can speak to.
ENERGY_SECTORS = ("Transport", "Buildings", "Energy & Industry")

#: Sectors carried forward on a linear trend instead.
OTHER_SECTORS = ("Agriculture", "Waste", "Fluorinated Gases")

#: Length of the calibration window, in reported years.
TRAIN_YEARS = 6

#: Years over which the non-fuel sectors' trend is measured.
TREND_YEARS = 3


def project(consumption, train_start=None, train_end=None, project_years=None):
    """Project total Austrian emissions from projected fuel consumption.

    consumption    {fuel: {"data": {Timestamp: quantity}, "std_energy": float}},
                   as built by `charts/fossil_fuels.py`
    train_start /
    train_end      calibration window; defaults to the last TRAIN_YEARS reported
                   UBA years
    project_years  years to project; defaults to every year after the last
                   reported one for which fuel consumption exists

    Returns (data_plot, diagnostics). The data_plot is chart-ready; the
    diagnostics are what `figures/methodology.py` draws.
    """
    reported = umweltbundesamt.sectoral_emissions()["data"]
    times_historic = list(reported["Agriculture"]["x"])
    last_reported = times_historic[-1].year

    if train_end is None:
        train_end = last_reported
    if train_start is None:
        train_start = train_end - TRAIN_YEARS + 1

    times_train = pd.date_range(start=datetime(train_start, 1, 1),
                                end=datetime(train_end, 1, 1), freq="YS")

    if project_years is None:
        # Only years the fuel model actually reaches. Asking for a year with no
        # consumption behind it used to be a KeyError deep inside the loop.
        available = {pd.Timestamp(t).year for f in consumption for t in consumption[f]["data"]}
        project_years = sorted(y for y in available if y > train_end)
    if not project_years:
        raise ValueError("nothing to project: fuel data reaches %d, UBA reaches %d"
                         % (max(available) if available else 0, train_end))

    times_projected = pd.date_range(start=datetime(project_years[0], 1, 1),
                                    end=datetime(project_years[-1], 1, 1), freq="YS")

    # --- step 1 + 2: calibrate the bottom-up estimate against the reported total
    estimated_train = np.zeros(len(times_train))
    for fuel in consumption:
        estimated_train += np.array([consumption[fuel]["data"][t] for t in times_train]) \
            * fuels.emission_factor(fuel)

    energy_reported = _sector_sum(reported, ENERGY_SECTORS)
    other_reported = _sector_sum(reported, OTHER_SECTORS)

    train_index = [times_historic.index(t) for t in times_train]
    ratios = [energy_reported[i] / estimated_train[k]
              for k, i in enumerate(train_index)]
    ratio_mean = float(np.mean(ratios))
    # The same conservative small-sample correction the fuel extrapolation uses;
    # see models/fossil_extrapolation.py.
    ratio_std = float(np.sqrt(np.var(ratios) * len(ratios) / (len(ratios) - 1.5)))

    # --- step 3: project the energy sectors, and their two error terms
    energy_projected = []
    std_scaling = []
    std_consumption = []
    for t in times_projected:
        estimated = sum(consumption[f]["data"][t] * fuels.emission_factor(f)
                        for f in consumption)
        projected = estimated * ratio_mean
        energy_projected.append(projected)
        std_scaling.append(projected * ratio_std)

        # A year whose own fuel data is complete carries no extrapolation error.
        # "Complete" is decided by whether the *next* year exists in the
        # consumption series, which is what the fuel model produces once it has
        # rolled over.
        std = 0.0
        next_year = pd.Timestamp(year=t.year + 1, month=1, day=1)
        for f in consumption:
            if next_year not in consumption[f]["data"]:
                std += consumption[f]["std_energy"] * fuels.emission_factor(f) * ratio_mean
        std_consumption.append(std)

    band = [a + b for a, b in zip(std_scaling, std_consumption)]

    # --- the non-fuel sectors, on a linear trend
    last = times_historic.index(times_train[-1])
    trend = (other_reported[last] - other_reported[last - TREND_YEARS]) / TREND_YEARS
    other_projected = [other_reported[last] + (i + 1) * trend
                       for i in range(len(times_projected))]

    historic = energy_reported + other_reported
    projected_total = [historic[last]] + [energy_projected[i] + other_projected[i]
                                          for i in range(len(times_projected))]
    times_projected_line = [times_historic[last]] + list(times_projected)

    times_total = times_historic + times_projected_line[1:]

    data_plot = {
        "data": {
            "Energy sectors": {"x": times_total,
                               "y": list(energy_reported) + energy_projected},
            "Other sectors": {"x": times_total,
                              "y": list(other_reported) + other_projected},
            "Projected emissions": {"x": times_projected_line, "y": projected_total},
            "Historic emissions": {"x": times_historic, "y": historic},
        },
        # The band starts at 0 because its first point is the last reported year,
        # which the projection line is anchored to rather than projecting.
        "meta": {"uncertainty": {"Projected emissions": [0] + band},
                 "areas": ["Energy sectors", "Other sectors"]},
    }

    diagnostics = {"energy_projected": energy_projected,
                   "std_scaling": std_scaling,
                   "std_consumption": std_consumption,
                   "other_projected": other_projected,
                   "ratio_mean": ratio_mean,
                   "ratio_std": ratio_std,
                   "train": (train_start, train_end)}
    return data_plot, diagnostics


def _sector_sum(reported, sectors):
    return sum(np.array(reported[s]["y"]) for s in sectors)
