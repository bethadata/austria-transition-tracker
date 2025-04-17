# -*- coding: utf-8 -*-
"""
Created on Thu May  2 19:57:38 2024

@author: Bernhard
"""

import plotly.express as px
from plot_single import plot_single_go, plot_with_toggle
import numpy as np 

from utils import filter_national_inventory

data_land_use = filter_national_inventory.get_land_uses()

         
colors = px.colors.qualitative.Dark2.copy()
colors.remove('rgb(231,41,138)')  #removes pink 
### swap two colors 
colors[3],colors[4] = colors[4],colors[3]
colors_plot = {"Forests": colors[0], 
               "Crop land": colors[1],
               "Grass land": colors[2],
               "Wet land": colors[3],
               "Settlements": colors[4],
               "Other": colors[6]}

plot_with_toggle(title = "<b>Land use</b>: absolute area",
              filename = "AT_timeseries_land_use_abs",
              unit = "Area (kHa)", 
              data_plot = data_land_use,
              time_res = "yearly",
              show_plot = False,
              colors = list([colors_plot[cat] for cat in data_land_use["data"]]),
              source_text = "National Inventory Report",
              initial_visible = "bar",
              plotmax_fac = 1)
    
tot_area = np.zeros(len(data_land_use["data"]["Forests"]["x"]))
for cat in data_land_use["data"]: 
    tot_area += data_land_use["data"][cat]["y"]
data_land_use_rel = {"data": {}}
for cat in data_land_use["data"]: 
    data_land_use_rel["data"][cat] = {"x": data_land_use["data"][cat]["x"],
                                       "y": data_land_use["data"][cat]["y"]*100/tot_area}
    
    
plot_with_toggle(title = "<b>Land use</b>: shares",
              filename = "AT_timeseries_land_use_rel",
              unit = "Share (%)", 
              data_plot = data_land_use_rel,
              time_res = "yearly",
              show_plot = False,
              colors = list([colors_plot[cat] for cat in data_land_use["data"]]),
              source_text = "National Inventory Report",
              initial_visible = "bar",
              plotmax_fac = 1)