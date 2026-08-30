# -*- coding: utf-8 -*-
"""The fossil fuel table: where each fuel is read from, and what burning it emits.

Pure reference data, and the reason it is its own module: these numbers are the
physical assumptions behind every emissions figure the site computes itself --
the whole "monthly CO2 by fuel" chart and the front page's emissions projection
rest on them. Buried at the top of a 870-line plotting module they read as setup;
here they can be checked.

Each entry carries:

  dataset / code  the eurostat monthly cache to read (`sources/eurostat.py`)
  options         the dimension filter that picks this fuel's row
  ncv             net calorific value, in TJ per unit of the reported quantity,
                  i.e. the factor that turns the reported figure into energy
  emission_factor t CO2 per TJ

so that emissions = quantity * ncv * emission_factor / 1000, giving Mt CO2.

**Natural gas needs one conversion the others do not.** eurostat reports it in
TJ *gross* calorific value, and emission factors are per TJ *net*, so its `ncv`
is the GCV-to-NCV ratio (0.03723 / 0.03914) rather than a calorific value --
divided by 1000 to land in the same units as the rest. Getting this wrong
inflates Austrian gas emissions by about 5%, which is small enough to look
plausible.
"""

#: Natural gas: TJ per thousand m3, gross and net. The ratio, not the values, is
#: what the table uses.
TJ_GCV_PER_1000M3 = 0.03914
TJ_NCV_PER_1000M3 = 0.03723

_GCV_TO_NCV = TJ_NCV_PER_1000M3 / TJ_GCV_PER_1000M3 / 1000

#: fuel -> where to read it and what it emits. `chart_id` is the id stem of the
#: two per-fuel consumption charts (`consumption_<stem>_monthly` / `_yearly`).
FUELS = {
    "Natural gas": {
        "chart_id": "natural_gas",
        "dataset": "gas",
        "code": "NRG_CB_GASM",
        "options": {"unit": "TJ_GCV",
                    "nrg_bal": "Inland consumption - calculated as defined in MOS GAS [IC_CAL_MG]"},
        "ncv": _GCV_TO_NCV,
        "emission_factor": 55.4,
    },
    "Gasoline": {
        "chart_id": "gasoline",
        "dataset": "oil",
        "code": "NRG_CB_OILM",
        "options": {"unit": "THS_T",
                    "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                    "siec": "Motor gasoline [O4652]"},
        "ncv": 0.0418,
        "emission_factor": 71.3,
    },
    "Diesel": {
        "chart_id": "diesel",
        "dataset": "oil",
        "code": "NRG_CB_OILM",
        "options": {"unit": "THS_T",
                    "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                    "siec": "Road diesel [O46711]"},
        "ncv": 0.0424,
        "emission_factor": 71.3,
    },
    "Heating gas oil": {
        "chart_id": "heating_oil",
        "dataset": "oil",
        "code": "NRG_CB_OILM",
        "options": {"unit": "THS_T",
                    "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                    "siec": "Heating and other gasoil [O46712]"},
        "ncv": 0.0428,
        "emission_factor": 75,
    },
    "Refinery gas": {
        "chart_id": "refinery_gas",
        "dataset": "oil",
        "code": "NRG_CB_OILM",
        "options": {"unit": "THS_T",
                    "nrg_bal": "Refinery fuel [RF]",
                    "siec": "Refinery gas [O4610]"},
        "ncv": 0.0306,
        "emission_factor": 64,
    },
    "Hard coal - electricity sector": {
        "chart_id": "hard_coal_electricity",
        "dataset": "coal",
        "code": "NRG_CB_SFFM",
        "options": {"unit": "THS_T",
                    "nrg_bal": "Transformation input - electricity and heat generation - main activity producers [TI_EHG_MAP]",
                    "siec": "Hard coal [C0100]"},
        "ncv": 0.0299,
        "emission_factor": 95,
    },
    "Hard coal - industry sector": {
        "chart_id": "hard_coal_industry",
        "dataset": "coal",
        "code": "NRG_CB_SFFM",
        "options": {"unit": "THS_T",
                    "nrg_bal": "Final consumption - industry sector [FC_IND]",
                    "siec": "Hard coal [C0100]"},
        "ncv": 0.0299,
        "emission_factor": 84,
    },
    "Hard coal - coke ovens": {
        "chart_id": "hard_coal_coke_ovens",
        "dataset": "coal",
        "code": "NRG_CB_SFFM",
        "options": {"unit": "THS_T",
                    "nrg_bal": "Transformation input - coke ovens [TI_CO]",
                    "siec": "Hard coal [C0100]"},
        "ncv": 0.0299,
        "emission_factor": 84,
    },
    "Coke oven coke": {
        "chart_id": "coke_oven_coke",
        "dataset": "coal",
        "code": "NRG_CB_SFFM",
        "options": {"unit": "THS_T",
                    "nrg_bal": "Gross inland deliveries - calculated [GID_CAL]",
                    "siec": "Coke oven coke [C0311]"},
        "ncv": 0.0282,
        "emission_factor": 94.6,
    },
}

#: The three groups the emissions-by-fuel charts stack. Order is palette order.
CATEGORIES = {
    "Gas": ["Natural gas"],
    "Oil": ["Gasoline", "Diesel", "Heating gas oil", "Refinery gas"],
    "Coal": ["Coke oven coke", "Hard coal - coke ovens",
             "Hard coal - industry sector", "Hard coal - electricity sector"],
}

#: eurostat's unit codes, as they should read on a y axis.
UNIT_LABELS = {"THS_T": "1000 tons",
               "TJ_GCV": "TJ<sub>GCV</sub>"}

#: The two fuels eurostat reports with the biofuel blend included. Their charts
#: split the blend out, so the fossil half is not overstated.
BLENDED = {"Diesel": "Blended biodiesels [R5220B]",
           "Gasoline": "Blended biogasoline [R5210B]"}


def emission_factor(fuel):
    """Mt CO2 per reported unit of `fuel`."""
    spec = FUELS[fuel]
    return spec["ncv"] * spec["emission_factor"] / 1000


def unit_label(fuel):
    return UNIT_LABELS[FUELS[fuel]["options"]["unit"]]
