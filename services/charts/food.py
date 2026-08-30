# -*- coding: utf-8 -*-
"""Food consumption: meat and dairy, total and per capita.

On the Agriculture page. Four charts, two StatCube exports, and the only
difference between the pairs is the measure column and a unit factor -- which is
why they are a table.

`factor` is a divisor: StatCube reports tonnes, the total charts show kilotonnes,
and the per-capita charts show the kilogram figure as published.
"""

from loguru import logger

from sources import statcube

from .spec import chart

SOURCE = "Statcube, Statistik Austria"

#: chart id -> (title, unit, reader, StatCube measure, divisor, note)
CHARTS = {
    "meat_consumption_total": (
        "AT Meat consumption: total", "Meat consumption (kt)",
        statcube.meat_consumption, "Menschlicher Verzehr", 1e3,
        "Human consumption per year"),
    "meat_consumption_per_capita": (
        "AT Meat consumption: per capita",
        "Meat consumption per capita (kg)",
        statcube.meat_consumption, "Menschlicher Verzehr pro Kopf in kg", 1,
        "Human consumption per capita in kg"),
    "milk_consumption_total": (
        "AT Milk product consumption: total", "Milk consumption (t)",
        statcube.milk_consumption, "NAHRUNGSVERBRAUCH", 1e3,
        "Food consumption per year"),
    "milk_consumption_per_capita": (
        "AT Milk product consumption: per capita",
        "Milk consumption per capita (kg)",
        statcube.milk_consumption, "Nahrungsverbrauch pro Kopf in kg", 1,
        "Food consumption per capita in kg"),
}


def plot():
    logger.info("Charts: food consumption ...")

    for chart_id, (title, unit, read, measure, factor, note) in CHARTS.items():
        chart(chart_id,
              title=title,
              unit=unit,
              data=read(measure=measure, factor=factor),
              source=SOURCE,
              note=note,
              time_res="yearly",
              view="toggle", initial="bar")
