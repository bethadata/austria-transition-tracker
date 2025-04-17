# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 19:05:38 2024

@author: Bernhard
"""

import numpy as np

from plot_single import plot_single_go
from utils.filter import filter_eurostat_monthly
from utils.filter import filter_eurostat_yearly
from utils import filter_national_inventory

def plot():
    
    ### Natural gas use industry 
    data_ng_industry_final_en = filter_eurostat_yearly(name = "natural_gas_en_bal",
                                code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - industry sector - non-energy use [FC_IND_NE]",
                                        "siec": "Natural gas [G3000]"},
                              unit = "GWH")
    
    
    data_ng_industry_final_non_en = filter_eurostat_yearly(name = "natural_gas_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - industry sector - energy use [FC_IND_E]",
                                        "siec": "Natural gas [G3000]"},
                              unit = "GWH")
 
    data_ng_en_industry_en_use = filter_eurostat_yearly(name = "natural_gas_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Energy sector - energy use [NRG_E]",
                                        "siec": "Natural gas [G3000]"},
                              unit = "GWH")

    data_ng_elec_generation = filter_eurostat_yearly(name = "natural_gas_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Transformation input - electricity and heat generation - energy use [TI_EHG_E]",
                                        "siec": "Natural gas [G3000]"},
                              unit = "GWH")
    
    
    ### coal use industry 
    data_coal_industry_final_en = filter_eurostat_yearly(name = "coal_en_bal",
                                code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - energy use [FC_E]",
                                        "siec": "Solid fossil fuels [C0000X0350-0370]"},
                              unit = "GWH")
    
    data_coal_industry_trans_inp = filter_eurostat_yearly(name = "coal_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Transformation input - energy use [TI_E]",
                                        "siec": "Solid fossil fuels [C0000X0350-0370]"},
                              unit = "GWH")

    data_coal_industry_trans_out = filter_eurostat_yearly(name = "coal_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Transformation output [TO]",
                                        "siec": "Solid fossil fuels [C0000X0350-0370]"},
                              unit = "GWH")
    
    data_coal_elec_generation = filter_eurostat_yearly(name = "coal_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Transformation input - electricity and heat generation - energy use [TI_EHG_E]",
                                        "siec": "Solid fossil fuels [C0000X0350-0370]"},
                              unit = "GWH")
    

    ### oil use industry 
    # data_oil_industry_final_non_en = filter_eurostat_yearly(name = "oil_en_bal",
    #                             code = "nrg_bal_c",
    #                           options = {"unit": "GWH",
    #                                     "nrg_bal": "Final consumption - industry sector - non-energy use [FC_IND_NE]",
    #                                     "siec": "Oil and petroleum products (excluding biofuel portion) [O4000XBIO]"},
    #                           unit = "GWH")
    
    
    data_oil_industry_final_en = filter_eurostat_yearly(name = "oil_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Final consumption - industry sector - energy use [FC_IND_E]",
                                        "siec": "Oil and petroleum products (excluding biofuel portion) [O4000XBIO]"},
                              unit = "GWH")
 
    data_oil_en_industry_en_use = filter_eurostat_yearly(name = "oil_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Energy sector - energy use [NRG_E]",
                                        "siec": "Oil and petroleum products (excluding biofuel portion) [O4000XBIO]"},
                              unit = "GWH")
    
    data_oil_elec_generation = filter_eurostat_yearly(name = "oil_en_bal",
                                  code = "nrg_bal_c",
                              options = {"unit": "GWH",
                                        "nrg_bal": "Transformation input - electricity and heat generation - energy use [TI_EHG_E]",
                                        "siec": "Oil and petroleum products (excluding biofuel portion) [O4000XBIO]"},
                              unit = "GWH")    
    
    
    
    # data_plot = {"data": {"Natural gas - Industry": 
    #                           {"x": data_ng_industry_final_en["data"]["natural_gas_en_bal"]["x"],
    #                             "y": (np.array(data_ng_industry_final_en["data"]["natural_gas_en_bal"]["y"])+
    #                                 np.array(data_ng_industry_final_non_en["data"]["natural_gas_en_bal"]["y"])+
    #                                 np.array(data_ng_en_industry_en_use["data"]["natural_gas_en_bal"]["y"]))/1000},
    #                       "Coal use - Industry": 
    #                             {"x": data_coal_industry_final_en["data"]["coal_en_bal"]["x"],
    #                               "y": (np.array(data_coal_industry_final_en["data"]["coal_en_bal"]["y"])+
    #                                   np.array(data_coal_industry_trans_inp["data"]["coal_en_bal"]["y"])-
    #                                   np.array(data_coal_industry_trans_out["data"]["coal_en_bal"]["y"]))/1000},
    #                       "Oil use -Industry": 
    #                             {"x": data_oil_industry_final_en["data"]["oil_en_bal"]["x"],
    #                               "y": (np.array(data_oil_industry_final_en["data"]["oil_en_bal"]["y"])+
    #                                   np.array(data_oil_en_industry_en_use["data"]["oil_en_bal"]["y"]))/1000}
    #                           }}
                          
        
    # plot_single_go(title = "<b>Natural gas / Coal / Oil</b>: yearly consumption Industry sector ", 
    #                 filename = "AT_timeseries_natural_gas_coal_oil_industry",
    #                 unit = "Energy (TWh)", 
    #                 data_plot=data_plot,
    #                 show_plot = False,
    #                 legend_inside = False,
    #                 time_res = "yearly",
    #                 source_text = "Source: eurostat (nrg_bal_c)<br>"
    #                 "Natural gas: final consumption energy + non-energy use + energy sector energy use<br>"
    #                 "Coal: final consumption energy use + transformation input - transformation output<br>"
    #                 "Oil final consumption energy use + energy sector energy use")


    data_plot = {"data": {"Natural gas - Electricity & District Heat generation": 
                              {"x": data_ng_elec_generation["data"]["natural_gas_en_bal"]["x"],
                              "y": np.array(data_ng_elec_generation["data"]["natural_gas_en_bal"]["y"])/1000},
                          "Coal - Electricity & District Heat generation": 
                                                    {"x": data_coal_elec_generation["data"]["coal_en_bal"]["x"],
                                                    "y": np.array(data_coal_elec_generation["data"]["coal_en_bal"]["y"])/1000},  
                          "Oil - Electricity & District Heat generation": 
                                                  {"x": data_oil_elec_generation["data"]["oil_en_bal"]["x"],
                                                  "y": np.array(data_oil_elec_generation["data"]["oil_en_bal"]["y"])/1000},   
                              }}
                          

    plot_single_go(title = "<b>Natural gas / Coal / Oil</b>: yearly consumption Electrcity & Disricht Heat generation ", 
                    filename = "AT_timeseries_natural_gas_coal_oil_energy_sector",
                    unit = "Energy (TWh)", 
                    data_plot=data_plot,
                    show_plot = False,
                    legend_inside = False,
                    time_res = "yearly",
                    source_text = "eurostat (nrg_bal_c)")      
    
    
    
if __name__ == "__main__": 
    plot()