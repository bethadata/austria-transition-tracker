# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 20:17:32 2024

@author: Bernhard
"""


import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd 
from datetime import datetime 
import matplotlib.pyplot as plt 
from sklearn.linear_model import LinearRegression

from filter import filter_uba_sectoral_emisssions
from filter import filter_eurostat_monthly

TJ_GCV_to_Miom3 = 39.139 #TJ_GCV / Miom3 
TJ_NCV_to_1000m3 = 0.03723 #TJ_NCV / 1000M3
TJ_to_TWh = 3600 #TJ / TWh
fac_ng = (TJ_NCV_to_1000m3*1000)/TJ_GCV_to_Miom3/TJ_to_TWh



data_gas = filter_eurostat_monthly(name = "gas",
                       start_year = 2013,
                        code = "NRG_CB_GASM",
                        options = {"unit": "TJ_GCV",
                                  "nrg_bal": "Inland consumption - calculated as defined in MOS GAS [IC_CAL_MG]"},
                        unit = "TJ_GCV", movmean = 12)



data_refinery_gas = filter_eurostat_monthly(name = "oil",
                        start_year = 2013,
                        code = "NRG_CB_OILM",
                        options = {"unit": "THS_T",
                                  "nrg_bal": "Refinery fuel [RF]",
                                  "siec": "Refinery gas [O4610]"},
                        unit = "THS_T", movmean = 12)


data_gasoline = filter_eurostat_monthly(name = "oil",
                        start_year = 2013,
                        code = "NRG_CB_OILM",
                        options = {"unit": "THS_T",
                                  "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                  "siec": "Motor gasoline (excluding biofuel portion) [O4652XR5210B]"},
                        unit = "THS_T", movmean = 12)

data_diesel_road = filter_eurostat_monthly(name = "oil",
                        start_year = 2013,
                        code = "NRG_CB_OILM",
                        options = {"unit": "THS_T",
                                  "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                  "siec": "Road diesel [O46711]"},
                        unit = "THS_T", movmean = 12)

data_biodiesel = filter_eurostat_monthly(name = "oil",
                        start_year = 2013,
                        code = "NRG_CB_OILM",
                        options = {"unit": "THS_T",
                                  "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                  "siec": "Blended biodiesels [R5220B]"},
                        unit = "THS_T", movmean = 12)

data_heating_oil = filter_eurostat_monthly(name = "oil",
                        start_year = 2013,
                        code = "NRG_CB_OILM",
                        options = {"unit": "THS_T",
                                  "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                  "siec": "Heating and other gasoil [O46712]"},
                        unit = "THS_T", movmean = 12)

data_coal_elec = filter_eurostat_monthly(name = "coal",
                        code = "NRG_CB_SFFM",
                        start_year = 2013,
                        options = {"unit": "THS_T",
                                  "nrg_bal": "Transformation input - electricity and heat generation - main activity producers [TI_EHG_MAP]",
                                  "siec": "Hard coal [C0100]"},
                        unit = "THS_T", movmean = 12)

data_coal_coke_ovens = filter_eurostat_monthly(name = "coal",
                    code = "NRG_CB_SFFM",
                    start_year = 2013,
                    options = {"unit": "THS_T",
                              "nrg_bal": "Transformation input - coke ovens [TI_CO]",
                              "siec": "Hard coal [C0100]"},
                    unit = "THS_T", movmean = 12)

data_coal_industry = filter_eurostat_monthly(name = "coal",
                    code = "NRG_CB_SFFM",
                    start_year = 2013,
                    options = {"unit": "THS_T",
                              "nrg_bal": "Final consumption - industry sector [FC_IND]",
                              "siec": "Hard coal [C0100]"},
                    unit = "THS_T", movmean = 12)

data_coke_oven_coke = filter_eurostat_monthly(name = "coal",
                    code = "NRG_CB_SFFM",
                    start_year = 2013,
                    options = {"unit": "THS_T",
                              "nrg_bal": "Final consumption - industry sector - iron and steel [FC_IND_IS]",
                              "siec": "Coke oven coke [C0311]"},
                    unit = "THS_T", movmean = 12)

emissions = filter_uba_sectoral_emisssions()

first_year = 2013 
last_year = 2022

times = pd.date_range(start = datetime(year = first_year, month = 1, day =1),
                      end = datetime(year = last_year, month = 1, day = 1),
                      freq="YS")

gas_years = np.zeros(len(times))  
gasoline_years = np.zeros(len(times))
diesel_years = np.zeros(len(times)) 
biodiesel_years = np.zeros(len(times))
heating_oil_years = np.zeros(len(times)) 
hard_coal_elec_years = np.zeros(len(times)) 
hard_coal_coke_ovens_years = np.zeros(len(times)) 
hard_coal_industry_years = np.zeros(len(times)) 
coke_oven_coke_years = np.zeros(len(times))

emissions_energy_years = np.zeros(len(times))

for t in range(len(times)): 
    time = times[t]
    for tm in range(len(data_gas["data"]['Monthly']["x"])):
        time_m = data_gas["data"]['Monthly']["x"][tm]
        
        if time_m.year == time.year: 
            gas_years[t] += data_gas["data"]['Monthly']["y"][tm]
            gasoline_years[t] += data_gasoline["data"]['Monthly']["y"][tm]
            diesel_years[t] += data_diesel_road["data"]['Monthly']["y"][tm]
            biodiesel_years[t] += data_biodiesel["data"]['Monthly']["y"][tm]
            heating_oil_years[t] += data_heating_oil["data"]['Monthly']["y"][tm]
            hard_coal_elec_years[t] += data_coal_elec["data"]['Monthly']["y"][tm]
            hard_coal_coke_ovens_years[t] += data_coal_coke_ovens["data"]['Monthly']["y"][tm]
            hard_coal_industry_years[t] += data_coal_industry["data"]['Monthly']["y"][tm]
            coke_oven_coke_years[t] += data_coke_oven_coke["data"]['Monthly']["y"][tm]

    ind = emissions["data"]["Transport"]["x"].index(time)
    emissions_energy_years[t] = (emissions["data"]["Transport"]["y"][ind]+
                                 emissions["data"]["Buildings"]["y"][ind]+
                                 emissions["data"]["Energy & Industry"]["y"][ind])


### all values based on NCV 
f_gas = 55.4 #t_CO2 / TJ (NIV)
f_hard_coal_elec = 95 #t_CO2 / TJ (NIV)
f_harc_coal_industry = 84 #t_CO2 / TJ (NIV)
f_coke_oven_coke = 94.60 #t_CO2 / TJ (NIV)
f_oil = 71.3 #t_CO2 / TJ (NIV)
f_heating_oil = 75 #t_CO2 / TJ (NIV)

LHV_hard_coal = 0.0299 #TJ / t (SA)
LHV_coke_oven_coke = 0.0282 #TJ / t (SA) 
LHV_diesel = 0.0424 #TJ / t (SA) 
LHV_gasoline = 0.0418 #TJ / t (SA)
LHV_heating_oil = 0.0428 #TJ / t (SA)

em_gas = np.array(gas_years) * fac_ng * f_gas * 3600 / 1e6 
em_gasoline = np.array(gasoline_years) *1000 * LHV_gasoline * f_oil / 1e6 
em_diesel = (np.array(diesel_years)-np.array(biodiesel_years)) *1000 * LHV_diesel * f_oil / 1e6 
em_heating_oil = np.array(heating_oil_years) *1000 * LHV_heating_oil * f_heating_oil / 1e6 
em_hard_coal_elec_years = np.array(hard_coal_elec_years) *1000 * LHV_hard_coal  * f_hard_coal_elec / 1e6 
em_hard_coal_industry_years = np.array(hard_coal_industry_years) *1000 * LHV_hard_coal  * f_hard_coal_elec / 1e6 
em_hard_coal_coke_ovens_years = np.array(hard_coal_coke_ovens_years) *1000 * LHV_hard_coal  * f_hard_coal_elec / 1e6 
em_coke_oven_coke_years = np.array(coke_oven_coke_years) *1000 * LHV_coke_oven_coke  * f_coke_oven_coke / 1e6 

em_model = (em_gas+
            em_gasoline+
            em_diesel+
            em_heating_oil+
            em_hard_coal_elec_years+
            em_hard_coal_industry_years+
            em_hard_coal_coke_ovens_years+
            em_coke_oven_coke_years)

fig,ax = plt.subplots(3,1)
fig.set_size_inches(7,3*3)

ax[0].plot(times, emissions_energy_years, label = "Actual emissions") 
ax[0].plot(times, em_model, label = "Emissions model") 
ax[0].legend() 
ax[0].set_ylim([0, max(emissions_energy_years)*1.1])

plt.tight_layout() 

# emissions_model = (np.array(gas_years) * fac_ng * f_gas * 3600 + 
#                    np.arraa(gasoline_years) * f_oil * 1000 + 
#                    np.array()

