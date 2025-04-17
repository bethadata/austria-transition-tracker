# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 10:32:07 2024

@author: Bernhard
"""

import plotly.express as px
from plot_single import plot_single_go, plot_with_toggle
import numpy as np 
import os 
import pandas as pd 
import datetime 

from utils.filter import filter_eurostat_energy_balance



def plot(show_plot = False): 
    
    
    ### GROSS ENERGY CONSUMPTION 
    siecs_gross_energy = {"Natural gas": ["Natural gas"],
              "Oil": ["Oil and petroleum products (excluding biofuel portion)"],
              "Coal": ["Solid fossil fuels"],
              "Biomass": ["Primary solid biofuels", "Charcoal", "Pure biogasoline",
                          "Blended biogasoline", "Pure biodiesels", "Blended biodiesels",
                          "Pure bio jet kerosene", "Blended bio jet kerosene", "Other liquid biofuels",
                          "Biogases"],
              "Renewable electricity": ["Hydro","Wind","Solar photovoltaic","Tide, wave, ocean"],
              "Ambient heat": ["Geothermal", "Solar thermal", "Ambient heat (heat pumps)"],
              "Other": ["Manufactured gases", "Industrial waste (non-renewable)", 
                        "Non-renewable municipal waste",
                        "Renewable municipal waste", "Heat", "Electricity"]}
    
    set2 = px.colors.qualitative.Dark2
    colors_siecs_gross_energy ={"Natural gas": set2[5],
                    "Oil": set2[6],
                    "Coal": set2[7],
                    "Biomass": set2[4],
                    "Renewable electricity": set2[2],
                    "Ambient heat": set2[3],
                    "Other": set2[1]}    
    
    data_all_abs = filter_eurostat_energy_balance(bals = ["Gross inland consumption"],
                                                  siecs = siecs_gross_energy)
    data_all_abs_plot = {"data": {}}
    
    for siec in siecs_gross_energy: 
        data_all_abs_plot["data"][siec] = data_all_abs["data"][siec]
        

    ### VORLÄUFIGE ENERGIEBILANZ 
    if not data_all_abs_plot["data"]["Oil"]["x"][-1].year == 2022: 
        data_source = "eurostat energy balances (nrg_bal_c)"
    else: 
        data_source = "eurostat energy balances (nrg_bal_c) + Statistik Austria preliminary energy balance"
        
        data_2023 = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                                                "../data_raw/statistik_austria/vorlaeufigeEnergiebilanzenOesterreich2023inTerajouleDatenI(1).xlsx"),
                                  skiprows = 1)
        
        x_new = pd.date_range(start = data_all_abs_plot["data"]["Oil"]["x"][0],
                              end = datetime.datetime(year = 2023,month=1,day=1),freq = "YS")
        siecs = {"Natural gas": ["Gas"],
                "Oil": ["Öl"],
                "Coal": ["Kohle"],
                "Biomass": ["Brennholz", "feste Biogene Brenn- u. Treibstoffe",
                            "Biogase", "Bioethanol (Beimengung)", "Biodiesel (Beimengung)"],
                "Renewable electricity": ["Wasserkraft", "Windkraft", "Fotovoltaik"],
                "Ambient heat": ["Umgebungs-wärme","Geothermie", "Solarthermie"],
                "Other": ["Elektrische Energie", "Fernwärme", "Brennbare Abfälle",
                          "Gichtgas", "Kokereigas", "Raffinerie-Restgas"]}
            
        for siec in siecs: 
            value = 0 
            for energy_type in siecs[siec]:
                value += float(data_2023[energy_type][data_2023["Bilanzaggregat \ Energieträger\n"] == "Bruttoinlandsverbrauch"].iloc[0])/3600
                
            data_all_abs_plot["data"][siec] = {"y": np.append(
                data_all_abs_plot["data"][siec]["y"], value),
                "x": x_new}


    data_all_rel_plot = {"data": {}}
    data_total = np.zeros(len(data_all_abs_plot["data"]["Oil"]["x"]))
    for siec in colors_siecs_gross_energy: 
        data_total += np.array(data_all_abs_plot["data"][siec]["y"])

    for siec in colors_siecs_gross_energy: 
        data_all_rel_plot["data"][siec] = {"x": data_all_abs_plot["data"][siec]["x"],
                          "y": data_all_abs_plot["data"][siec]["y"]*100/data_total}    
            

    plot_with_toggle(title = "<b>AT gross inland consumption</b>: shares",
                  filename = "AT_timeseries_gross_inland_consumption_share",
                  unit = "Share [%]", 
                  data_plot = data_all_rel_plot,
                  time_res = "yearly",
                  show_plot = show_plot,
                  colors = list([colors_siecs_gross_energy[label] for label in colors_siecs_gross_energy]),
                  source_text = data_source,
                  plotmax_fac = 1,
                  initial_visible = "bar")
        
    plot_with_toggle(title = "<b>AT gross inland consumption</b>: absolute",
                  filename = "AT_timeseries_gross_inland_consumption_absolute",
                  unit = "Energy (TWh)", 
                  data_plot = data_all_abs_plot,
                  time_res = "yearly",
                  show_plot = show_plot,
                  colors = list([colors_siecs_gross_energy[label] for label in colors_siecs_gross_energy]),
                  source_text = data_source,
                  initial_visible = "bar")
    
    
    ### SECTORIAL FINAL ENERGY 
    siecs_final_energy = {"Natural gas": ["Natural gas"],
              "Oil": ["Oil and petroleum products (excluding biofuel portion)"],
              "Coal": ["Solid fossil fuels"],
              "Biomass": ["Primary solid biofuels", "Charcoal", "Pure biogasoline",
                          "Blended biogasoline", "Pure biodiesels", "Blended biodiesels",
                          "Pure bio jet kerosene", "Blended bio jet kerosene", "Other liquid biofuels",
                          "Biogases"],
              "Electricity": ["Electricity"],
              "District Heat": ["Heat"],
              "Other": ["Manufactured gases", "Industrial waste (non-renewable)", 
                        "Geothermal", "Solar thermal", "Ambient heat (heat pumps)",
                        ]}
    
    set2 = px.colors.qualitative.Dark2
    colors_siecs_final_energy ={"Natural gas": set2[5],
                    "Oil": set2[6],
                    "Coal": set2[7],
                    "Biomass": set2[4],
                    "Electricity": set2[2],
                    "District Heat": set2[3],
                    "Other": set2[1]}    
    
    sectors = {"Buildings": {"file": "buildings",
                              "en_bal": {"Households": "Final consumption - other sectors - households - energy use",
                                        "Commercial": "Final consumption - other sectors - commercial and public services - energy use"}},
                "Industry": {"file": "industry",
                            "en_bal": {"Iron & Steel": "Final consumption - industry sector - iron and steel - energy use",
                                        "Chemicals": "Final consumption - industry sector - chemical and petrochemical - energy use",
                                        "Pulp & Paper": "Final consumption - industry sector - paper, pulp and printing - energy use",
                                        "Non-metallic minerals": "Final consumption - industry sector - non-metallic minerals - energy use",
                                        "Non-ferrous metals": "Final consumption - industry sector - non-ferrous metals - energy use",
                                        "Transport equipment": "Final consumption - industry sector - transport equipment - energy use",
                                        "Machinery": "Final consumption - industry sector - machinery - energy use",
                                        "Mining": "Final consumption - industry sector - mining and quarrying - energy use",
                                        "Food industry": "Final consumption - industry sector - food, beverages and tobacco - energy use",
                                        "Wood industry": "Final consumption - industry sector - wood and wood products - energy use",
                                        "Construction": "Final consumption - industry sector - construction - energy use",
                                        "Textile": "Final consumption - industry sector - textile and leather - energy use",
                                        "Other": "Final consumption - industry sector - not elsewhere specified - energy use"
                                        }},
                "Agriculture":  {"file": "agriculture",
                                "en_bal": {"Total": "Final consumption - other sectors - agriculture and forestry - energy use"}},
                "Transport":  {"file": "transport",
                              "en_bal": {"Rail": "Final consumption - transport sector - rail - energy use",
                                          "Road": "Final consumption - transport sector - road - energy use",
                                          "Domestic aviation": "Final consumption - transport sector - domestic aviation - energy use",
                                          "Domestic shipping": "Final consumption - transport sector - domestic navigation - energy use",
                                          "Pipelines": "Final consumption - transport sector - pipeline transport - energy use",
                                          "Other": "Final consumption - transport sector - not elsewhere specified - energy use"}
                              },
                "AT-total": {"file": "total",
                          "en_bal": {"Total": "Available for final consumption"}}
                }

    
    
    
    for sector in sectors: 
        data_all_abs = {}
        
        for bal in sectors[sector]["en_bal"]:
            data_all_abs[bal] = filter_eurostat_energy_balance(bals = [sectors[sector]["en_bal"][bal]],
                                                                siecs = siecs_final_energy)
        
        data_all_abs_plot = {"Total": {"data": {}}}
        
        for bal in data_all_abs: 
            data_all_abs_plot[bal] = {"data": {}}
            for siec in siecs_final_energy: 
                data_all_abs_plot[bal]["data"][siec] = data_all_abs[bal]["data"][siec]

        ### Total of sector               
        if "Total" not in data_all_abs: 
            for siec in data_all_abs_plot[bal]["data"]: 
                total_sector = np.zeros(len(data_all_abs[bal]["data"]["Oil"]["x"]))
                for bal in data_all_abs_plot:
                    if bal not in ["Total"]: 
                        total_sector += data_all_abs_plot[bal]["data"][siec]["y"]
                data_all_abs_plot["Total"]["data"][siec] =  {"x": data_all_abs_plot[bal]["data"][siec]["x"],
                                                              "y": total_sector}
                
        ### VORLÄUFIGE ENERGIEBILANZ 
        if data_all_abs[bal]["data"]["Oil"]["x"][-1].year == 2022: 
            
            data_2023 = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                                                    "../data_raw/statistik_austria/vorlaeufigeEnergiebilanzenOesterreich2023inTerajouleDatenI(1).xlsx"),
                                      skiprows = 1)
            
            x_new = pd.date_range(start = data_all_abs_plot["Total"]["data"]["Oil"]["x"][0],
                                  end = datetime.datetime(year = 2023,month=1,day=1),freq = "YS")
            siecs = {"Natural gas": ["Gas"],
                    "Oil": ["Öl"],
                    "Coal": ["Kohle"],
                    "Biomass": ["Brennholz", "feste Biogene Brenn- u. Treibstoffe",
                                "Biogase", "Bioethanol (Beimengung)", "Biodiesel (Beimengung)"],
                    "Electricity": ["Elektrische Energie"],
                    "District Heat": ["Fernwärme"],
                    "Other": ["Brennbare Abfälle", "Geothermie", "Solarthermie", "Umgebungs-wärme",
                              "Gichtgas", "Kokereigas", "Raffinerie-Restgas"]}
            
            
            for siec in siecs: 
                if sector == "Buildings": 
                    rows = ["Öffentliche und Private Dienstleistungen", "Private Haushalte"]
                elif sector == "Transport": 
                    rows = ["Verkehr"]
                elif sector == "Industry": 
                    rows = ["Produzierender Bereich"]
                elif sector == "Agriculture": 
                    rows = ["Landwirtschaft"]
                elif sector == "AT-total": 
                    rows = ["Energetischer Endverbrauch"]
                
                
                value = 0 
                for row in rows:
                    for energy_type in siecs[siec]:
                        value += float(data_2023[energy_type][data_2023["Bilanzaggregat \ Energieträger\n"] == row].iloc[0])/3600
                    
                data_all_abs_plot["Total"]["data"][siec] = {"y": np.append(
                    data_all_abs_plot["Total"]["data"][siec]["y"], value),
                    "x": x_new}
                   
                    
        data_all_rel_plot = {}
        for bal in data_all_abs_plot:
            data_all_rel_plot[bal] = {"data": {}}
            data_total = np.zeros(len(data_all_abs_plot[bal]["data"]["Oil"]["x"]))
            for siec in colors_siecs_final_energy: 
                data_total += np.array(data_all_abs_plot[bal]["data"][siec]["y"])
    
            for siec in colors_siecs_final_energy: 
                data_all_rel_plot[bal]["data"][siec] = {"x": data_all_abs_plot[bal]["data"][siec]["x"],
                                  "y": data_all_abs_plot[bal]["data"][siec]["y"]*100/data_total}    
                
            
        if sector != "AT-total": 
            plot_single_go(title = "<b>%s</b>: final energy use - shares" %(sector),
                          filename = "AT_timeseries_%s_final_energy_use_share" %(sectors[sector]["file"]),
                          unit = "Share [%]", 
                          data_plot = data_all_rel_plot,
                          time_res = "yearly",
                          show_plot = show_plot,
                          colors = list([colors_siecs_final_energy[label] for label in colors_siecs_final_energy]),
                          source_text = data_source,
                          plot_type = "area_button",
                          plotmax_fac = 1)
                
            plot_single_go(title = "<b>%s</b>: final energy use" %(sector),
                          filename = "AT_timeseries_%s_final_energy_use" %(sectors[sector]["file"]),
                          unit = "Energy (TWh)", 
                          data_plot = data_all_abs_plot,
                          time_res = "yearly",
                          show_plot = show_plot,
                          colors = list([colors_siecs_final_energy[label] for label in data_all_abs_plot[bal]["data"]]),
                          source_text = data_source,
                          plot_type = "area_button")
        else: 
            plot_with_toggle(title = "<b>AT final energy use</b>: shares",
                          filename = "AT_timeseries_%s_final_energy_use_share" %(sectors[sector]["file"]),
                          unit = "Share [%]", 
                          data_plot = data_all_rel_plot["Total"],
                          time_res = "yearly",
                          show_plot = show_plot,
                          colors = list([colors_siecs_final_energy[label] for label in colors_siecs_final_energy]),
                          source_text = data_source,
                          plotmax_fac = 1,
                          initial_visible = "bar")
                
            plot_with_toggle(title = "<b>AT final energy use</b>: absolute",
                          filename = "AT_timeseries_%s_final_energy_use" %(sectors[sector]["file"]),
                          unit = "Energy (TWh)", 
                          data_plot = data_all_abs_plot["Total"],
                          time_res = "yearly",
                          show_plot = show_plot,
                          colors = list([colors_siecs_final_energy[label] for label in data_all_abs_plot[bal]["data"]]),
                          source_text = data_source,
                          initial_visible = "bar")

    


if __name__ == "__main__": 
    print("Plotting ...")
    plot()
    
    # data = filter_eurostat_energy_balance(bals = ["Gross inland consumption"],
    #                                               siecs = {"Total": ["Total"]})


