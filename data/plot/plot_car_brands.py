# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 13:20:43 2025

@author: Bernhard
"""

import os 
import pandas as pd 
import numpy as np 
from datetime import datetime 
from plot_single import plot_with_toggle
import plotly.express as px

def plot(): 
    
    bold = px.colors.qualitative.Bold
    pastel = px.colors.qualitative.Pastel
    bold.append(pastel[0])
    
        
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    months = {"Jaenner": 1, "Februar": 2, "Maerz": 3, "April": 4,
              "Mai": 5, "Juni": 6, "Juli": 7, "August": 8,
              "September": 9, "Oktober": 10, "November": 11, "Dezember": 12}
    
    
    data_monthly = {}
    for year in years: 
        file_found = False 
        for month in reversed(months):   
            filename = "NeuzulassungenFahrzeugeJaennerBis%s%i" %(month, year)
            filepath = os.path.join(os.path.dirname(__file__), 
                "../data_raw/statistik_austria/Fahrzeuge/%s.xlsx" %(filename))
            if os.path.exists(filepath) and not file_found:
                file_found = True 
                month_list = list(months.keys())
                for month_name in month_list[:month_list.index(month)+1]:
                    time = pd.to_datetime(datetime(year = year, 
                                    month = month_list.index(month_name)+1,
                                    day = 1))
                    data_monthly[time] = {}
                    
                    if month_name == "Maerz": month_name = "März"
                    elif month_name == "Jaenner": month_name = "Jänner"
                                        
                    data_sa = pd.read_excel(filepath, sheet_name = month_name)
                    number = data_sa["Unnamed: 1"]
                    column = data_sa["Tabelle 1a: Kfz-Neuzulassungen"]
                    
                    for c in range(len(column)): 
                        if str(column[c]) == "Tabelle 7: Pkw-Neuzulassungen nach TOP 10 Marken und Typen mit Elektroantrieb": 
                            for c1 in range(2,13):
                                label = str(column[c+c1])
                                label = str(column[c+c1]).rstrip(" ")
                                data_monthly[time][label] = float(number[c+c1])
    
    
    ### find top 10: 
    brands = {}
    for time in data_monthly: 
        for brand in data_monthly[time]:
            if brand not in brands: 
                brands[brand] = data_monthly[time][brand]
            else: 
                brands[brand] += data_monthly[time][brand]
    brands = dict(sorted(brands.items(), key=lambda item: item[1], reverse=True))
    brands_list = list(brands.keys())
    top12 = [brands_list[m] for m in range(12)]                
    top12.remove('Sonstige Pkw mit Elektroantrieb')
    
    data_plot = {"data": {brand: {"x": [], "y": []} for brand in top12}}
    data_plot["data"]["other"] = {"x": [], "y": []}
    
    for time in data_monthly: 
        for brand in top12: 
            data_plot["data"][brand]["x"].append(time)
            if brand in data_monthly[time]: 
                data_plot["data"][brand]["y"].append(data_monthly[time][brand])
            else: 
                data_plot["data"][brand]["y"].append(0)
                
        for brand in data_monthly[time]:
            value_other = 0 
            if brand not in top12: 
                value_other += data_monthly[time][brand]
                
        data_plot["data"]["other"]["x"].append(time)
        data_plot["data"]["other"]["y"].append(value_other) 
    
    
    values_total = []
    for t in range(len(data_plot["data"]["other"]["x"])): 
        value_total = 0 
        for brand in data_plot["data"]: 
            value_total += data_plot["data"][brand]["y"][t]
        values_total.append(value_total) 
        
    data_plot["data"]["Total"] = {"x": data_plot["data"]["other"]["x"],
                                  "y": values_total} 
       
    
    data_rel = {"data": {}}
    for brand in data_plot["data"]: 
        if brand != "Total": 
            data_rel["data"][brand] = {"x": data_plot["data"][brand]["x"],
                                       "y": np.array(data_plot["data"][brand]["y"])*100/np.array(data_plot["data"]["Total"]["y"])}
    
    plot_with_toggle(title = "<b>AT new monthly BEV registrations:</b> car brands absolute number",
                  filename = "AT_timeseries_monthly_registrations_brands_absolute",
                  unit = "Number", 
                  data_plot = data_plot,
                  show_plot = False,
                  colors = bold,
                  source_text = "Statistik Austria",
                  info_text = "Only top 10 car brands (over all years) shown.",
                  initial_visible = "bar",
                  plotmax_fac = 1)
    
        
    plot_with_toggle(title = "<b>AT new monthly BEV registrations:</b> car brands shares",
                  filename = "AT_timeseries_monthly_registrations_brands_shares",
                  unit = "Share (%)", 
                  data_plot = data_rel,
                  show_plot = False,
                  colors = bold,
                  source_text = "Statistik Austria",
                  info_text = "Only top 10 car brands (over all years) shown.",
                  initial_visible = "bar",
                   plotmax_fac = 1)    
                    
    ### yearly 
    data_yearly_raw = {brand: {} for brand in data_plot["data"]}
    for brand in data_plot["data"]: 
        years = []
        for t in range(len(data_plot["data"][brand]["x"])): 
            date = data_plot["data"][brand]["x"][t]
            if date.year in years: 
                date_save = datetime(year = date.year, month = 1, day = 1)
            else: 
                years.append(date.year) 
                date_save = date 
                data_yearly_raw[brand][date_save] = 0 
            data_yearly_raw[brand][date_save] += data_plot["data"][brand]["y"][t]
    
    
    data_yearly_abs = {"data": {cat: {"x": np.array([date for date in data_yearly_raw[cat]]),
                         "y": np.array([data_yearly_raw[cat][date] for date in data_yearly_raw[cat]])}
                       for cat in data_yearly_raw}}  
    
    data_yearly_rel = {"data": {}}
    for cat in data_yearly_abs["data"]: 
        if cat != "Total": 
            data_yearly_rel["data"][cat] = {"x": data_yearly_abs["data"][cat]["x"],
                                            "y": data_yearly_abs["data"][cat]["y"]*100/data_yearly_abs["data"]["Total"]["y"]}    
    
    
    plot_with_toggle(title = "<b>AT new yearly BEV registrations:</b> car brands absolute number",
                  filename = "AT_timeseries_yearly_registrations_brands_absolute",
                  unit = "Number", 
                  data_plot = data_yearly_abs,
                  show_plot = False,
                  colors = bold,
                  source_text = "Statistik Austria",
                  info_text = "Only top 10 car brands (over all years) shown.",
                  initial_visible = "bar",
                  plotmax_fac = 1)
    
        
    plot_with_toggle(title = "<b>AT new yearly BEV registrations:</b> car brands shares",
                  filename = "AT_timeseries_yearly_registrations_brands_shares",
                  unit = "Share (%)", 
                  data_plot = data_yearly_rel,
                  show_plot = True,
                  colors = bold,
                  source_text = "Statistik Austria",
                  info_text = "Only top 10 car brands (over all years) shown.",
                  initial_visible = "bar",
                  plotmax_fac = 1)    
                
    
if __name__ == "__main__": 
    plot()
