# -*- coding: utf-8 -*-
"""The three diagrams on the Methodology page.

    python -m figures.methodology

**Run by hand, not by the pipeline.** These illustrate how the projection models
work rather than reporting current data, so they only need regenerating when a
model changes -- and each one runs the fuel extrapolation twelve times over, once
per hypothetical cut-off month, which is far too slow for a nightly build.

They write PNGs into `public/images/`, alongside the rest of the app's static
assets:

    fossil_fuel_consumption_estimation.png  how one fuel's year is projected from
                                            its published months, for three fuels
                                            and every possible cut-off month
    emissions_projection_2022.png           the same question asked of total
                                            emissions: how good was the
                                            projection, month by month, for a
                                            year now fully reported
    emissions_estimation.png                the calibration step: bottom-up fuel
                                            emissions against the reported total,
                                            before and after scaling

**These were broken before the Vue migration and had been for some time.** All
three wrote into `docs/assets/images/` -- the Jekyll asset tree, deleted with the
rest of it -- and one of them called the projection with a keyword argument that
no longer existed. Nothing noticed, because nothing ran them and the PNGs they
had already produced were still being served.

**Transparent background, themed ink.** The three existing PNGs are opaque white,
so they sit as bright rectangles on the dark theme. These are drawn with a
transparent canvas and a mid-grey ink that reads on either background, which is
the fix for that -- regenerate them to apply it.
"""

import os

import matplotlib
import numpy as np
import pandas as pd
from loguru import logger

from models import emissions_projection
from models import fossil_extrapolation
from models import fuels
from sources import eurostat
from sources import umweltbundesamt
from paths import PUBLIC_IMAGES

from charts import fossil_fuels

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (must follow the backend choice)

#: Ink that reads on both the light and the dark theme. Neither black nor white
#: works on both; this mid-grey does, and the accent colours are the same hues
#: the charts use.
INK = "#6b7280"
ACCENT = ["#2a78d6", "#d97706", "#0ca30c"]

#: The year the two emissions figures are drawn for. A *fully reported* year, so
#: the projection can be compared against the truth -- that is the whole point of
#: the figures, and it is why this is a literal rather than "the newest year".
DEMO_YEAR = 2022

#: The three fuels the consumption figure illustrates: one from each of gas, oil
#: and coal, since the seasonality differs sharply between them.
DEMO_FUELS = ["Natural gas", "Diesel", "Coke oven coke"]

MONTHS = np.arange(1, 13)


def _style(ax, title, xlabel, ylabel):
    ax.set_title(title, color=INK)
    ax.set_xlabel(xlabel, color=INK)
    ax.set_ylabel(ylabel, color=INK)
    ax.tick_params(colors=INK)
    for spine in ax.spines.values():
        spine.set_color(INK)
    ax.grid(color=INK, alpha=0.25)
    legend = ax.legend(labelcolor=INK, framealpha=0)
    legend.get_frame().set_edgecolor(INK)


def _save(fig, name):
    os.makedirs(PUBLIC_IMAGES, exist_ok=True)
    path = "%s/%s.png" % (PUBLIC_IMAGES, name)
    fig.tight_layout()
    fig.savefig(path, dpi=400, transparent=True)
    plt.close(fig)
    logger.info("Wrote %s" % path)


def _monthly(fuel):
    """One fuel's monthly series, biofuel split out where that applies."""
    spec = fuels.FUELS[fuel]
    monthly = eurostat.monthly(name=spec["dataset"], code=spec["code"],
                               options=spec["options"],
                               unit=spec["options"]["unit"], movmean=12)
    label = "Monthly"
    if fuel in fuels.BLENDED:
        monthly = fossil_fuels.split_biofuel(monthly, fuel)
        label = "%s Monthly" % fuel
    return monthly, label


# ---------------------------------------------------------------------------
# 1: one fuel's year, projected from each possible cut-off month
# ---------------------------------------------------------------------------

def fuel_consumption_estimation():
    fig, axes = plt.subplots(1, len(DEMO_FUELS))
    fig.set_size_inches(7 * len(DEMO_FUELS), 4)

    for ax, fuel in zip(np.atleast_1d(axes), DEMO_FUELS):
        monthly, label = _monthly(fuel)
        cuts = fossil_extrapolation.by_year(monthly, label=label)

        projected, spread, to_month = [], [], []
        for month in MONTHS:
            result = fossil_extrapolation.project(cuts, last_year=DEMO_YEAR,
                                                  last_month=int(month))
            projected.append(result["extrapolated_year"])
            spread.append(result["std_energy"])
            to_month.append(result["consumption_to_month"])

        projected = np.array(projected)
        spread = np.array(spread)
        actual = cuts["values_year"][DEMO_YEAR]

        ax.plot(MONTHS, projected, color=ACCENT[0], label="Extrapolated yearly")
        ax.fill_between(MONTHS, projected - spread, projected + spread,
                        color=ACCENT[0], alpha=0.25,
                        label="Estimated standard deviation")
        ax.plot(MONTHS, [actual] * len(MONTHS), color=ACCENT[1],
                label="Actual yearly")
        ax.plot(MONTHS, to_month, color=ACCENT[2],
                label="Actual monthly (cumulated)")
        ax.set_ylim([0, max(projected) * 1.3])
        _style(ax, "Consumption estimation: %s %i" % (fuel, DEMO_YEAR),
               "Month", "Consumption (%s)" % fuels.unit_label(fuel))

    _save(fig, "fossil_fuel_consumption_estimation")


# ---------------------------------------------------------------------------
# 2: the calibration step, bottom-up against reported
# ---------------------------------------------------------------------------

def emissions_estimation(start_year=2008):
    times = pd.date_range(start="%i-01-01" % start_year,
                          end="%i-01-01" % DEMO_YEAR, freq="YS")

    estimated = np.zeros(len(times))
    for fuel in fuels.FUELS:
        monthly, label = _monthly(fuel)
        cuts = fossil_extrapolation.by_year(monthly, label=label)
        estimated += np.array([cuts["values_year"][t.year] for t in times]) \
            * fuels.emission_factor(fuel)

    reported = umweltbundesamt.sectoral_emissions()["data"]
    index = {t: i for i, t in enumerate(reported["Transport"]["x"])}
    energy = np.array([sum(reported[s]["y"][index[t]]
                           for s in emissions_projection.ENERGY_SECTORS)
                       for t in times])

    ratios = energy / estimated
    ratio_mean = float(np.mean(ratios))
    ratio_std = float(np.sqrt(np.var(ratios) * len(ratios) / (len(ratios) - 1.5)))
    scaled = estimated * ratio_mean
    spread = estimated * ratio_std

    fig, axes = plt.subplots(2, 1)
    fig.set_size_inches(7, 6)

    axes[0].plot(times, estimated, color=ACCENT[0], label="Estimated emissions")
    axes[0].plot(times, energy, color=ACCENT[1],
                 label="Actual emissions Energy-sectors")
    axes[0].set_ylim([0, max(energy) * 1.1])
    _style(axes[0], "", "", "CO2 emissions (Mt)")

    axes[1].plot(times, scaled, color=ACCENT[0], label="Scaled emissions")
    axes[1].plot(times, energy, color=ACCENT[1],
                 label="Actual emissions Energy-sectors")
    axes[1].fill_between(times, scaled - spread, scaled + spread,
                         color=ACCENT[0], alpha=0.25,
                         label="Scaling standard deviation")
    axes[1].set_ylim([0, max(energy) * 1.1])
    _style(axes[1], "", "Year", "CO2 emissions (Mt)")

    _save(fig, "emissions_estimation")


# ---------------------------------------------------------------------------
# 3: how good the total-emissions projection was, month by month
# ---------------------------------------------------------------------------

def emissions_projection_demo(start_year=2008):
    """Project DEMO_YEAR's total from each cut-off month, against the truth."""
    cached = {}
    for fuel in fuels.FUELS:
        monthly, label = _monthly(fuel)
        cached[fuel] = fossil_extrapolation.by_year(monthly, label=label)

    times = pd.date_range(start="%i-01-01" % start_year,
                          end="%i-01-01" % DEMO_YEAR, freq="YS")

    projected, scaling_error, consumption_error = [], [], []
    for month in MONTHS:
        logger.info("Projecting %i from month %i/12" % (DEMO_YEAR, month))
        consumption = {}
        for fuel, cuts in cached.items():
            result = fossil_extrapolation.project(cuts, last_year=DEMO_YEAR,
                                                  last_month=int(month))
            yearly = np.array([cuts["values_year_to_last_month"][t.year]
                               + cuts["values_year_from_last_month"][t.year]
                               for t in times])
            yearly[-1] = result["extrapolated_year"]
            consumption[fuel] = {
                "data": {times[i]: yearly[i] for i in range(len(times))},
                "std_energy": result["std_energy"]}

        _, diagnostics = emissions_projection.project(
            consumption, train_start=start_year, train_end=DEMO_YEAR - 1,
            project_years=[DEMO_YEAR])
        projected.append(diagnostics["energy_projected"][0]
                         + diagnostics["other_projected"][0])
        scaling_error.append(diagnostics["std_scaling"][0])
        consumption_error.append(diagnostics["std_consumption"][0])

    reported = umweltbundesamt.sectoral_emissions()["data"]
    index = list(reported["Transport"]["x"]).index(times[-1])
    actual = sum(reported[s]["y"][index]
                 for s in emissions_projection.ENERGY_SECTORS
                 + emissions_projection.OTHER_SECTORS)

    projected = np.array(projected)
    band = np.array(scaling_error) + np.array(consumption_error)

    fig, axes = plt.subplots(2, 1)
    fig.set_size_inches(7, 6)

    axes[0].plot(MONTHS, [actual] * len(MONTHS), color=ACCENT[1],
                 label="Actual emissions")
    axes[0].plot(MONTHS, projected, color=ACCENT[0], label="Projected emissions")
    axes[0].fill_between(MONTHS, projected - band / 2, projected + band / 2,
                         color=ACCENT[0], alpha=0.25,
                         label="Estimated standard deviation")
    axes[0].set_ylim([0, actual * 1.2])
    _style(axes[0],
           "CO2 emission extrapolation of %i using monthly data" % DEMO_YEAR,
           "", "CO2 emissions (Mt_CO2e)")

    axes[1].plot(MONTHS, consumption_error, color=ACCENT[0],
                 label="Uncertainty fossil fuel consumption extrapolation")
    axes[1].plot(MONTHS, scaling_error, color=ACCENT[1],
                 label="Uncertainty emission scaling")
    axes[1].set_ylim([0, max(max(consumption_error), max(scaling_error)) * 1.1])
    _style(axes[1], "", "Month", "CO2 emissions (Mt_CO2e)")

    _save(fig, "emissions_projection_%i" % DEMO_YEAR)


def build_all():
    fuel_consumption_estimation()
    emissions_estimation()
    emissions_projection_demo()


if __name__ == "__main__":
    build_all()
