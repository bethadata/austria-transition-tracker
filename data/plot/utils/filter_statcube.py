# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 09:51:56 2024

@author: Bernhard
"""

import pandas as pd 
import numpy as np 
from datetime import datetime 
import os 

def filter_meat(size = "Menschlicher Verzehr", fac = 1): 
    
    filepath = "../../data_raw/statistik_austria/meat_consumption_StatCube_table_2024-10-20.csv"
    fp = open(os.path.join(os.path.dirname(__file__), filepath), "r")
    data = pd.read_csv(fp, skiprows = 6, encoding =  "ISO-8859-1", on_bad_lines='skip', 
                       sep=";", skipfooter=1,engine = "python", decimal = ",")
    
    meat_types = {"Total": "Fleisch insgesamt",
                  "Chicken / Poultry": "Geflügelfleisch",
                  "Pigmeat": "Schweinefleisch",
                  "Cows / cattle": "Rind- und Kalbfleisch"}
    
    data_plot = {"data": {}}
    
    ### find last year in database 
    firstyearfound = False 
    for year in [1990+i for i in range(200)]: 
        if year in np.array(data["Jahr"]) and not firstyearfound: 
            first_year = year
            firstyearfound = True 
        elif year in np.array(data["Jahr"]):
            last_year = year 
            
    times = pd.date_range(
        start = datetime(year = first_year, month = 1, day = 1),
        end = datetime(year = last_year, month = 1, day = 1),
        freq="YS")
    
    
    for meat in meat_types: 
        values = data[np.logical_and(data["Produkte"] == meat_types[meat],
                                     data["Werte"] == size)]
        values_sorted = []
        for time in times: 
            values_sorted.append(float(values[values["Jahr"]==time.year]["Anzahl"].iloc[0]))
        
        data_plot["data"][meat] = {"x": times, 
                                   "y": np.array(values_sorted)/fac}
        
    data_plot["data"]["Other"] = {"x": times, 
                                  "y": np.array(data_plot["data"]["Total"]["y"]
                                                -data_plot["data"]["Chicken / Poultry"]["y"]
                                                -data_plot["data"]["Pigmeat"]["y"]
                                                -data_plot["data"]["Cows / cattle"]["y"]
                                                )}
    return data_plot 

        
def filter_milk(size = "Menschlicher Verzehr", fac = 1): 
    
    filepath = "../../data_raw/statistik_austria/milk-consumption_StatCube_table_2024-11-24_09-46-17.csv"
    fp = open(os.path.join(os.path.dirname(__file__), filepath), "r")
    data = pd.read_csv(fp, skiprows = 6, encoding =  "ISO-8859-1", on_bad_lines='skip', 
                       sep=";", skipfooter=1,engine = "python", decimal = ",")
    
    milk_types = {"Milk": "Konsummilch",
                  "Cheese": "Käse",
                  "Butter": "Butter",
                  "Cream": "Obers und Rahm"}
    
    data_plot = {"data": {}}
    
    ### find last year in database 
    firstyearfound = False 
    for year in [1990+i for i in range(200)]: 
        if year in np.array(data["Jahr"]) and not firstyearfound: 
            first_year = year
            firstyearfound = True 
        elif year in np.array(data["Jahr"]):
            last_year = year 
            
    times = pd.date_range(
        start = datetime(year = first_year, month = 1, day = 1),
        end = datetime(year = last_year, month = 1, day = 1),
        freq="YS")
    
    
    for milk in milk_types: 
        values = data[np.logical_and(data["Produkte"] == milk_types[milk],
                                     data["Werte"] == size)]
        values_sorted = []
        for time in times: 
            values_sorted.append(float(values[values["Jahr"]==time.year]["Anzahl"].iloc[0]))
        
        data_plot["data"][milk] = {"x": times, 
                                   "y": np.array(values_sorted)/fac}
        
    # data_plot["data"]["Other"] = {"x": times, 
    #                               "y": np.array(data_plot["data"]["Total"]["y"]
    #                                             -data_plot["data"]["Chicken / Poultry"]["y"]
    #                                             -data_plot["data"]["Pigmeat"]["y"]
    #                                             -data_plot["data"]["Cows / cattle"]["y"]
    #                                             )}
    return data_plot 