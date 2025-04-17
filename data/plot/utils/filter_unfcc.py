# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 17:40:52 2024

@author: Bernhard
"""

import os 
import pandas as pd 
import numpy as np 
from datetime import datetime 

from .filter import filter_uba_sectoral_emisssions
# from filter import filter_uba_sectoral_emisssions

data = pd.read_excel(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "../../data_raw/unfcc/unfcc_Austria_2023.xlsx"))

data["Sector Name"] = data["Sector Name"].ffill()
data["Gas"] = data["Gas"].ffill()
data["Country"] = data["Country"].ffill()
data = data.fillna(0)

def filter_file(name = "agriculture",
                sub_sectors = []): 
    filepath  = "../../data_raw/national_inventory_report/%s.txt" %(name)
    fp = open(os.path.join(os.path.dirname(__file__), filepath), "r")
    lines = fp.readlines()
    
    data = {}
    years = []
    for sub_sector in sub_sectors: 
        data[sub_sector] = []
        
    for line in lines: 
        splits = line.split(" ")
        years.append(int(splits[0]))
        
        sub_sec_num = 0
        for split in splits[1:]:
            if split in ["NO", "NO\n"]: split = "0.00"
            split = split.replace("%", "")
            data[sub_sectors[sub_sec_num]].append(float(split))
            sub_sec_num += 1
            
    return data, years


def get_data(sector = "1 - Energy",
             gas = "All greenhouse gases - (CO2 equivalent)"): 
    data_cut = data[(data["Sector Name"] == sector) & 
                     (data["Country"] == "Austria") & 
                     (data["Gas"] == gas)
                     ]
       
    years = np.array(data_cut["Jahr von Date"])
    emissions = np.array(data_cut["t CO2 equivalent"])
    
    return years, emissions 


years, emissions = get_data()


def filt(sector = "Agriculture"): 
    data = {}
    
    if sector == "Agriculture": 
        sub_sectors = {"enteric_fermentation": {"codes": ["3.A - Enteric Fermentation"],
                                                "name": "Fermentation (cows)"},
                       "manure_management": {"codes": ["3.B - Manure Management"],
                                             "name": "Organic fertilizer (manure) management"},
                       "agrigultural_soils": {"codes": ["3.D - Agricultural Soils"],
                                              "name": "Soil fertilization"},
                       "energy": {"codes": ["1.A.4.c - Agriculture/Forestry/Fishing"],
                                  "name": "Energy use"}}

    
    
    elif sector == "Transport": 
        sub_sectors = {"passenger_cars": {"codes": ["1.A.3.b.i - Cars"],
                                          "name": "Passenger cars"},
                       "light_duty_vehicles": {"codes": ["1.A.3.b.ii - Light duty trucks"],
                                             "name": "Light duty vehilces"},
                       "heavy_duty_vehicles": {"codes": ["1.A.3.b.iii - Heavy duty trucks and buses"],
                                              "name": "Heavy duty vehicles and buses"},
                       "motorcycles": {"codes": ["1.A.3.b.iv - Motorcycles"],
                                  "name": "Mopeds and Motorcycles"}}
    
    elif sector == "Waste": 
        sub_sectors = {"solid_waste_disposal": {"codes": ["5.A - Solid Waste Disposal"],
                                          "name": "Solid waste disposal (landfills)"},
                       "biological_treatment_solid_waste": {"codes": ["5.B - Biological Treatment of Solid Waste"],
                                             "name": "Biological waste treatment"},
                       "wastewater_treatment": {"codes": ["5.D - Wastewater Treatment and Discharge"],
                                              "name": "Waste water treatment"},
                       "waste_energy": {"codes": ["1.A.1.a - Public Electricity and Heat Production"],
                                  "name": "Waste incineration for power/heat generation"}}
        
       
    elif sector == "Energy & Industry": 
        sub_sectors = {"electricity_heat_generation": {"codes": ["1.A.1.a - Public Electricity and Heat Production"],
                                                       "name": "Electricity and heat generation"},
                       "iron_and_steel": {"codes": ["1.A.2.a - Iron and Steel", "2.C.1 - Iron and Steel Production"],
                                          "name": "Iron and steel"},
                       "mineral_products": {"codes": ["2.A - Mineral Industry", "1.A.2.f - Non-metallic minerals"],
                                           "name": "Cement / Minerals"},
                       "chemical_industry":  {"codes": ["1.A.2.c - Chemicals", "2.B - Chemical Industry"],
                                           "name": "Chemical industry"},
                       "pulp_paper_print": {"codes": ["1.A.2.d - Pulp, Paper and Print"],
                                           "name": "Pulp / Paper"},
                       "petroleum_refining": {"codes": ["1.A.1.b - Petroleum Refining"],
                                           "name": "Petroleum refining"},
                       "construction": {"codes": ["1.A.2.g - Other Manufacturing Industries and Constructions"],
                                        "name": "Construction"},
                       }
        
      
    elif sector == "Buildings": 
        sub_sectors = {"residential": {"codes": ["1.A.4.b - Residential"],
                                       "name": "Residential / private"},
                       "commercial": {"codes": ["1.A.4.a - Commercial/Institutional"],
                                      "name": "Commercial / public"}}
    
    elif sector == "LULUCF": 
        sub_sectors = {"forest_land": {"codes": ["4.A - Forest Land"],
                                            "name": "Forests"},
                       "crop_land": {"codes": ["4.B - Cropland"],
                                                "name": "Cropland"},
                       "grass_land":  {"codes": ["4.C - Grassland"],
                                       "name": "Grassland"},
                       "wet_land": {"codes": ["4.D - Wetlands"],
                                    "name": "Wetlands"},
                       "settlements": {"codes": ["4.E - Settlements"],
                                       "name": "Settlements"},
                       "other_land": {"codes": ["4.F - Other Land"],
                                      "name": "Other land"},
                       "harvested_wood_products": {"codes": ["4.G - Harvested Wood Products"],
                                       "name": "Wood products"},
                       }
        
    
    elif sector == "Fluorinated Gases": 
        sub_sectors = {"refrigeration_AC": {"codes": ["2.F.1 - Refrigeration and Air conditioning"],
                                            "name": "Refrigeration and Air conditioning"},
                       "electronics_industry": {"codes": ["2.E - Electronics Industry"],
                                                "name": "Electronics industry"},
                       "magnesium":  {"codes": ["2.C.4 - Magnesium Production"],
                                       "name": "Magnesium industry"},
                       "aluminium": {"codes": ["2.C.3 - Aluminium Production"],
                                       "name": "Aluminium industry"},
                       }
        
    data_out= {"data": {}}
    
    for sub_sector in sub_sectors: 
        for sub_sub_sector in sub_sectors[sub_sector]["codes"]: 
            years, emissions = get_data(sub_sub_sector) 
            if sub_sector in data: 
                data[sub_sector] += emissions 
            else: 
                data[sub_sector] = emissions 
        
        times = pd.date_range(
            start = datetime(year = years[0], month = 1, day = 1),
            end = datetime(year = years[-1], month = 1, day = 1),
            freq="YS")
        
        data_out["data"][sub_sectors[sub_sector]["name"]] = {
            "x": times,
            "y": np.array(data[sub_sector])/1e6}



    ### CORRECTIONS 
    
    ### Austria counts waste burning for elec/heat to waste-sector, UNFCC to energy-sector 
    ### correct here by shares uf uel energies
    shares_fuels_energy,_ = filter_file(name = "electricity_heat_generation_fuel_shares",
                                        sub_sectors = ["Liquid", "Solid", "Gaseous", "Other"])
    
    if len(shares_fuels_energy) < len(times):
        diff = len(times) - len(shares_fuels_energy["Other"])
        for sub_sector in shares_fuels_energy: 
            shares_fuels_energy[sub_sector] += [shares_fuels_energy[sub_sector][-1] for i in range(diff)]
    
    if sector == "Waste": 
        data_out["data"]["Waste incineration for power/heat generation"]["y"] *= np.array(shares_fuels_energy["Other"])/100
    if sector == "Energy & Industry": 
        data_out["data"]["Electricity and heat generation"]["y"] *= (1-np.array(shares_fuels_energy["Other"])/100)
        
        
    # if sector == "Fluorinated Gases": 
    #     years, emissions = get_data("2.C.3 - Aluminium Production", gas = "Fluorinated gases - (CO2 equivalent)") 
    #     data_out["data"]["Aluminium industry"]["y"] = np.array(emissions)/1e6
    #     years, emissions = get_data("2.C.4 - Magnesium Production", gas = "Fluorinated gases - (CO2 equivalent)") 
    #     data_out["data"]["Magnesium industry"]["y"] = np.array(emissions)/1e6       
    
    
    ### corrections with last 2023 data
    # data_aagi_2023 = pd.read_excel(os.path.join(os.path.dirname(os.path.realpath(__file__)),
    #                                   "../../data_raw/Umweltbundesamt/aagi_1990_2023_data.xlsx"),
    #                                index_col = "Category", thousands = ",")
    
    
    data_aagi_2023 = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      "../../data_raw/Umweltbundesamt/aagi_1990_2023_data.csv"),
                                 index_col = "Category", thousands =",", sep = ";", decimal = ".",
                                 encoding='latin-1')
    for col in data_aagi_2023: 
        data_aagi_2023[col] = pd.to_numeric(data_aagi_2023[col].str.replace(",", ""), errors="coerce")
    
    if times[-1].year != 2023: 
        pass 
    
    ### complete new dataset of LULUCF starting 2024 database 
    if sector in ["LULUCF"]:
        times =  pd.date_range(
            start = datetime(year = years[0], month = 1, day = 1),
            end = datetime(year = 2023, month = 1, day = 1),
            freq="YS")
        
        if sector == "LULUCF": 
            uba_sectors = {"Forests": "A.    Forest Land",
                            "Cropland": "B.    Cropland",
                            "Grassland": "C.    Grassland",
                            "Wetlands": "D.    Wetlands",
                            "Settlements": "E.    Settlements" ,
                            "Other land": "F.    Other Land",
                            "Wood products": "G.    Harvested Wood Products"}
        
        
        for uba_sector, uba_table_name in uba_sectors.items(): 
            data_uba = np.zeros(len(times))
            for t in range(len(times)): 
                if str(times[t].year) in data_aagi_2023: 
                    data_uba[t] = data_aagi_2023[str(times[t].year)][uba_table_name]/1000 #Mt
                else: 
                    data_uba[t] = data_out["data"][uba_sector]["y"][t]

            data_out["data"][uba_sector]["x"] = times 
            data_out["data"][uba_sector]["y"] = data_uba
            
    sum_sectors = np.zeros(len(times))
    for sub_sector in data_out["data"]:
        sum_sectors += np.array(data_out["data"][sub_sector]["y"])
        
    ### LULUCF not in Umweltbundesamt data 
    if sector in ["LULUCF"]:
        data_out["data"]["Total"] = {"x": data_out["data"][sub_sector]["x"],
                                     "y": sum_sectors}
    else: 
        uba_emissions = filter_uba_sectoral_emisssions()
        
        statistical_difference = np.array(uba_emissions["data"][sector]["y"][:-1]) - sum_sectors
        data_out["data"]["Other"] = {"x": times,
                                     "y": np.array(statistical_difference)}
    
        ### extend sectoral data, if value still not present 
        if uba_emissions["data"][sector]["x"][-1] not in data_out["data"]["Other"]["x"]:
            for sub_sector in data_out["data"]: 
                data_out["data"][sub_sector]["x"] = uba_emissions["data"][sector]["x"]
                sector_emissions = uba_emissions["data"][sector]["y"][-1] * (
                    data_out["data"][sub_sector]["y"][-1]/(sum_sectors[-1]+statistical_difference[-1]))
                data_out["data"][sub_sector]["y"] = np.append(data_out["data"][sub_sector]["y"], sector_emissions)
        
        data_out["data"]["Total"] = uba_emissions["data"][sector]
        
    return data_out
        
if __name__ == "__main__": 
    print("Filtering ...") 
    # data = filt(sector = "Transport")
    # data = filt(sector = "Waste")
    # data = filt(sector = "Energy & Industry")
    # data = filt(sector = "Buildings")
    # data = filt(sector = "Fluorinated Gases")
    data = filt(sector = "LULUCF")
    # data = filt()