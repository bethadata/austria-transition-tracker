# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 14:07:07 2024

@author: Bernhard
"""




import pandas as pd 
import numpy as np 
import os 
from datetime import datetime 

def filter_econtrol_monthly(): 
    
    filepath = "../../data_raw/e_control/el_dataset_mn.csv"
    fp = open(os.path.join(os.path.dirname(__file__), filepath), "r", encoding='ISO-8859-1')
    data = pd.read_csv(fp, skiprows = range(1,14), encoding =  "ISO-8859-1", 
                        sep=";", header =  [0],engine = "python", decimal = ",")
    
    times = pd.to_datetime(data["Header & Timestamp"])
    first_time = datetime(year=2015, month =1, day=1)
    times_plot =  list(pd.to_datetime(times[times >=first_time]))
                       
    data_plot = {"data": {}}
    for energy_type, codes in {"PV": ["84"],
                                "Wind": ["83"],
                                "Hydro": ["72"],
                              "Biomass":  ["79", "80"],
                              "Natural gas": ["77"],
                              "Coal": ["73", "74"],
                               "Waste": [],
                              "Other": ["75","76", "81","85", "88"],
                              "Domestic consumption": ["92"]
                              }.items(): 
        
        data_codes = np.zeros(len(times_plot))
        for code in codes: 
            data_energy = data[code]
            
            if len(data_codes) > 0: 
                data_codes += np.array(data_energy[times >=first_time])
            else: 
                data_codes = np.array(data_energy[times >=first_time])
                
        data_plot["data"][energy_type] = {"x": times_plot, 
                                          "y": data_codes/1e6}  ###TWh
    return data_plot 
        
