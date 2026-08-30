# -*- coding: utf-8 -*-
"""Download E-Control's monthly electricity dataset (MoMeGes).

One CSV, one URL, no API. `sources/econtrol.py` reads it and documents the
column codes, which are the fragile part.
"""

import os

import requests
from loguru import logger

from paths import DATA_RAW

URL = "https://www.e-control.at/documents/1785851/8165594/el_dataset_mn.csv"
TARGET = DATA_RAW + "/e_control/el_dataset_mn.csv"


def download_monthly_electricity():
    # Git-ignored directory, so it does not exist on a fresh clone.
    os.makedirs(os.path.dirname(TARGET), exist_ok=True)

    response = requests.get(URL, timeout=120)
    if response.status_code != 200:
        # Warn rather than raise: a scrape that loses one source should still
        # refresh the others, and the charts fall back to the cached CSV.
        logger.warning("E-Control download failed: HTTP %s" % response.status_code)
        return False

    with open(TARGET, "wb") as fp:
        fp.write(response.content)
    logger.info("E-Control download successful")
    return True


if __name__ == "__main__":
    download_monthly_electricity()
