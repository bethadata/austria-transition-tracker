# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 11:03:47 2024

@author: Bernhard
"""

import numpy as np 
import os 
import matplotlib.pyplot as plt 


def cut_data_fossil(data_monthly): 
    start_year = 2013
    
    times_months = data_monthly["data"]["Monthly"]["x"]
    values =  data_monthly["data"]["Monthly"]["y"]
    
    start_year = times_months[0].year 
    last_year = times_months[-1].year 
    last_month = times_months[-1].month 
    
    data_years = {year: 0 for year in range(start_year, last_year+1)}
    data_years_to_last_month = {year: 0 for year in range(start_year, last_year+1)}
    data_years_from_last_month = {year: 0 for year in range(start_year, last_year+1)}

    data_months = {}
    for t in range(len(times_months)):
        time = times_months[t]
        value = values[t]
        
        if time.year == last_year and time.month > last_month: 
            pass 
        else: 
            data_years[time.year] += value
            data_months[time] = value
            
            if time.month <= last_month: 
                data_years_to_last_month[time.year] += value
            else: 
                data_years_from_last_month[time.year] += value
            
    data_out  =    {"values_months": data_months,
                    "values_year": data_years,
                    "values_year_to_last_month": data_years_to_last_month,
                    "values_year_from_last_month": data_years_from_last_month,
                    "meta": {"last_year": last_year,
                             "last_month": last_month}}
        
    return data_out   
        
    
    
def extrapolate_data_fossil(data,
                            last_year_raw = None,
                            last_month_raw = None): 
    """ extrapolates data from a specific year to the missing months, using previous months
        increase factors """ 
        
    data_out = {}
    if last_year_raw == None: 
        last_year = data["meta"]["last_year"]
    else: 
        last_year = last_year_raw 
        
    if last_month_raw == None: 
        last_month = data["meta"]["last_month"]
    else: 
        last_month = last_month_raw 

    values_extrapolated = np.zeros(len(data["values_year"]))
    
    ### consider as much year as possible for model 
    years_to_consider = last_year-2013
    
    facs = []
    for year in [last_year-years_to_consider+i for i in range(years_to_consider)]:
        consumption_year = data["values_year"][year]
        if consumption_year > 0: 
            consumption_to_last_month = 0
            for time in data["values_months"]: 
    
                if time.year == year and time.month <= last_month: 
                    consumption_to_last_month += data["values_months"][time]
            facs.append(consumption_year/consumption_to_last_month)
    
    
    consumption_to_last_month_last_year = 0
    for time in data["values_months"]: 
        if time.year == last_year and time.month <= last_month: 
            consumption_to_last_month_last_year += data["values_months"][time]
            
    fac_mean = np.mean(np.array(facs))
    std_estimator = np.sqrt(np.var(facs)*len(facs)/(len(facs)-1.5))
    values_extrapolated[-1] = consumption_to_last_month_last_year * fac_mean 
    std_energy =  consumption_to_last_month_last_year *  std_estimator
    
    data_out  = {"facs": facs, 
                "consumption_to_month": consumption_to_last_month_last_year,
                "fac_mean": fac_mean, 
                "std_estimator": std_estimator,
                "std_energy": std_energy,
                "extrapolated_year": values_extrapolated[-1]}
    
    return data_out 


    
def plot_data_fossils(data, year_plot = 2022): 
    """ plot the extrapolated data for various starting months to demonstrate the model """ 
    
    # fig, ax = plt.subplots(len(data), 1)
    # fig.set_size_inches(9,len(data)*4)
    
    fig, ax = plt.subplots(1, len(data))
    fig.set_size_inches(7*len(data),4)

    if len(data) == 1: ax = [ax]
    p = 0
    for siec in data: 
        last_months = data[siec]["last_months"]
        extrapolated_data = np.array(data[siec]["extrapolated_data"])
        std_data = np.array(data[siec]["std_data"])
        actual_consumption_year = data[siec]["actual_consumption_year"]
        actual_consumption_to_month = data[siec]["actual_consumption_to_month"]
        
        ax[p].plot(last_months, extrapolated_data,
                      label = "Extrapolated yearly")
        ax[p].fill_between(last_months, 
                              extrapolated_data-std_data,
                              extrapolated_data+std_data,
                              alpha = 0.3,
                              label = "Estimated standard deviation")
        ax[p].plot(last_months, actual_consumption_year, label = "Actual yearly")
        ax[p].plot(last_months, actual_consumption_to_month, label = "Actual monthly (cumulated)")
        
        ax[p].set_title("Consumption estimation: %s %i" %(siec, year_plot))
        ax[p].legend()
        ax[p].grid()
        ax[p].set_ylim([0, max(extrapolated_data)*1.3])
        ax[p].set_xlabel("Month")
        ax[p].set_ylabel("Consumption (%s)" %(data[siec]["unit"]))
        p += 1 


    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), 
                             "../../../docs/assets/images/fossil_fuel_consumption_estimation.png"), dpi = 400)
            


