"""Build every chart and write the frontend data contract.

This is the only orchestrator. There used to be a second, byte-for-byte
equivalent copy of plot_all() in plot/plot_all.py, differing only in import
style; adding a chart meant editing both and nothing caught it if you edited
one. CLAUDE.md described the two as calling each other. They never did.
"""

import plotly.io as pio
pio.renderers.default = "browser"

from loguru import logger

from plot import manifest
from plot import plot_agriculture
from plot import plot_buildings
from plot import plot_car_brands
from plot import plot_emissions_sectors
from plot import plot_energy
from plot import plot_energy_balance
from plot import plot_food_consumption
from plot import plot_fossil_fuels
from plot import plot_industry
from plot import plot_transport
from plot import plot_waste


def plot_all():
    plot_buildings.plot()
    # extrapolate_emissions() calls extrapolate_fossil_fuels() itself, and that
    # is where the per-fuel consumption charts are written -- calling it here as
    # well rebuilt all 16 of them a second time every run.
    # save=True, show_plot=False: the emissions projection is on the front page.
    # It had not been regenerated in months because its only save path was tied
    # to a debug flag that also opened a browser window, so the orchestrator
    # kept it switched off and the chart quietly froze.
    plot_fossil_fuels.extrapolate_emissions(plot=False, save=True)
    plot_fossil_fuels.plot_emissions_fuels()
    plot_fossil_fuels.plot_ng_separation()
    plot_agriculture.plot()
    plot_transport.plot()
    plot_industry.plot()
    plot_waste.plot()
    plot_emissions_sectors.plot()
    plot_energy.plot()
    plot_energy_balance.plot()
    plot_food_consumption.plot()
    plot_car_brands.plot()
    # plot_lulucf has no plot(): it draws at import time. Imported here rather
    # than at module level so it runs in order with the rest.
    from plot import plot_lulucf  # noqa: F401


def main():
    logger.info("Building charts ...")
    plot_all()

    result = manifest.finalize()
    logger.info("Wrote manifest: %d charts" % result["charts"])
    if result["pruned"]:
        logger.info("Pruned %d stale data files: %s"
                    % (len(result["pruned"]), ", ".join(sorted(result["pruned"]))))

    orphans = manifest.summary()
    if orphans:
        # Built but on no page. Not fatal -- but it is how the Jekyll site ended
        # up serving charts that nothing regenerated, so it gets said out loud.
        logger.warning("%d chart(s) with no page in plot/pages.py: %s"
                       % (len(orphans), ", ".join(orphans)))
    return result


if __name__ == "__main__":
    main()
