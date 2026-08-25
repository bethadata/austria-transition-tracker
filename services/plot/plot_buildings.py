# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 19:05:38 2024

@author: bethadata
"""

import numpy as np
from loguru import logger 
from .plot_single import plot_single_go, plot_with_toggle
from .utils.filter import filter_eurostat_monthly
from .utils.filter import filter_eurostat_yearly
from .utils import filter_statistik_austria
from .utils import filter_national_inventory


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
    logger.info("Plotting Buildings ...")
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
    
    
    

    ### heating systems buildings 
    data_rel, data_abs  = filter_statistik_austria.filter_heating_systems()
    
    plot_with_toggle(title = "<b>Heating system shares</b>: main types",
                  filename = "AT_timeseries_share_heating_systems",
                  unit = "Share [%]", 
                  data_plot = data_rel,
                  time_res = "yearly",
                  show_plot = False,
                  colors = list([colors_heatings[label] for label in colors_heatings]),
                  source_text = "Statistik Austria",
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
                  source_text = "Statistik Austria",
                  initial_visible = "bar")

         
    
if __name__ == "__main__": 
    plot()