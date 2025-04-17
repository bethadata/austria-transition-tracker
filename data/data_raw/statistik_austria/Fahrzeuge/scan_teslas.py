# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 13:20:43 2025

@author: Bernhard
"""

import os 
import pandas as pd 
from datetime import datetime 
from plot_single import plot_single_go, plot_with_toggle


years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
months = {"Jaenner": 1, "Februar": 2, "Maerz": 3, "April": 4,
          "Mai": 5, "Juni": 6, "Juli": 7, "August": 8,
          "September": 9, "Oktober": 10, "November": 11, "Dezember": 12}


labels = {"Tesla": "Tesla"}

### check which file exists 
data_monthly = {}
for year in years: 
    file_found = False 
    for month in reversed(months):   
        filename = "NeuzulassungenFahrzeugeJaennerBis%s%i" %(month, year)
        filepath = "%s.xlsx" %(filename)
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

                for label in labels: 
                    found = False 
                    for c in range(len(column)): 
                        
                        if str(column[c]) == "Tabelle 7: Pkw-Neuzulassungen nach TOP 10 Marken und Typen mit Elektroantrieb": 
                            found = True 
                            5
                            for c1 in range(2,13):
                                label = str(column[c+c1])
                                label = str(column[c+c1]).rstrip(" ")
                                data_monthly[time][label] = float(number[c+c1])
                            
                        # if str(column[c])[:len(labels[label])] == labels[label] and found: 
                        #     data_monthly[label][time] = float(number[c])
         
### find top 10: 
marks = {}
for time in data_monthly: 
    for mark in data_monthly[time]:
        if mark not in marks: 
            marks[mark] = data_monthly[time][mark]
        else: 
            marks[mark] += data_monthly[time][mark]
marks = dict(sorted(marks.items(), key=lambda item: item[1], reverse=True))
marks_list = list(marks.keys())
top12 = [marks_list[m] for m in range(12)]                

for time in data_monthly: 
    data_monthly[time]["other"] = 0
    data_monthly[time]["total"] = 0
    for mark in data_monthly[time]:  
        if mark not in top12: 
            data_monthly[time]["other"] += data_monthly[time][mark]
        data_monthly[time]["total"] += data_monthly[time][mark]
        
data_monthly_2 = {}
for mark in top12: 
    data_monthly_2[mark] = {}
    for time in data_monthly: 
        if mark in data_monthly[time]: 
            data_monthly_2[mark][time] = data_monthly[time][mark]
        else: 
            data_monthly_2[mark][time] = 0
        
for time in data_monthly:
    data_monthly_2["other"][time] = data_monthly[time]["other"]
            
    
    
data_plot = {"data": data_monthly_2}

plot_with_toggle(title = "<b>New monthly car registrations:</b> car brand",
              filename = "AT_timeseries_monthly_registrations_brands",
              unit = "Number", 
              data_plot = data_plot,
              show_plot = True,
              colors = list([colors_cars[label] for label in colors_cars]),
              source_text = "eurostat (road_eqr_carpda) & Statistik Austria",
              initial_visible = "area",
              plotmax_fac = 1)
            

# import matplotlib.pyplot as plt 
# times = [time for time in data_monthly]
# values = []
# for time in times: 
#     if "Tesla" in data_monthly[time]: 
#         values.append(data_monthly[time]["Tesla"])
#     else: 
#         values.append(0)
# plt.plot(times, values) 

