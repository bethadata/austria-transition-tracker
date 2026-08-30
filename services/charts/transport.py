# -*- coding: utf-8 -*-
"""The Transport page: road fuels, vehicle fleets and the rail network.

Twenty-two charts, in four groups:

  fuel volumes     monthly eurostat deliveries of road fuel, road biofuel and
                   kerosene, each with a 12-month trailing average
  vehicles         new registrations and the standing fleet, by fuel category,
                   absolute and as shares -- the messiest data in the project,
                   see `sources/vehicles.py`
  brands           BEV registrations by manufacturer (`charts/car_brands.py`)
  rail             track length, electrified and not

**The fuel-category order is Electric first**, and deliberately so: these charts
exist to show the electrification of the fleet, so the series that matters is at
the bottom of the stack where it can be read against the axis. It is not the
order `sources/vehicles.FUEL_CATEGORIES` declares, which is the order eurostat
reports in.
"""

import numpy as np
from loguru import logger

from sources import eurostat
from sources import vehicles

import series as S

from .spec import chart

OIL = "NRG_CB_OILM"
FUEL_UNIT = "Fuel (thousand tons)"

#: Read-order for the vehicle charts: electrification at the bottom of the stack.
FUEL_ORDER = ["Electric", "Hybrid plugin", "Hybrid", "Diesel", "Gasoline", "Other"]

_GID = "Gross inland deliveries - observed [GID_OBS]"

REGISTRATION_SOURCE = "eurostat (road_eqr_carpda) & Statistik Austria"
STOCK_SOURCE = "eurostat (road_eqs_carpda) and Statistik Austria"
LORRY_SOURCE = "eurostat (road_eqr_lormot)"
RAIL_SOURCE = "eurostat (rail_if_line_tr) & Statistik Austria"

# Neither clause names a year, and that is the point. This note used to open
# with "Data of 2024 until 12/2024" and to fix the hybrid merge at "before
# 2013"; both were written by hand into the locale, and both went stale silently
# the moment a new drop moved them. How far the newest point runs is now the
# chart's own x axis, and whether it is provisional travels in the manifest as
# `preliminary` -- see charts/spec.chart().
STOCK_NOTE = ("Plug-in hybrids count as hybrids where the source does not "
              "split them.")
REGISTRATION_NOTE = "The newest year covers the months published so far."


def plot():
    logger.info("Charts: transport ...")
    _road_fuels()
    _new_registrations()
    _car_stock()
    _lorries()
    _rail()


# ---------------------------------------------------------------------------
# Fuel volumes
# ---------------------------------------------------------------------------

def _oil_series(siec, start_year=2010):
    return eurostat.monthly(name="oil", code=OIL, start_year=start_year,
                            options={"unit": "THS_T", "nrg_bal": _GID, "siec": siec},
                            unit="THS_T", movmean=12)


def _pair(label, data):
    """One fuel's two series -- the months and their average -- renamed for a
    chart that carries more than one fuel."""
    avg = "12-Month average"
    return [("%s monthly" % label, data["data"]["Monthly"]),
            ("%s 12-Month average" % label, data["data"][avg])]


def _road_fuels():
    diesel = _oil_series("Road diesel [O46711]")
    gasoline = _oil_series("Motor gasoline [O4652]")

    chart("road_fuels_consumption",
          title="AT Road fuels: monthly consumption (incl. biofuels)",
          unit=FUEL_UNIT,
          data=S.wrap(_pair("Diesel", diesel) + _pair("Gasoline", gasoline),
                      {"code": "%s | %s" % (OIL, OIL)}),
          source="eurostat (%s)" % OIL,
          time_res="monthly",
          view="line")

    bio_diesel = _oil_series("Blended biodiesels [R5220B]")
    bio_gasoline = _oil_series("Blended biogasoline [R5210B]")

    chart("road_biofuels_consumption",
          title="AT Road biofuels: monthly consumption",
          unit=FUEL_UNIT,
          data=S.wrap(_pair("Blended biodiesel", bio_diesel)
                      + _pair("Blended biogasoline", bio_gasoline),
                      {"code": "%s | %s" % (OIL, OIL)}),
          source="eurostat (%s)" % OIL,
          time_res="monthly",
          view="line")

    chart("kerosene_consumption",
          title="AT Kerosene / Aviation fuel: monthly consumption (incl. biofuels)",
          unit=FUEL_UNIT,
          data=_oil_series("Kerosene-type jet fuel [O4661]"),
          source="eurostat (%s)" % OIL,
          time_res="monthly",
          view="line")


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------

def _by_category(counts):
    """{category: {date: count}} -> (shares, absolute with a Total).

    The two are built together because the shares divide by the same Total the
    absolute chart draws, and because both charts always appear as a pair.
    """
    axis = list(counts[FUEL_ORDER[0]])
    absolute = S.wrap(
        [(category, S.series(axis, [counts[category][t] for t in axis]))
         for category in FUEL_ORDER]
        + [("Total", S.series(axis, [counts["Total"][t] for t in axis]))])
    return S.shares(absolute), absolute


def _new_registrations():
    monthly = vehicles.new_registrations_monthly()
    shares, absolute = _by_category(monthly)

    chart("share_fuel_new_cars",
          title="AT new monthly car registrations: fuel type share",
          unit="Share [%]",
          data=shares,
          source=REGISTRATION_SOURCE,
          time_res="monthly",
          view="toggle", initial="area")

    chart("number_fuel_new_cars",
          title="AT new monthly car registrations: fuel type absolute number",
          unit="Number",
          data=absolute,
          source=REGISTRATION_SOURCE,
          time_res="monthly",
          view="toggle", initial="line")

    # Yearly is the monthly sum, and the Total is dropped: on a yearly bar chart
    # the stack already reads as the total, and a line over it just repeats it.
    yearly_absolute = S.to_yearly(absolute)
    yearly_shares = S.shares(yearly_absolute)
    yearly_absolute = S.select(yearly_absolute, FUEL_ORDER)

    chart("share_fuel_new_cars_yearly",
          title="AT new yearly car registrations: fuel type share",
          unit="Share [%]",
          data=yearly_shares,
          source=REGISTRATION_SOURCE,
          note=REGISTRATION_NOTE,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("number_fuel_new_cars_yearly",
          title="AT new yearly car registrations: fuel type absolute number",
          unit="Number",
          data=yearly_absolute,
          source=REGISTRATION_SOURCE,
          note=REGISTRATION_NOTE,
          time_res="yearly",
          view="toggle", initial="bar")


def _car_stock():
    stock, month, year, preliminary = vehicles.car_stock_yearly()
    shares, absolute = _by_category(stock)
    if preliminary:
        logger.info("Charts: car stock ends {:02d}/{}, provisional", month, year)

    chart("share_fuel_stock_cars",
          title="AT registered cars: fuel type share",
          unit="Share [%]",
          data=shares,
          source=STOCK_SOURCE,
          note=STOCK_NOTE,
          preliminary=preliminary,
          time_res="yearly",
          view="toggle", initial="bar")

    chart("number_fuel_stock_cars",
          title="AT registered cars: fuel type absolute number",
          unit="Number",
          data=absolute,
          source=STOCK_SOURCE,
          note=STOCK_NOTE,
          preliminary=preliminary,
          time_res="yearly",
          view="toggle", initial="bar")


def _lorries():
    for stem, vehicle_class, label in [
            ("le3p5", "VG_LE3P5", "≤3.5t"),
            ("gt3p5", "LOR_GT3P5", ">3.5t")]:
        counts, _years = vehicles.yearly_by_fuel(
            "lorries", "road_eqr_lormot", options={"vehicle": vehicle_class})
        shares, absolute = _by_category(counts)

        chart("share_fuel_new_lorries_%s" % stem,
              title="AT new lorry (%s) registrations: fuel type share" % label,
              unit="Share [%]",
              data=shares,
              source=LORRY_SOURCE,
              time_res="yearly",
              view="toggle", initial="bar")

        chart("number_fuel_new_lorries_%s" % stem,
              title="AT new lorry (%s) registrations: fuel type absolute number" % label,
              unit="Number",
              data=absolute,
              source=LORRY_SOURCE,
              time_res="yearly",
              view="toggle", initial="bar")


# ---------------------------------------------------------------------------
# Rail
# ---------------------------------------------------------------------------

def _rail():
    tracks = _rail_tracks()

    chart("rail_tracks_abs",
          title="AT rail track lengths: absolute length",
          unit="Length (km)",
          data=tracks,
          source=RAIL_SOURCE,
          time_res="yearly",
          view="toggle", initial="line")

    chart("rail_tracks_rel",
          title="AT rail track lengths: shares electrified/non-electrified",
          unit="Share (%)",
          # shares(), not a hand-rolled division: the open-coded version divided
          # without the * 100 while the chart was labelled "Share (%)", so the
          # site reported Austria's rail network as 0.74 % electrified.
          data=S.shares(tracks),
          source=RAIL_SOURCE,
          time_res="yearly",
          view="toggle", initial="bar")


def _rail_tracks():
    """Track length, electrified and not, against the total.

    Total starts in 1900 rather than 1990 so the chart carries the whole
    available history; the electrified/non-electrified split only exists from
    1990, which is why the three are read separately and aligned.
    """
    def lines(infrastructure, start_year):
        return eurostat.yearly(name="rail_tracks", code="rail_if_line_tr",
                               options={"tra_infr": infrastructure,
                                        "n_tracks": "Total [TOTAL]"},
                               unit="KM", start_year=start_year,
                               label="rail_tracks")

    parts = [
        ("Electrified", lines("Electrified railway lines [RL_ELC]", 1990)),
        ("Non-electrified", lines("Non-electrified railway lines [RL_NELC]", 1990)),
        ("Total", lines("Total [TOTAL]", 1900)),
    ]
    return S.wrap([(label, data["data"]["rail_tracks"]) for label, data in parts])
