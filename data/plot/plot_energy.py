# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 23:39:34 2024

@author: Bernhard
"""

import plotly.express as px
from plot_single import plot_single_go, plot_with_toggle
import numpy as np 
import pandas as pd 
from datetime import datetime 

from utils import filter_national_inventory
from utils.filter import filter_eurostat_energy_balance
from utils.filter import filter_uba_sectoral_emisssions
from utils.filter import filter_uba_emissions
from utils import filter_econtrol 

def plot(): 
    
    """ DISTRICT HEAT """ 
    
    siecs = {"Natural gas": ["Natural gas"],
             "Oil": ["Oil and petroleum products (excluding biofuel portion)"],
             "Biomass": ["Primary solid biofuels"],
              "Coal": ["Solid fossil fuels"],
             "Waste non-renewable": ["Non-renewable waste"],
             "Waste renewable": ["Renewable municipal waste"],
             "Total": ["Total"]}
    
    dark2 = px.colors.qualitative.Dark2
    colors_siecs ={"Natural gas": dark2[5],
                    "Oil": dark2[6],
                    "Coal": dark2[7],
                    "Biomass": dark2[4],
                    "Waste": dark2[2],
                    "Other": dark2[1]}    
    
    data  = filter_eurostat_energy_balance(bals = ["Gross heat production"],
                                                 siecs = siecs)
    
    data_plot = {"data": {"Natural gas": data["data"]["Natural gas"],
                          "Oil": data["data"]["Oil"],
                          "Coal": data["data"]["Coal"],
                          "Biomass": data["data"]["Biomass"],
                          "Waste": {"x": data["data"]["Waste non-renewable"]["x"],
                                    "y": (np.array(data["data"]["Waste non-renewable"]["y"])+
                                          np.array(data["data"]["Waste renewable"]["y"]))},
                          "Other": {"x":  data["data"]["Waste non-renewable"]["x"],
                                    "y": (np.array(data["data"]["Total"]["y"])-
                                          np.array(data["data"]["Natural gas"]["y"])-
                                          np.array(data["data"]["Oil"]["y"])-
                                          np.array(data["data"]["Coal"]["y"])-
                                          np.array(data["data"]["Biomass"]["y"])-
                                          np.array(data["data"]["Waste non-renewable"]["y"])-
                                          np.array(data["data"]["Waste renewable"]["y"]))}}}
    
    data_rel = {"data": {}}
    
    for siec in data_plot["data"]: 
        data_rel["data"][siec] = {"x": data_plot["data"][siec]["x"],
                                    "y": np.array(data_plot["data"][siec]["y"])*100/np.array(data["data"]["Total"]["y"])}
    
    plot_with_toggle(title = "<b>District heat generation (gross)</b>: energy",
                  filename = "AT_timeseries_dh_energy_use",
                  unit = "Energy (TWh)", 
                  data_plot = data_plot,
                  time_res = "yearly",
                  show_plot = False,
                   colors = list([colors_siecs[label] for label in colors_siecs]),
                  source_text = "eurostat energy balances (nrg_bal_c)",
                  initial_visible = "bar")
    
    
    plot_with_toggle(title = "<b>District heat generation (gross)</b>: energy shares",
                  filename = "AT_timeseries_dh_energy_use_share",
                  unit = "Share [%]", 
                  data_plot = data_rel,
                  time_res = "yearly",
                  show_plot = False,
                  colors = list([colors_siecs[label] for label in colors_siecs]),
                  source_text = "eurostat energy balances (nrg_bal_c)",
                  plot_type = "area",
                  initial_visible = "bar",
                  plotmax_fac = 1)
    
    
    
    
    """ ELECTRICITY """ 
    
    siecs = {"Natural gas": ["Natural gas"],
             "Biomass": ["Bioenergy"],
              "Coal": ["Solid fossil fuels"],
             "Waste non-renewable": ["Non-renewable waste"],
             "Waste renewable": ["Renewable municipal waste"],
             "PV": ["Solar photovoltaic"],
             "Wind": ["Wind"],
             "Hydro": ["Hydro"],
             "Total": ["Total"]}
    
    dark2 = px.colors.qualitative.Dark2
    set1 = px.colors.qualitative.Set1
    set2 = px.colors.qualitative.Set2
    set3 = px.colors.qualitative.Set3
    
    colors_siecs ={"PV": set2[1],
                   "Wind": dark2[0],
                   "Hydro": set1[1],
                   "Biomass": dark2[4],
                    "Natural gas": dark2[5],
                    "Coal": dark2[7],
                    "Waste": dark2[2],
                    "Other": set3[9],
                    }    
    
    data  = filter_eurostat_energy_balance(bals = ["Gross electricity production"],
                                                 siecs = siecs)
    data_cons = filter_eurostat_energy_balance(bals = ["Available for final consumption",
                                                       "Energy sector - energy use",
                                                       "Distribution losses"
                                                       ],
                                                 siecs = {"electricity": ["Electricity"]})
    
    data_plot = {"data": {"PV": data["data"]["PV"],
                          "Wind": data["data"]["Wind"],
                          "Hydro": data["data"]["Hydro"],
                          "Biomass": data["data"]["Biomass"],
                          "Natural gas": data["data"]["Natural gas"],
                          "Coal": data["data"]["Coal"],
                          "Waste": {"x": data["data"]["Waste non-renewable"]["x"],
                                    "y": (np.array(data["data"]["Waste non-renewable"]["y"])+
                                          np.array(data["data"]["Waste renewable"]["y"]))},
                          "Other": {"x":  data["data"]["Waste non-renewable"]["x"],
                                    "y": (np.array(data["data"]["Total"]["y"])-
                                          np.array(data["data"]["Natural gas"]["y"])-
                                          np.array(data["data"]["PV"]["y"])-
                                          np.array(data["data"]["Wind"]["y"])-
                                          np.array(data["data"]["Hydro"]["y"])-
                                          np.array(data["data"]["Coal"]["y"])-
                                          np.array(data["data"]["Biomass"]["y"])-
                                          np.array(data["data"]["Waste non-renewable"]["y"])-
                                          np.array(data["data"]["Waste renewable"]["y"]))},
                          "Domestic consumption": {"x": data_cons["data"]["electricity"]["x"],
                                                   "y": (np.array(data_cons["data"]["electricity"]["y"]))}
                          
                          }}
    
    
    ### E-control monthly 
    data_monthly = filter_econtrol.filter_econtrol_monthly()
    last_month = data_monthly["data"]["PV"]["x"][-1].month 
    
    ### exchange all E-control available data 
    years_econtrol = []
    for date in data_monthly["data"]["PV"]["x"]: 
        if date.year in years_econtrol: 
            pass
        else: 
            years_econtrol.append(date.year)
            
    times = pd.date_range(start = datetime(year=data_plot["data"]["Other"]["x"][0].year, month = 1, day =1),
                          end = datetime(year = years_econtrol[-1], month = 1, day = 1),
                          freq = "YS")     
            
    for siec in data_plot["data"]: 
        values = {data_plot["data"][siec]["x"][i]: data_plot["data"][siec]["y"][i] for i in range(len(data_plot["data"][siec]["x"]))}
       
        for year in years_econtrol: 
            value = sum(data_monthly["data"][siec]["y"][pd.to_datetime(data_monthly["data"][siec]["x"]).year == year])
            values[datetime(year = year, month = 1, day= 1)] = value 
            
        data_plot["data"][siec] = {"x": times,
                                   "y": np.array([values[time] for time in values])}


    ### sum up total production data 
    data_total = np.zeros(len(data_plot["data"][siec]["x"]))
    for siec in data_plot["data"]:
        if siec not in ["Domestic consumption"]: 
            data_total += data_plot["data"][siec]["y"]
        data["data"]["Total"]["y"] = data_total 
    
    
    data_rel = {"data": {}}
    data_rel_cons = {"data": {}}
    
    for siec in data_plot["data"]: 
        if siec not in ["Domestic consumption"]: 
            data_rel["data"][siec] = {"x": data_plot["data"][siec]["x"],
                                        "y": np.array(data_plot["data"][siec]["y"])*100/np.array(data["data"]["Total"]["y"])}
            data_rel_cons["data"][siec] = {"x": data_plot["data"][siec]["x"],
                            "y": np.array(data_plot["data"][siec]["y"])*100/np.array(data_plot["data"]["Domestic consumption"]["y"])}



    plot_with_toggle(title = "<b>Yearly electricity production AT (gross)</b>: energy ",
                  filename = "AT_timeseries_elec_energy_use",
                  unit = "Energy (TWh)", 
                  data_plot = data_plot,
                  time_res = "yearly",
                  show_plot = False,
                  colors = list([colors_siecs[label] for label in colors_siecs]),
                  source_text = f"eurostat energy balances (nrg_bal_c) up to 2015, E-control from 2015 up to {last_month}/{years_econtrol[-1]}",
                  info_text = "Note: no Waste-data available in E-control data.",
                  initial_visible = "bar")
    
    plot_with_toggle(title = "<b>Yearly electricity production AT (gross)</b>: shares of production",
                  filename = "AT_timeseries_elec_energy_use_share",
                  unit = "Share [%]", 
                  data_plot = data_rel,
                  time_res = "yearly",
                  show_plot = False,
                  colors = list([colors_siecs[label] for label in colors_siecs]),
                  source_text = f"eurostat energy balances (nrg_bal_c) up to 2015, E-control from 2015 up to {last_month}/{years_econtrol[-1]}",
                  info_text = "Note: no Waste-data available in E-control data.",
                  plot_type = "bar",
                  plotmax_fac = 1,
                  initial_visible = "bar")
    

    plot_with_toggle(title = "<b>Yearly electricity production AT (gross)</b>: shares of consumption",
                  filename = "AT_timeseries_elec_energy_use_share_cons",
                  unit = "Share [%]", 
                  data_plot = data_rel_cons,
                  time_res = "yearly",
                  show_plot = False,
                  colors = list([colors_siecs[label] for label in colors_siecs]),
                  source_text = f"eurostat energy balances (nrg_bal_c) up to 2015, E-control from 2015 up to {last_month}/{years_econtrol[-1]}",
                  info_text = "Note: no Waste-data available in E-control data.",
                  plot_type = "bar",
                  plotmax_fac = 1.05,
                  initial_visible = "bar")
    

    data_rel = {"data": {}}
    data_rel_cons = {"data": {}}
    data_total = np.zeros(len(data_monthly["data"]["PV"]["y"]))
    for siec in data_plot["data"]: 
        if siec not in ["Domestic consumption"]:
            data_total += np.array(data_monthly["data"][siec]["y"])
        
    for siec in data_plot["data"]: 
        if siec not in ["Domestic consumption"]:
            data_rel["data"][siec] = {"x": data_monthly["data"][siec]["x"],
                                      "y": np.array(data_monthly["data"][siec]["y"]*100)/data_total}
            data_rel_cons["data"][siec] =  {"x": data_monthly["data"][siec]["x"],
                                      "y": np.array(data_monthly["data"][siec]["y"]*100)/ np.array(
                                          data_monthly["data"]["Domestic consumption"]["y"])}
            
            
    plot_with_toggle(title = "<b>Monthly electricity production AT (gross)</b>: energy ",
                  filename = "AT_timeseries_elec_prod_monthly",
                  unit = "Energy (TWh)", 
                  data_plot = data_monthly,
                  time_res = "monthly",
                  show_plot = False,
                  colors = list([colors_siecs[label] for label in colors_siecs]),
                  source_text = "E-control (MoMeGes)",
                  plot_type = "area")
    
    
    plot_with_toggle(title = "<b>Monthly electricity production AT (gross)</b>: shares of production",
                  filename = "AT_timeseries_elec_prod_monthly_share",
                  unit = "Share [%]", 
                  data_plot = data_rel,
                  time_res = "monthly",
                  show_plot = False,
                  colors = list([colors_siecs[label] for label in colors_siecs]),
                  source_text = "E-control (MoMeGes)",
                  plot_type = "area",
                  plotmax_fac = 1)
        
    plot_with_toggle(title = "<b>Monthly electricity production AT (gross)</b>: shares of consumption",
                  filename = "AT_timeseries_elec_prod_monthly_share_cons",
                  unit = "Share [%]", 
                  data_plot = data_rel_cons,
                  time_res = "monthly",
                  show_plot = False,
                  colors = list([colors_siecs[label] for label in colors_siecs]),
                  source_text = "E-control (MoMeGes)",
                  initial_visible = "area",
                  plotmax_fac = 1.05)
    
    
    return data_plot


if __name__ == "__main__": 
    data_plot = plot()