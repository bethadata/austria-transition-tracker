# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 18:24:03 2024

@author: Bernhard
"""

from plot_single import plot_single_go, plot_with_toggle
from utils import filter_unfcc
import pandas as pd 
from datetime import datetime 
import numpy as np

def plot(): 
    years, emissions = filter_unfcc.get_data(sector = "5.F.1 - Long-term Storage of C in Waste Disposal Sites")
    times = pd.date_range(start = datetime(year = years[0], month = 1, day = 1),
                          end = datetime(year = years[-1], month = 1, day = 1),
                          periods = len(years))

    data_plot = {"data": {"Austria ": {"x": times,
                                       "y": np.array(emissions)/1e6}}}

    plot_with_toggle(title = "Austrian long-term Storage of C in Waste Disposal Sites",
                  filename = "AT_timeseries_long_term_storage_C_disposal",
                  unit = "Emissions (Mt<sub>CO2e</sub>)",
                  data_plot = data_plot,
                  time_res = "yearly",
                  show_plot = False,
                  unit_fac= 1, 
                  source_text = "EEA greenhouse gases — data viewer (sector: 5.F.1)",
                  initial_visible = "bar",
                  save = True)
    
    
    
if __name__ == "__main__": 
    plot()