# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 19:11:17 2024

@author: Bernhard
"""

import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd 
from datetime import datetime 
import matplotlib.pyplot as plt 
from sklearn.linear_model import LinearRegression

import filter_fossil_extrapolation 
from filter import filter_uba_sectoral_emisssions
from filter import filter_eurostat_monthly

data_gas = filter_eurostat_monthly(name = "gas",
                       start_year = 2013,
                        code = "NRG_CB_GASM",
                        options = {"unit": "TJ_GCV",
                                  "nrg_bal": "Inland consumption - calculated as defined in MOS GAS [IC_CAL_MG]"},
                        unit = "TJ_GCV", movmean = 12)

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


# data_raw = filter_fossil_extrapolation.get_data_fossils()
emissions = filter_uba_sectoral_emisssions()

first_year = 2013 
last_year = 2022

times = pd.date_range(start = datetime(year = first_year, month = 1, day =1),
                      end = datetime(year = last_year, month = 1, day = 1),
                      freq="YS")

gas_years = np.zeros(len(times))  
gasoline_years = np.zeros(len(times))
diesel_years = np.zeros(len(times)) 
heating_oil_years = np.zeros(len(times)) 
coal_elec_years = np.zeros(len(times)) 
coal_coke_ovens_years = np.zeros(len(times)) 
coal_industry_years = np.zeros(len(times)) 

emissions_energy_years = np.zeros(len(times))

for t in range(len(times)): 
    time = times[t]
    for tm in range(len(data_gas["data"]['Monthly']["x"])):
        time_m = data_gas["data"]['Monthly']["x"][tm]
        
        if time_m.year == time.year: 
            gas_years[t] += data_gas["data"]['Monthly']["y"][tm]/3600
            gasoline_years[t] += data_gasoline["data"]['Monthly']["y"][tm]
            diesel_years[t] += data_diesel_road["data"]['Monthly']["y"][tm]
            heating_oil_years[t] += data_heating_oil["data"]['Monthly']["y"][tm]
            coal_elec_years[t] += data_coal_elec["data"]['Monthly']["y"][tm]
            coal_coke_ovens_years[t] += data_coal_coke_ovens["data"]['Monthly']["y"][tm]
            coal_industry_years[t] += data_coal_industry["data"]['Monthly']["y"][tm]


    ind = emissions["data"]["Transport"]["x"].index(time)
    emissions_energy_years[t] = (emissions["data"]["Transport"]["y"][ind]+
                                 emissions["data"]["Buildings"]["y"][ind]+
                                 emissions["data"]["Energy & Industry"]["y"][ind])

### regression 
x = np.zeros((len(times), 5))
for t in range(len(times)): 
    x[t][0] = gas_years[t]
    x[t][1] = diesel_years[t]+gasoline_years[t]
    x[t][2] = heating_oil_years[t]
    x[t][3] = coal_elec_years[t]
    x[t][4] = coal_coke_ovens_years[t]+coal_industry_years[t]
    # x[t][6] = coal_industry_years[t]
    # x[t][1] = gasoline_years[t]

            
     
y = emissions_energy_years
model = LinearRegression(positive = True).fit(x[:], y[:])
# model = LinearRegression().fit(x[2:], y[2:])
# model = LinearRegression().fit(x[1:], y[1:])

r_sq = model.score(x[:], y[:])
print(f"coefficient of determination: {r_sq}")
print(f"slope: {model.coef_}")

# model_emissions = []
# for t in range(len(times)): 
model_emissions = (model.predict(x))

plt.figure()
plt.plot(times, emissions_energy_years, label = "Actual emissions")
plt.plot(times, model_emissions, label = "Model emissions")
plt.ylim([0, max(emissions_energy_years)*1.1])
plt.grid()
plt.tight_layout()



    



# fig,ax = plt.subplots(2, 2, squeeze = True)
# fig.set_size_inches(8,5)

# ax[0][0].plot(coal_years, emissions_energy_years)
# ax[0][0].grid()
# ax[0][0].set_title("Coal")

# ax[1][0].plot(gas_years, emissions_energy_years)
# ax[1][0].grid()
# ax[1][0].set_title("Gas")

# ax[0][1].plot(oil_years, emissions_energy_years)
# ax[0][1].grid()
# ax[0][1].set_title("Oil")

# plt.tight_layout()