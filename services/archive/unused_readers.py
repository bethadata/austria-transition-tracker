# -*- coding: utf-8 -*-
"""ARCHIVED 2026-08-25 -- two readers from the old `plot/utils/filter.py`
that nothing called.

`filter_eurostat_monnthly_to_yearly` (the double-n is original) aggregated a
monthly eurostat series to years and extrapolated the incomplete final year from
the average of the same partial-year ratio over the previous ten years. It was
reachable only from its own `__main__` block. Its method survives in
`models/fossil_extrapolation.py`, which does the same thing per fuel and is what
the yearly consumption charts actually use -- so this is superseded rather than
merely unused, and is kept because the two differ in how they pick the training
window (a fixed ten years here, everything since 2013 there).

`filter_uba_emissions` split the Klimadashboard total into the Effort Sharing and
Emissions Trading halves. Nothing has ever plotted it, though two chart modules
imported it. Kept because the ESR/ETS split is a real and useful cut of the
Austrian total -- if a chart for it is ever wanted, this is the reader, and note
that it reads a *different* UBA export ("Treibhausgas-Emissionen und Zielpfade")
from the one `sources/umweltbundesamt.py` uses.
"""

import os
from datetime import datetime

import numpy as np
import pandas as pd


def filter_eurostat_monnthly_to_yearly(name = "oil",
                                       code = "NRG_CB_OILM",
                                       geo = "AT",
                                       start_year = 2013,
                                       options = {"unit": "THS_T",
                                                  "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                                  "siec": "Oil products [O4600]"},
                                       unit = "THS_T"): 
    
    data_file = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                              "../../data_raw/eurostat/%s_%s_%s.xlsx" %(geo, name, code)))
    data_file = data_file.fillna(0)
    data_trim = pandas_to_dict(data_file, options, unit)

    
    ### find last key with columns 
    for year in [1990+i for i in range(100)]:
        for month in range(1, 13):
            if "%i-%02i" %(year, month) in data_file: 
                if sum(data_file["%i-%02i" %(year, month)] > 0):
                    last_year = year 
                    last_month = month 

    times_months = pd.date_range(start = datetime(year = start_year, month = 1, day =1),
                          end = datetime(year = last_year+1, month = 1, day = 1),
                          freq="ME")
    
    times_years = pd.date_range(start = datetime(year = start_year, month = 1, day =1),
                          end = datetime(year = last_year, month = 1, day = 1),
                          freq="YS")
    
    data = {year: 0 for year in range(start_year, last_year+1)}
    data_months = {}
    for time in times_months: 
        if time.year == last_year and time.month > last_month: 
            pass 
        else: 
            time_key = "%i-%02i" %(time.year, time.month)
            
            if time_key not in data_file.keys(): value = 0 
            else: value = data_trim[time_key]
            
            data[time.year] += value 
            data_months[time] = value
    
    values_extrapolated = np.zeros(len(times_years))
    

    if last_month != 12: 
        ### extrapolation of missing months 
        ### get medium consumption increase of months to last month of previous three years 
        facs = []
        years_to_consider = 10
        for year in [last_year-years_to_consider+i for i in range(years_to_consider)]:
            consumption_year = data[year]
            consumption_to_last_month = 0
            for time in times_months: 
                if time.year == year and time.month <= last_month: 
                    consumption_to_last_month += data_months[time]
            facs.append(consumption_year/consumption_to_last_month)
        fac_mean = np.mean(np.array(facs))
        values_extrapolated[-1] = data[last_year] * fac_mean 
        
    std_estimator = np.sqrt(np.var(facs)*len(facs)/(len(facs)-1))
    std_energy = data[last_year] * std_estimator/2
          
    data_out = {"data": {"Actual consumption": {"x": times_years,
                                                "y": [data[year] for year in data]},
                        "Extrapolated": {"x": times_years,
                                          "y": values_extrapolated}
                        },
                "meta": {"last_year": last_year,
                         "last_month": last_month,
                         "fac_mean": fac_mean,
                         "facs": facs,
                         "std_estimator": std_estimator,
                         "std_energy": std_energy,
                         "code": code}
                }

    return data_out


def filter_uba_emissions(): 
    data_raw = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                              "../../data_raw/umweltbundesamt/Treibhausgas-Emissionen und Zielpfade.xlsx"),
                              decimal = ",", skiprows = 2)
                         
    data_raw = data_raw.fillna(0)
    times = pd.to_datetime(data_raw["Jahr"], format = "%Y")[data_raw["Gesamte THG"] > 0]
    emissions_total = data_raw["Gesamte THG"][data_raw["Gesamte THG"] > 0]

    times_ets = times[data_raw["THG nach KSG"] > 0]
    emissions_esr =  data_raw["THG nach KSG"][data_raw["THG nach KSG"] > 0]
    emissions_ets = emissions_total[data_raw["THG nach KSG"] > 0] - emissions_esr 
    
    data = {"data": {"GHG emissions total": {"x": times,
                                             "y": emissions_total},
                     "GHG emissions Effor Sharing": {"x": times_ets,
                                           "y": emissions_esr},
                     "GHG emissions ETS": {"x": times_ets,
                                           "y": emissions_ets}}
            }
       
    return data
