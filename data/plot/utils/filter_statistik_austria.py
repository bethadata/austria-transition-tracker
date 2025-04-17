# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 19:41:17 2024

@author: Bernhard
"""

import pandas as pd 
import os 
from datetime import datetime 



def filter_heating_systems(start_year = 2003,
                     end_year= 2022): 

    data_raw = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                      "../../data_raw/statistik_austria/08Heizungen2003Bis2022NachBundeslaendernUndVerwendetemEnergietraeger.xlsx"),
                             skiprows = 1, sheet_name = "Österreich")
    data_raw = data_raw.fillna(0)
    data_raw = data_raw.replace("Kohle, Koks, Briketts2", "Kohle, Koks, Briketts")
    
    heaters = {"Heat pumps / solar": "Solar, Wärmepumpen",
               "Biomass": "Holz, Hackschnitzel, Pellets, Holzbriketts",
               "District heat": "Fernwärme",
               "Electricity": "Strom",
               "Natural gas": "Erdgas",
               "Oil": "Heizöl, Flüssiggas",
               "Coal": "Kohle, Koks, Briketts"}
    
    times = list(pd.date_range(start = datetime(year = start_year, month = 1, day =1),
                          end = datetime(year = end_year, month = 1, day = 1),
                          freq="YS"))
    
    data = {"data": {}}
    for heater in heaters: 
        data["data"][heater] = {"x": times,
                        "y": []}
        
        for index in data_raw.index: 
            if data_raw["Energieträger"][index] == heaters[heater]: 
                data["data"][heater]["y"].append(data_raw['Anzahl Wohnungen („Hauptwohnsitze“) insgesamt'][index])
                data["data"][heater]["y"].append(data_raw['Anzahl Wohnungen („Hauptwohnsitze“) insgesamt'][index])
             
    data_rel = {"data": {heater: {} for heater in heaters}}
    
    for heater in heaters: 
        data_rel["data"][heater]["x"] = data["data"][heater]["x"]
        data_rel["data"][heater]["y"] = []
        for t in range(len(data["data"][heater]["x"])):
            data_rel["data"][heater]["y"].append(data["data"][heater]["y"][t] / (
                sum([data["data"][h]["y"][t] for h in heaters])))
             
                
    return data_rel, data 






