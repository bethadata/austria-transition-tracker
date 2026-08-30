# -*- coding: utf-8 -*-
"""Projecting a fuel's full-year consumption from the months published so far.

The mechanism the whole "incl. projection" half of this dashboard rests on, and
it is deliberately simple: for the current year, only January to the last
published month is known. Take the ratio of full-year to same-partial-year
consumption in every previous year, average it, and apply that average to this
year's partial figure.

    projected_year = consumption(Jan..M this year) * mean over past years of
                     consumption(full year) / consumption(Jan..M that year)

It works because fossil-fuel consumption in Austria is strongly seasonal and the
seasonality is stable: the ratio for a given cut-off month varies little between
years. The spread of those ratios is therefore a usable uncertainty -- the
standard deviation of the ratios, scaled by the partial figure, is the error bar
the projection charts draw.

Divisor `len(facs) - 1.5` rather than the textbook `- 1`: a deliberately
conservative small-sample correction, kept because it is what the published
uncertainty bands have always used. Changing it would move every error bar on the
site without any underlying data changing.

The model is trained on 2013 onwards, which is when eurostat's monthly series
become complete for Austria.

This module was `plot/utils/filter_fossil_extrapolation.py` and also wrote a
matplotlib figure for the methodology page. That figure moved to
`figures/methodology.py`: a model and a diagram of the model are different jobs,
and the figure writer was pointing at the deleted `docs/` tree, so it had been
failing silently.
"""

import numpy as np

#: First year of complete monthly eurostat coverage for Austria.
TRAIN_START = 2013


def by_year(data_monthly, label="Monthly"):
    """Split a monthly series into per-year sums, whole and either side of the
    last published month.

    Returns the three cuts every caller needs at once, because computing them
    separately means walking the same months three times and getting the
    "which months count" question right three times:

      values_year                 full calendar years
      values_year_to_last_month   Jan .. last published month, every year
      values_year_from_last_month the rest of the year, every year

    The split point is the same month in every year, which is what makes the
    ratio across years comparable.
    """
    times = list(data_monthly["data"][label]["x"])
    values = list(data_monthly["data"][label]["y"])

    last_year = times[-1].year
    last_month = times[-1].month

    years = range(times[0].year, last_year + 1)
    whole = {year: 0 for year in years}
    to_month = {year: 0 for year in years}
    from_month = {year: 0 for year in years}
    months = {}

    for t, value in zip(times, values):
        # Months of the current year after the last published one are not zero,
        # they are absent -- counting them as zero would make this year's partial
        # figure look like a collapse.
        if t.year == last_year and t.month > last_month:
            continue
        whole[t.year] += value
        months[t] = value
        if t.month <= last_month:
            to_month[t.year] += value
        else:
            from_month[t.year] += value

    return {"values_months": months,
            "values_year": whole,
            "values_year_to_last_month": to_month,
            "values_year_from_last_month": from_month,
            "meta": {"last_year": last_year, "last_month": last_month}}


def project(cuts, last_year=None, last_month=None):
    """Project `last_year`'s full consumption from its first `last_month` months.

    `last_year` / `last_month` override what the data says, which is what the
    methodology figure uses to ask "what would this model have said in March?"
    """
    if last_year is None:
        last_year = cuts["meta"]["last_year"]
    if last_month is None:
        last_month = cuts["meta"]["last_month"]

    ratios = []
    for year in range(last_year - (last_year - TRAIN_START), last_year):
        full = cuts["values_year"][year]
        if full <= 0:
            # A year with no data cannot train the ratio, and dividing by its
            # partial sum would be a division by zero.
            continue
        partial = sum(value for t, value in cuts["values_months"].items()
                      if t.year == year and t.month <= last_month)
        ratios.append(full / partial)

    partial_now = sum(value for t, value in cuts["values_months"].items()
                      if t.year == last_year and t.month <= last_month)

    ratio_mean = np.mean(np.array(ratios))
    # See the module docstring on the 1.5.
    ratio_std = np.sqrt(np.var(ratios) * len(ratios) / (len(ratios) - 1.5))

    return {"facs": ratios,
            "consumption_to_month": partial_now,
            "fac_mean": ratio_mean,
            "std_estimator": ratio_std,
            "std_energy": partial_now * ratio_std,
            "extrapolated_year": partial_now * ratio_mean}
