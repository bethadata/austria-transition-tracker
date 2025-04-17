# -*- coding: utf-8 -*-
"""
Created on Fri May  3 15:22:44 2024

@author: Bernhard
"""

import numpy as np
import plotly.express as px


from plot_single import plot_single_go, plot_with_toggle
from utils import filter_statcube 

colors = px.colors.qualitative.Dark2.copy()
colors.remove('rgb(231,41,138)')  #removes pink 
colors[3],colors[4] = colors[4],colors[3]
colors = ["rgb(0,0,0)"]+colors

def plot(): 
    
    #### MEAT ####
    colors = px.colors.qualitative.Dark2.copy()
    colors.remove('rgb(231,41,138)')  #removes pink 
    colors[3],colors[4] = colors[4],colors[3]
    colors = ["rgb(0,0,0)"]+colors
    
    data = filter_statcube.filter_meat(size = "Menschlicher Verzehr", fac = 1e3)
    plot_with_toggle(title = "Meat consumption in Austria: total",
                  filename = "AT_timeseries_meat_consumption_total",
                  unit = "Meat consumption (kt)", 
                  data_plot = data,
                  time_res = "yearly",
                  colors = colors, 
                  show_plot = False,
                  legend_inside = False,
                  source_text = "Statcube, Statistik Austria",
                  info_text = "Human consumption per year",
                  initial_visible = "bar",
                  plotmax_fac = 1.1)
    
    
    data = filter_statcube.filter_meat(size = "Menschlicher Verzehr pro Kopf in kg", fac = 1)
    plot_with_toggle(title = "Meat consumption in Austria: per capita",
                  filename = "AT_timeseries_meat_consumption_per_capita",
                  unit = "Meat consumption per capita (kg)", 
                  data_plot = data,
                  time_res = "yearly",
                  colors = colors, 
                  show_plot = False,
                  legend_inside = False,
                  source_text = "Statcube, Statistik Austria",
                  info_text = "Human consumption per capita in kg",
                  initial_visible = "bar",
                  plotmax_fac = 1.1)
    
    
    
    #### MILK ####
    colors = px.colors.qualitative.Dark2.copy()
    colors.remove('rgb(231,41,138)')  #removes pink 
    colors[3],colors[4] = colors[4],colors[3]
    
    data = filter_statcube.filter_milk(size = "NAHRUNGSVERBRAUCH", fac = 1e3)
    plot_with_toggle(title = "Milk product consumption in Austria: total",
                  filename = "AT_timeseries_milk_consumption_total",
                  unit = "Milk consumption (t)", 
                  data_plot = data,
                  time_res = "yearly",
                  colors = colors, 
                  show_plot = False,
                  legend_inside = False,
                  source_text = "Statcube, Statistik Austria",
                  info_text = "Food consumption per year",
                  initial_visible = "bar",
                  plotmax_fac = 1.1)
    
    
    data = filter_statcube.filter_milk(size = "Nahrungsverbrauch pro Kopf in kg", fac = 1)
    plot_with_toggle(title = "Milk product consumption in Austria: per capita",
                  filename = "AT_timeseries_milk_consumption_per_capita",
                  unit = "Milk consumption per capita (kg)", 
                  data_plot = data,
                  time_res = "yearly",
                  colors = colors, 
                  show_plot = False,
                  legend_inside = False,
                  source_text = "Statcube, Statistik Austria",
                  info_text = "Food consumption per capita in kg",
                  initial_visible = "bar",
                  plotmax_fac = 1.1)
    
    
if __name__ == "__main__": 
    plot()