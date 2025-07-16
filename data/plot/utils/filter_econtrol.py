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
    data = pd.read_csv(fp, skiprows = [0,1,3,4,5,6,7,8,9,10,11,12,13], encoding =  "ISO-8859-1", 
                        sep=";", header =  [0],engine = "python", decimal = ",")
    
    times = pd.to_datetime(data["TS_ID"])
    first_time = datetime(year=2015, month =1, day=1)
    times_plot =  list(pd.to_datetime(times[times >=first_time]))
                       
    data_plot = {"data": {}}
    for energy_type, codes in {"PV": ["#248357"],
                                "Wind": ["#89101"],
                                "Hydro": ["#999003m"],
                              "Biomass":  ["#99105m", "#156858m"],
                              "Natural gas": ["#89097m"],
                              "Coal": ["#89093m"],
                               "Waste": [],
                              "Other": ["#89096m","#89095m", "#99106m","#113482m", "#89103m"],
                              "Domestic consumption": ["#89110m"]
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
        
