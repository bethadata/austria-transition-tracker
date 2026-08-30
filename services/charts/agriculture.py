# -*- coding: utf-8 -*-
"""The Agriculture page: livestock, slaughterings, milk and fertiliser.

Six charts, all straight eurostat reads with no modelling. Grouped as a table
rather than six near-identical call sites, because the only thing that differs
between them is which dataset and which dimension filter.

The livestock chart is the one composite: four separate eurostat datasets, one
per animal, on one axis. Each has its own first year -- goats are only counted
from 1997 -- which is why the start years differ.
"""

from loguru import logger

from sources import eurostat

import series as S

from .spec import chart

MEAT_CODE = "apro_mt_pheadm"
SLAUGHT = "Slaughterings [SLAUGHT]"

#: Monthly eurostat series: chart id -> (title, unit label, dataset, code,
#: dimension filter, first year).
MONTHLY = {
    "slaughtered_pig_meat": (
        "AT Pigs: monthly slaughtered", "Meat (thousand tons)",
        "meat", MEAT_CODE, {"meat": "Pigmeat [B3100]", "meatitem": SLAUGHT}, 1990),
    "slaughtered_chicken_meat": (
        "AT Chicken: monthly slaughtered", "Meat (thousand tons)",
        # 2008 rather than 1990: eurostat's chicken series changes name twice
        # before then and the spliced result is not comparable.
        "meat", MEAT_CODE, {"meat": "Chicken [B7100]", "meatitem": SLAUGHT}, 2008),
    "slaughtered_cattle_meat": (
        "AT Cattle/cows: monthly slaughtered", "Meat (thousand tons)",
        "meat", MEAT_CODE, {"meat": "Bovine meat [B1000]", "meatitem": SLAUGHT}, 1990),
    "raw_cow_milk": (
        "AT Raw cow milk: monthly deliveries", "Milk (thousand tons)",
        "milk", "apro_mk_colm",
        {"dairyprod": "Raw cows' milk delivered to dairies [D1110D]"}, 1990),
}

#: The four livestock datasets, with the first year each is counted from.
LIVESTOCK = {
    "Cow / cattle": ("bovine_population", "apro_mt_lscatl",
                     "Live bovine animals [A2000]", 1993),
    "Pig": ("pig_population", "apro_mt_lspig",
            "Live swine, domestic species [A3100]", 1994),
    "Sheep": ("sheep_population", "apro_mt_lssheep",
              "Live sheep [A4100]", 1993),
    "Goat": ("goat_population", "apro_mt_lsgoat",
             "Live goats [A4200]", 1997),
}


def plot():
    logger.info("Charts: agriculture ...")

    for chart_id, (title, unit, dataset, code, options, start) in MONTHLY.items():
        chart(chart_id,
              title=title,
              unit=unit,
              data=eurostat.monthly(name=dataset, code=code, options=options,
                                    unit="THS_T", start_year=start, movmean=12),
              source="eurostat (%s)" % code,
              time_res="monthly",
              view="line")

    chart("fertilizer_nitrogen",
          title="AT Inorganic fertilizer: nitrogen consumption",
          unit="Tons",
          data=eurostat.yearly(name="fertilizer", code="aei_fm_usefert",
                               options={"nutrient": "N"}, unit="T",
                               start_year=2000),
          source="eurostat (aei_fm_usefert)",
          time_res="yearly",
          view="line")

    populations = []
    for label, (dataset, code, animal, start) in LIVESTOCK.items():
        data = eurostat.yearly(name=dataset, code=code,
                               options={"animals": animal}, unit="THS_HD",
                               start_year=start)
        populations.append((label, data["data"][dataset]))

    chart("animal_livestock_population",
          title="AT Cow/Pig/Sheep/Goats: population",
          unit="Thousand",
          data=S.wrap(populations),
          source="eurostat (%s)" % ", ".join(spec[1] for spec in LIVESTOCK.values()),
          time_res="yearly",
          view="line")
