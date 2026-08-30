# -*- coding: utf-8 -*-
"""Build every chart and write the frontend data contract.

The one orchestrator. Run it after `scrape.py`, or on its own to rebuild the
charts from the raw data already on disk:

    python pipeline.py          # rebuild everything
    python check_contract.py    # verify what it wrote

What it produces, all of it under `public/data/`:

    manifest.json     one entry per chart: id, page, section, view, series order,
                      unit key, source key. No human-readable text (that lives in
                      the frontend locale files).
    <chart-id>.json   the numbers for one chart.

and, as a side effect, `src/locales/_seed/` -- the English labels the pipeline
knows about, to diff against the hand-written locale files when a chart is added.

There used to be a second, byte-for-byte equivalent copy of this list in
`plot/plot_all.py`, and `CLAUDE.md` described the two as calling each other. They
never did: adding a chart meant editing both, and nothing caught it if you
edited one.

**Module order is not arbitrary.** `charts/fossil_fuels` builds the fuel
consumption the emissions projection needs, and `charts/overview` needs the
LULUCF breakdown before it can draw the with-LULUCF total. Everything else could
run in any order; keeping this one stable also keeps the manifest's own ordering
stable, so a rebuild with no data change produces no diff.
"""

from loguru import logger

from charts import manifest
from charts import agriculture
from charts import buildings
from charts import car_brands
from charts import energy
from charts import energy_balance
from charts import food
from charts import fossil_fuels
from charts import lulucf
from charts import overview
from charts import transport
from charts import waste

#: Every module that builds charts, in build order. A module belongs here and
#: nowhere else -- there is no second list.
MODULES = (
    buildings,
    fossil_fuels,
    agriculture,
    transport,
    waste,
    overview,
    energy,
    energy_balance,
    food,
    car_brands,
    lulucf,
)


def build():
    for module in MODULES:
        module.plot()


def main():
    logger.info("Building charts ...")
    build()

    result = manifest.finalize()
    logger.info("Wrote manifest: %d charts" % result["charts"])
    if result["pruned"]:
        logger.info("Pruned %d stale data files: %s"
                    % (len(result["pruned"]), ", ".join(sorted(result["pruned"]))))

    orphans = manifest.summary()
    if orphans:
        # Built but on no page. Not fatal -- but it is how the Jekyll site ended
        # up serving charts that nothing regenerated, so it gets said out loud.
        logger.warning("%d chart(s) with no page in charts/pages.py: %s"
                       % (len(orphans), ", ".join(orphans)))
    return result


if __name__ == "__main__":
    main()
