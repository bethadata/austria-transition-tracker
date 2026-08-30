# -*- coding: utf-8 -*-
"""Download the eurostat tables the charts read.

One `.xlsx` per dataset in `data_raw/eurostat/`, named `AT_<name>_<code>.xlsx`.
The coded dimension values are expanded to `"Label [CODE]"` on the way in, which
is what makes the filters in `sources/` readable -- and what makes them break
loudly rather than silently if eurostat renames a category.

New data points are logged as they arrive, which is the only routine signal that
the upstream sources have moved.
"""

import os

# The PyPI `eurostat` client, not this module: absolute imports are the default,
# so `download.eurostat` and `eurostat` do not collide. Worth knowing before
# adding a relative import here, which would.
import eurostat
import pandas as pd
from loguru import logger

from paths import DATA_RAW

EUROSTAT_DIR = DATA_RAW + "/eurostat"

#: The datasets, in download order. `options` are the dimensions whose codes get
#: expanded to labels; `filters` narrow the request itself, which matters for
#: nrg_bal_c where an unfiltered pull is enormous.
DATASETS = (
    # Agriculture
    {"name": "meat", "code": "apro_mt_pheadm", "options": ["meat", "meatitem"]},
    {"name": "milk", "code": "apro_mk_colm", "options": ["dairyprod"]},
    {"name": "fertilizer", "code": "aei_fm_usefert", "options": []},
    # Livestock. These were commented out for long enough that the four cached
    # files went stale and could not be rebuilt from a fresh clone at all --
    # `eurostat/` is git-ignored, so the chart's only data existed on one PC.
    # `month: M12` is the December census, which is the series the chart shows.
    {"name": "bovine_population", "code": "apro_mt_lscatl",
     "options": ["animals"], "filters": {"month": "M12"}},
    {"name": "pig_population", "code": "apro_mt_lspig",
     "options": ["animals"], "filters": {"month": "M12"}},
    {"name": "sheep_population", "code": "apro_mt_lssheep",
     "options": ["animals"], "filters": {"month": "M12"}},
    {"name": "goat_population", "code": "apro_mt_lsgoat",
     "options": ["animals"], "filters": {"month": "M12"}},
    # Fossil fuels, monthly
    {"name": "gas", "code": "NRG_CB_GASM", "options": ["siec", "nrg_bal"]},
    {"name": "coal", "code": "NRG_CB_SFFM", "options": ["siec", "nrg_bal"]},
    {"name": "oil", "code": "NRG_CB_OILM", "options": ["siec", "nrg_bal"]},
    # Vehicles
    {"name": "cars", "code": "road_eqr_carpda", "options": ["mot_nrg"]},
    {"name": "cars", "code": "road_eqs_carpda", "options": ["mot_nrg"]},
    {"name": "lorries", "code": "road_eqr_lormot", "options": ["mot_nrg"]},
    # Single-fuel cuts of the yearly energy balance
    {"name": "natural_gas_en_bal", "code": "nrg_bal_c",
     "options": ["siec", "nrg_bal"], "filters": {"unit": "GWH", "siec": "G3000"}},
    {"name": "oil_en_bal", "code": "nrg_bal_c",
     "options": ["siec", "nrg_bal"], "filters": {"unit": "GWH", "siec": "O4000XBIO"}},
    {"name": "coal_en_bal", "code": "nrg_bal_c",
     "options": ["siec", "nrg_bal"],
     "filters": {"unit": "GWH", "siec": "C0000X0350-0370"}},
    # Electricity and rail
    {"name": "electricity_fuel_type", "code": "nrg_cb_pem", "options": ["siec"]},
    {"name": "rail_tracks", "code": "rail_if_line_tr", "options": ["tra_infr"]},
)


def download_and_save(name, code, options=(), geo=("AT",), filters=None,
                      start_period=1990):
    logger.info("Downloading eurostat data %s ..." % name)

    # The directory is git-ignored, so on a fresh clone it does not exist at all
    # and pandas' to_excel would fail on the very first dataset.
    os.makedirs(EUROSTAT_DIR, exist_ok=True)
    path = "%s/%s_%s_%s.xlsx" % (EUROSTAT_DIR, geo[0], name, code)

    # The previous periods, so the ones that are new can be logged. Empty on a
    # first run; the old code assigned the previous frame unconditionally and
    # therefore raised NameError on a fresh clone, which is exactly the case
    # untracking `eurostat/` made routine.
    previous = pd.read_excel(path).keys() if os.path.exists(path) else []

    request = {"startPeriod": start_period, "geo": list(geo)}
    expansions = {}
    for option in options:
        codes = eurostat.get_par_values(code, option)
        names = eurostat.get_dic(code, option, frmt="dict")
        expansions[option] = (codes, names)
        request[option] = codes
    for key, value in (filters or {}).items():
        request[key] = value

    data = eurostat.get_data_df(code, filter_pars=request)

    # Code -> "Label [CODE]", so the filters in sources/ read as the labels a
    # reader sees on eurostat's own site and carry the code for provenance.
    for option, (codes, names) in expansions.items():
        for value in codes:
            data = data.replace(value, names[value].strip() + " [" + value + "]")

    frame = pd.DataFrame(data)
    frame.to_excel(path)

    for period in frame.keys():
        if period not in previous and sum(frame[period].notnull()) > 0:
            logger.info("New data point: %s" % period)

    logger.info("Downloading eurostat data %s finished!" % name)


def download_all():
    for dataset in DATASETS:
        download_and_save(**dataset)


if __name__ == "__main__":
    download_all()
