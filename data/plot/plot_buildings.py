# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 19:05:38 2024

@author: Bernhard
"""

import numpy as np

from plot_single import plot_single_go, plot_with_toggle
from utils.filter import filter_eurostat_monthly
from utils.filter import filter_eurostat_yearly
from utils import filter_statistik_austria
from utils import filter_national_inventory


import plotly.express as px


set2 = px.colors.qualitative.Dark2
colors_cars = {"Electric": set2[0],
          "Hybrid plugin": set2[1],
          "Hybrid": set2[2],
          "Diesel": set2[6],
          "Gasoline": set2[7],
          "Other": set2[5]}

colors_heatings = {"Heat pumps / solar": set2[2],
               "Biomass": set2[4],
               "District heat": set2[1],
               "Electricity": set2[0],
               "Natural gas": set2[5],
               "Oil": set2[6],
               "Coal": set2[7]}



def plot():
    ### Heating oil 
    data_oil = filter_eurostat_monthly(name = "oil",
                                  start_year = 2010,
                                  code = "NRG_CB_OILM",
                              options = {"unit": "THS_T",
                                        "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                        "siec": "Heating and other gasoil [O46712]"},
                              unit = "THS_T", movmean = 12)
    
    plot_single_go(title = "<b>Heating oil</b>: monthly consumption Austria", 
                    filename = "AT_timeseries_heating_oil_consumption",
                    unit = "Oil (thousand tons)", 
                    data_plot=data_oil,
                    show_plot = False)   
    
    
    
    ### Natural gas use buildings 
    data_households = filter_eurostat_yearly(name = "natural_gas_en_bal",
                                code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - other sectors - households - energy use [FC_OTH_HH_E]",
                                        "siec": "Natural gas [G3000]"},
                              unit = "GWH")
    
    
    data_tertiary = filter_eurostat_yearly(name = "natural_gas_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - other sectors - commercial and public services - energy use [FC_OTH_CP_E]",
                                        "siec": "Natural gas [G3000]"},
                              unit = "GWH")
 
    data_plot = {"data": {"Natural gas": 
                          {"x": data_households["data"]["natural_gas_en_bal"]["x"],
                          "y": (np.array(data_households["data"]["natural_gas_en_bal"]["y"])+
                                np.array(data_tertiary["data"]["natural_gas_en_bal"]["y"]))/1000 
                          }}
                  }
        
        
    ### Oil use buildings 
    data_households = filter_eurostat_yearly(name = "oil_en_bal",
                                code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - other sectors - households - energy use [FC_OTH_HH_E]",
                                        "siec": "Oil and petroleum products (excluding biofuel portion) [O4000XBIO]"},
                              unit = "GWH")
    
    
    data_tertiary = filter_eurostat_yearly(name = "oil_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - other sectors - commercial and public services - energy use [FC_OTH_CP_E]",
                                        "siec": "Oil and petroleum products (excluding biofuel portion) [O4000XBIO]"},
                              unit = "GWH")
 
    data_plot["data"]["Oil"] = {"x": data_households["data"]["oil_en_bal"]["x"],
                                "y": (np.array(data_households["data"]["oil_en_bal"]["y"])+
                                      np.array(data_tertiary["data"]["oil_en_bal"]["y"]))/1000}
    
        
    ### Coal use buildings 
    data_households = filter_eurostat_yearly(name = "coal_en_bal",
                                code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - other sectors - households - energy use [FC_OTH_HH_E]",
                                        "siec": "Solid fossil fuels [C0000X0350-0370]"},
                              unit = "GWH")
    
    
    data_tertiary = filter_eurostat_yearly(name = "coal_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - other sectors - commercial and public services - energy use [FC_OTH_CP_E]",
                                        "siec": "Solid fossil fuels [C0000X0350-0370]"},
                              unit = "GWH")

    data_plot["data"]["Coal"] = {"x": data_households["data"]["coal_en_bal"]["x"],
                                "y": (np.array(data_households["data"]["coal_en_bal"]["y"])+
                                      np.array(data_tertiary["data"]["coal_en_bal"]["y"]))/1000}    
                 
    
                         
    plot_single_go(title = "<b>Natural gas / Oil / Coal</b>: yearly consumption Building sector ", 
                    filename = "AT_timeseries_natural_gas_oil_coal_buildings",
                    unit = "Energy (TWh)", 
                    data_plot=data_plot,
                    show_plot = False,
                    time_res = "yearly",
                    source_text = "Source: eurostat (nrg_bal_c)") 


    ### heating systems buildings 
    data_rel, data_abs  = filter_statistik_austria.filter_heating_systems()
    
    plot_with_toggle(title = "<b>Heating system shares</b>: main types",
                  filename = "AT_timeseries_share_heating_systems",
                  unit = "Share [%]", 
                  data_plot = data_rel,
                  time_res = "yearly",
                  show_plot = False,
                  colors = list([colors_heatings[label] for label in colors_heatings]),
                  source_text = "Source: Statistik Austria",
                  plot_type = "area",
                  plotmax_fac = 1,
                  initial_visible = "bar")
        
    plot_with_toggle(title = "<b>Heating system absolute numbers</b>: main types",
                  filename = "AT_timeseries_number_heating_systems",
                  unit = "Number", 
                  data_plot = data_abs,
                  time_res = "yearly",
                  show_plot = False,
                    colors = list([colors_heatings[label] for label in colors_heatings]),
                  source_text = "Source: Statistik Austria",
                  initial_visible = "bar")

         
    
if __name__ == "__main__": 
    plot()