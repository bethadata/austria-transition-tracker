# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 17:11:04 2024

@author: Bernhard
"""

import plotly.express as px
from plot_single import plot_single_go, plot_with_toggle
import numpy as np 

from utils import filter_national_inventory
from utils import filter_unfcc
from utils.filter import filter_eurostat_energy_balance
from utils.filter import filter_uba_sectoral_emisssions
from utils.filter import filter_uba_emissions


def plot(show_plot=False): 
    
    dark2 = px.colors.qualitative.Dark2
    colors_siecs ={"Transport": dark2[2],
                    "Energy % Industry": dark2[1],
                    "Agriculture": dark2[4],
                    "Buildings": dark2[5],
                    "Waste": dark2[7],
                    "Fluorinated Gases": dark2[3],
                    "LULUCF": dark2[0]}    
    colors = list([colors_siecs[label] for label in colors_siecs])
    
    
    ### Emissions total 
    data_total = filter_uba_emissions()
    emissions = filter_uba_sectoral_emisssions()
        
    data_total = np.zeros(len(emissions["data"]["Buildings"]["x"]))
    for sector in emissions["data"]: 
        data_total += np.array(emissions["data"][sector]["y"])
    emissions["data"]["Total"] = {"x": emissions["data"]["Buildings"]["x"],
                                  "y": np.array(data_total)}
    
    
    plot_with_toggle(title = "<b>Austrian GHG emissions</b> by sectors (without LULUCF)",
                  filename = "AT_timeseries_co2_emissions_sectors",
                  unit = "Emissions (Mt<sub>CO2e</sub>)", 
                  data_plot = emissions,
                  time_res = "yearly",
                  show_plot = False,
                  colors = colors,
                  source_text = "Umweltbundesamt (Klimadashboard)",
                  plot_type = "area",
                  plotmax_fac = 1.05,
                  initial_visible = "bar")

    ### relative emissions 
    emissions_rel = {"data": {}}
    for sector in emissions["data"]: 
        if sector != "Total": 
            emissions_rel["data"][sector] = {"x": emissions["data"][sector]["x"],
                                             "y": (np.array(emissions["data"][sector]["y"])*100
                                                   /np.array(emissions["data"]["Total"]["y"]))}

    plot_with_toggle(title = "<b>Austrian GHG emission shares</b> by sectors (without LULUCF)",
                  filename = "AT_timeseries_co2_emissions_sectors_shares",
                  unit = "Emission share (%)", 
                  data_plot = emissions_rel,
                  time_res = "yearly",
                  show_plot = False,
                  colors = colors,
                  source_text = "Umweltbundesamt (Klimadashboard)",
                  plot_type = "area",
                  plotmax_fac = 1,
                  initial_visible = "bar")                                                                   


    ### Emissions sectors 
    sectors = {"Buildings": {"file": "buildings"},
                "Energy & Industry": {"file": "energy_industry"},
                "Agriculture":  {"file": "agriculture"},
                "Waste":  {"file": "waste"},
                "Transport":  {"file": "transport"}, 
                "Fluorinated Gases": {"file": "fluorinated_gases"}, 
                "LULUCF": {"file": "lulucf"}
                }
    
    for sector in sectors: 
        ### emissions with sub-sectors 
        # data_emissions = filter_national_inventory.filt(sector =  sector)
        data_emissions = filter_unfcc.filt(sector =  sector)

        if sector in ["LULUCF"]:
            source_text = "Umweltbundesamt AUSTRIA'S ANNUAL GREENHOUSE GAS INVENTORY 1990–2023"
            info_text = ""
            plot_type = "area_neg"
            
            plot_single_go(title = "<b>AT %s GHG emissions</b> by sub-sectors" %(sector),
                          filename = "AT_timeseries_"+sectors[sector]["file"]+"_emissions_sectors",
                          unit = "Emissions (Mt<sub>CO2e</sub>)", 
                          data_plot = data_emissions,
                          time_res = "yearly",
                          show_plot = show_plot,
                          legend_inside = False,
                          source_text = source_text,
                          info_text = info_text,
                          plot_type = plot_type,
                          plotmax_fac = 1.05)
            
            emissions["data"]["LULUCF"] = data_emissions["data"]["Total"]
            emissions["data"]["Total"]["y"] += np.array(data_emissions["data"]["Total"]["y"])
        else: 
            # source_text = "Austria NIR 2023, UBA (Klimadashboard), sectoral data 2022 extrapolated"
            source_text = "EEA for sectoral, UBA (Klimadashboard) for total emissions"
            info_text =  "<Other> scaled to match total emissions from UBA, 2023 sectoral data extrapolated"
            plot_type = "area" 
    
            plot_with_toggle(title = "<b>AT %s GHG emissions</b> by sub-sectors" %(sector),
                          filename = "AT_timeseries_"+sectors[sector]["file"]+"_emissions_sectors",
                          unit = "Emissions (Mt<sub>CO2e</sub>)", 
                          data_plot = data_emissions,
                          time_res = "yearly",
                          show_plot = show_plot,
                          legend_inside = False,
                          source_text = source_text,
                          info_text = info_text,
                          plotmax_fac = 1.05,
                          initial_visible = "bar")
            
            
            
    ### TOTAL EMISSION WITH LULUCF 
    emissions_sorted = {"data": {}}
    emissions_sorted["data"]["LULUCF"] = emissions["data"]["LULUCF"]
    for sector in emissions["data"]: 
        if sector != "LULUCF": emissions_sorted["data"][sector] = emissions["data"][sector]
        
    colors_siecs ={"LULUCF": dark2[0],
        "Transport": dark2[2],
                    "Energy % Industry": dark2[1],
                    "Agriculture": dark2[4],
                    "Buildings": dark2[5],
                    "Waste": dark2[7],
                    "Fluorinated Gases": dark2[3],
                    }    
    colors = list([colors_siecs[label] for label in colors_siecs])
        
    plot_single_go(title = "<b>Austrian GHG emissions</b> by sectors (with LULUCF)",
                  filename = "AT_timeseries_co2_emissions_sectors_with_LULUCF",
                  unit = "Emissions (Mt<sub>CO2e</sub>)", 
                  data_plot = emissions_sorted,
                  time_res = "yearly",
                  show_plot = True,
                  colors = colors,
                  source_text = "Umweltbundesamt (Klimadashboard)",
                  plot_type = "area_neg",
                  plotmax_fac = 1.05)



    
    
if __name__ == "__main__": 
    print("Plotting ...")
    plot()