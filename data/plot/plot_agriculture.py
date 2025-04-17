# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 19:03:26 2024

@author: Bernhard
"""

import numpy as np

from plot_single import plot_single_go
from utils.filter import filter_eurostat_monthly
from utils.filter import filter_eurostat_yearly
from utils import filter_national_inventory

def plot():
    ### Pig meat data 
    data_filtered = filter_eurostat_monthly(name = "meat",
                                      code = "apro_mt_pheadm",
                              options = {"meat": "Pigmeat [B3100]",
                                        "meatitem": "Slaughterings [SLAUGHT]"},
                              unit = "THS_T", movmean = 12)
    
    plot_single_go(title = "<b>Pigs</b>: monthly sloughtered ", 
                        filename = "AT_timeseries_sloughtered_pig_meat",
                        unit = "Meat (thousand tons)", 
                        data_plot=data_filtered)


    ### Chicken meat data 
    data = filter_eurostat_monthly(name = "meat",
                              code = "apro_mt_pheadm",
                              options = {"meat": "Chicken [B7100]",
                                        "meatitem": "Slaughterings [SLAUGHT]"},
                              unit = "THS_T", movmean = 12,
                              start_year = 2008)

    plot_single_go(title = "<b>Chicken</b>: monthly slaughtered ", 
                        filename = "AT_timeseries_sloughtered_chicken_meat",
                        unit = "Meat (thousand tons)", 
                        data_plot=data)


    ### Cattle meat data 
    data = filter_eurostat_monthly(name = "meat",
                              code = "apro_mt_pheadm",
                              options = {"meat": "Bovine meat [B1000]",
                                        "meatitem": "Slaughterings [SLAUGHT]"},
                              unit = "THS_T", movmean = 12)

    plot_single_go(title = "<b>Cattle/cows</b>: monthly slaughtered ", 
                        filename = "AT_timeseries_sloughtered_cattle_meat",
                        unit = "Meat (thousand tons)", 
                        data_plot=data)

    ### cow milk 
    data = filter_eurostat_monthly(name = "milk",
                              code = "apro_mk_colm",
                              options = {"dairyprod": "Raw cows' milk delivered to dairies [D1110D]"},
                              unit = "THS_T", movmean = 12)

    plot_single_go(title = "<b>Raw cow milk</b>: monthly deliveries ", 
                        filename = "AT_timeseries_raw_cow_milk",
                        unit = "Milk (thousand tons)", 
                        data_plot=data)    
    
    
    ### inorganic fertilizers 
    data = filter_eurostat_yearly(name = "fertilizer",
                              code = "aei_fm_usefert",
                              options = {"nutrient": "N"},
                              unit = "T",
                              start_year = 2000)

    plot_single_go(title = "<b>Inorganic fertilizer:</b> Nitrogen consumption ", 
                        filename = "AT_timeseries_fertilizer_nitrogen",
                        unit = "Tons", 
                        data_plot=data,
                        time_res = "yearly",
                        show_plot = False)        
    
    
    ### livestock population 
    data_cows = filter_eurostat_yearly(name = "bovine_population",
                              code = "apro_mt_lscatl",
                              options = {"animals": "Live bovine animals [A2000]"},
                              unit = "THS_HD",
                              start_year = 1993,
                              end_year = 2024)
    
    data_pigs = filter_eurostat_yearly(name = "pig_population",
                              code = "apro_mt_lspig",
                              options = {"animals": "Live swine, domestic species [A3100]"},
                              unit = "THS_HD",
                              start_year = 1994,
                              end_year = 2024)
    
    data_sheep = filter_eurostat_yearly(name = "sheep_population",
                              code = "apro_mt_lssheep",
                              options = {"animals": "Live sheep [A4100]"},
                              unit = "THS_HD",
                              start_year = 1993,
                              end_year = 2024)        
    
    data_goat = filter_eurostat_yearly(name = "goat_population",
                              code = "apro_mt_lsgoat",
                              options = {"animals": "Live goats [A4200]"},
                              unit = "THS_HD",
                              start_year = 1997,
                              end_year = 2024)    
    
    data_plot = {"data": {"Cow / cattle": {"x": data_cows["data"]["bovine_population"]["x"],
                                           "y": data_cows["data"]["bovine_population"]["y"]},
                          "Pig": {"x": data_pigs["data"]["pig_population"]["x"],
                                   "y": data_pigs["data"]["pig_population"]["y"]},
                           "Sheep": {"x": data_sheep["data"]["sheep_population"]["x"],
                                    "y": data_sheep["data"]["sheep_population"]["y"]},
                           "Goat": {"x": data_goat["data"]["goat_population"]["x"],
                                    "y": data_goat["data"]["goat_population"]["y"]},
                           }
                 }
    
    
    plot_single_go(title = "<b>Cow/Pig/Sheep/Goats:</b> population", 
                        filename = "AT_timeseries_animal_feestock_population",
                        unit = "Thousand", 
                        data_plot=data_plot,
                        time_res = "yearly",
                        source_text = "eursotat (apro_mt_lscatl, apro_mt_lspig, apro_mt_lssheep, apro_mt_lsgoat)",
                        show_plot = False)        
    
 
if __name__ == "__main__": 
    plot()
    
