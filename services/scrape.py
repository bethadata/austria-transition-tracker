# -*- coding: utf-8 -*-
"""Download everything the pipeline can download.

    python scrape.py

Covers the two automatable sources only -- the eurostat monthly and yearly
tables, and the E-Control monthly electricity CSV. Both land in
`data_raw/eurostat/` and `data_raw/e_control/`, which are git-ignored precisely
because this script reproduces them.

Two things it deliberately does **not** do:

* the eurostat full energy balance (`download/energy_balance.py`). It is a slow
  per-fuel walk of the whole nrg_bal_c cube and eurostat only publishes a new
  year about every eighteen months, so it is an annual manual step rather than a
  daily one. Run it by hand when a new year appears.
* the manual drops -- Statistik Austria vehicle workbooks, the Umweltbundesamt
  Klimadashboard export, the EEA inventory, the hand-transcribed NIR tables.
  There is no API for any of them. They are tracked in git because git is their
  only backup; `sources/*.py` name what goes where.
"""

from loguru import logger

from download import econtrol, eurostat


def scrape_all():
    eurostat.download_all()
    econtrol.download_monthly_electricity()
    logger.info("Scrape finished.")


if __name__ == "__main__":
    scrape_all()
