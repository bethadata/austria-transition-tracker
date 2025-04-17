# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 08:50:26 2024

@author: Bernhard
"""

import os 
import pandas as pd 
from datetime import datetime 
import numpy as np 
from .filter import filter_uba_sectoral_emisssions

sub_sectors = {"agriculture": ["total", "enteric_fermentation", "manure_management",
                               "agrigultural_soils", "field_burning_agricultural_residues",
                               "liming", "urea_application", "other_carbon_containing_fertilizers"],
               "agriculture_transport": ["co2", "ch4", "n2o", "tot"],
               "agriculture_stationary": ["co2", "ch4", "n2o", "tot"],
               "transport_road": ["passenger_cars_inland", "passenger_cars_export",
                                  "light_duty_vehicles_inland", "heavy_duty_vehicles_inland",
                                  "heavy_duty_vehicles_export", "mopeds_motorcycles"],
               "fluorinated_gases_electronics_industry": ["HFCs", "PFCs", "SF6", "NF3", "Total"],
               "fluorinated_gases_substitute_ozone_depletants": ["refrigeration_stationary_AC", 
                                     "mobile_AC", "foam_blowing_agents", "fire_protection", "aerosols", "solvents"],
               "fluorinated_gases_other_product_use": ["electrical_equip_SF6", "electrical_equip_CO2",
                                                       "other_use_SF6", "other_use_C3F8", "other_use_CO2",
                                                       "N2O_prod_use", "Total"],
               "fluorinated_gases_aluminium": ["CO2_kt", "PFC_t_aluminium", "CO2_kt_2", "SF6_kg_aluminium"],
               "fluorinated_gases_magnesium": ["SF6_t_magnesium"],
               "waste": ["solid_waste_disposal", "biological_treatment_solid_waste", "incineration", "wastewater_treatment", "total"],
               "electricity_heat_generation_fuel_shares": ["Liquid", "Solid", "Gaseous", "Other"],
               "electricity_heat_generation": ["co2", "ch4", "n2o","co2e"],
               "industry_process_emissions": ["mineral_products", "chemical_industry", "metal_production",
                                              "non_energy_products_fuel_use", "electronics", "ozone_depleting",
                                              "other_product_use", "total"],
               "energy_iron_steel": ["co2", "ch4", "n2o", "tot"],
               "energy_non_metallic_minerals": ["co2", "ch4", "n2o", "tot"],
               "energy_chemicals": ["co2", "ch4", "n2o", "tot"],
               "energy_pulp_paper_print": ["co2", "ch4", "n2o", "tot"],
               "energy_petroleum_refining": ["co2", "ch4", "n2o", "tot"],
               "energy_construction_mobile": ["co2", "ch4", "n2o", "tot"],
               "energy_construction_stationary": ["co2", "ch4", "n2o", "tot"],
               "buildings_commercial": ["co2", "ch4", "n2o", "tot"],
               "buildings_residential": ["co2", "ch4", "n2o", "tot"],
               "buildings_fuel_shares": ["Oil-heaters", "Coal-heaters", "Gas-heaters", "Other"],
               "lulucf": ["total", "forest_land", "crop_land", "grass_land", "wet_lands", "settlements", "other_land", "harvested_wood_products", "ch4", "n2o"],
               }


def filter_file(name = "agriculture"): 
    filepath  = "../../data_raw/national_inventory_report/%s.txt" %(name)
    fp = open(os.path.join(os.path.dirname(__file__), filepath), "r")
    lines = fp.readlines()
    
    
    data = {}
    years = []
    for sub_sector in sub_sectors[name]: 
        data[sub_sector] = []
        
    for line in lines: 
        splits = line.split(" ")
        years.append(int(splits[0]))
        
        sub_sec_num = 0
        for split in splits[1:]:
            if split in ["NO", "NO\n"]: split = "0.00"
            split = split.replace("%", "")
            data[sub_sectors[name][sub_sec_num]].append(float(split))
            sub_sec_num += 1

    return data, years



def filt(sector = "Agriculture"): 
    
    if sector == "Agriculture": 
        data, years = filter_file(name = "agriculture") 
        data.pop("total")
        data_energy_transport,_ = filter_file(name = "agriculture_transport")
        data_energy_stationary,_ = filter_file(name = "agriculture_stationary")
        data["energy"] = np.array(data_energy_transport["co2"])+np.array(data_energy_stationary["co2"])
        data_out_names = {"Fermentation (cows)": "enteric_fermentation",
                          "Organic fertilizer (manure) management": "manure_management",
                          "Soil fertilization": "agrigultural_soils",
                          "Energy use": "energy"}
        
    if sector == "Fluorinated Gases": 
        data_f_gas_electronics, years = filter_file(name = "fluorinated_gases_electronics_industry")
        data_f_gas_substitute_ozone,_ = filter_file(name = "fluorinated_gases_substitute_ozone_depletants")
        data_f_gas_other,_ = filter_file(name = "fluorinated_gases_other_product_use")
        data_f_gas_aluminium,_ = filter_file(name = "fluorinated_gases_aluminium")
        data_f_gas_magnesium,_ = filter_file(name = "fluorinated_gases_magnesium")
        
        data = {"electronics_industry": data_f_gas_electronics["Total"]}
        for entry in data_f_gas_substitute_ozone: 
            data[entry] = data_f_gas_substitute_ozone[entry]
        data["electrical_equip_CO2"] = data_f_gas_other["electrical_equip_CO2"]
        data["other_use_CO2"] = data_f_gas_other["other_use_CO2"]
        data["magnesium"] = np.array(data_f_gas_magnesium["SF6_t_magnesium"])*23500/1e3 #GWP of SF6, k
        
        #for PFC, use GWP of CF4 (7380) and C2F6 (12200), weighted with emissions of 1 t Al
        # https://www.researchgate.net/figure/Lifetimes-and-global-warming-potentials-of-CF-4-C-2-F-6-and-C-3-F-8_tbl1_43047606
        data["aluminium"] = (np.array(data_f_gas_aluminium["SF6_kg_aluminium"])*23500/1000 + #GWP of SF6 
                             np.array(data_f_gas_aluminium["PFC_t_aluminium"])*(1.56*7380+0.1248*12200)/(1.56+0.1248)) /1e3 #kt

        data_out_names = {"Stationary AC and refrigeration": "refrigeration_stationary_AC",
                          "Mobile AC": "mobile_AC",
                          "Electronics industry": "electronics_industry", 
                          "Aluminium industry": "aluminium",
                          "Magnesium industry": "magnesium"}
        
        ### year 2021 not present in ozone depleting substitutes (data error in 2023 inventory)
        ### scale with total emissions from 2021 using 2020 ratios (2022 inventory) 
        em_2021 = 1840
        em_2020 = 2140
        for entry in data_f_gas_substitute_ozone:
            data[entry].append(data[entry][-1]*em_2021/em_2020)
            
    elif sector == "Transport": 
        data,years = filter_file(name = "transport_road")
        data_out_names = {"Passenger cars: fuel inland": "passenger_cars_inland",
                          "Light duty vehilces: fuel inland": "light_duty_vehicles_inland",
                          "Heavy duty vehicles: fuel inland": "heavy_duty_vehicles_inland",
                          "Mopeds and Motorcycles": "mopeds_motorcycles",
                         "Passenger cars: fuel export": "passenger_cars_export",
                          "Heavy duty vehicles: fuel export": "heavy_duty_vehicles_export"}
            
    elif sector == "Waste": 
        data, years = filter_file(name = "waste")
        
        ### add waste energy sector emissions from power/heat generation 
        data_fuels,_ = filter_file(name = "electricity_heat_generation_fuel_shares")
        data_emissions,_ = filter_file(name = "electricity_heat_generation")
        data["waste_energy"] = np.array(data_fuels["Other"])/100 * np.array(data_emissions["co2e"])
        
        data_out_names = {"Solid waste disposal (landfills)": "solid_waste_disposal",
                          "Biological waste treatment": "biological_treatment_solid_waste",
                          "Waste water treatment": "wastewater_treatment", 
                          "Waste incineration for power/heat generation": "waste_energy"}
            

    elif sector == "Energy & Industry": 
        data_emissions, years = filter_file(name = "electricity_heat_generation")
        data_fuels,_ = filter_file(name = "electricity_heat_generation_fuel_shares")
        data = {"electricity_heat_generation": (100-np.array(data_fuels["Other"])
                                                )/100 * np.array(data_emissions["co2e"])}
        
        data_industry_process,_ = filter_file(name = "industry_process_emissions")
        data_energy_iron_steel, _ = filter_file(name = "energy_iron_steel")
        data["iron_and_steel"] = (np.array(data_industry_process["metal_production"]) + 
                                   np.array(data_energy_iron_steel["tot"]))
        data_energy_mineral_products, _ = filter_file(name = "energy_non_metallic_minerals")
        data["mineral_products"] = (np.array(data_industry_process["mineral_products"]) + 
                                   np.array(data_energy_mineral_products["tot"]))
        data_energy_chemicals, _ = filter_file(name = "energy_chemicals")
        data["chemical_industry"] = (np.array(data_industry_process["chemical_industry"]) + 
                                   np.array(data_energy_chemicals["tot"]))
        data["pulp_paper_print"] = filter_file(name = "energy_pulp_paper_print")[0]["tot"]
        data["petroleum_refining"] = filter_file(name = "energy_petroleum_refining")[0]["tot"]
        data["construction"] = (np.array(filter_file(name = "energy_construction_mobile")[0]["tot"]) + 
                                np.array(filter_file(name = "energy_construction_stationary")[0]["tot"]))

        # data_pulp_paper_print["tot"]
        
        data_out_names = {"Electricity and heat generation": "electricity_heat_generation",
                          "Iron and steel": "iron_and_steel",
                          "Cement / Minerals": "mineral_products",
                          "Chemical industry": "chemical_industry",
                          "Pulp / Paper": "pulp_paper_print",
                          "Petroleum refining": "petroleum_refining",
                          "Construction": "construction"}
        
        
    elif sector == "Buildings": 
        data_raw, years = filter_file(name = "buildings_fuel_shares")
        data_residential = np.array(filter_file(name = "buildings_residential")[0]["tot"])
        data_commercial = np.array(filter_file(name = "buildings_commercial")[0]["tot"])
        data= {}
        for fuel in data_raw: 
            data[fuel] = np.array(data_raw[fuel]) * (data_residential+data_commercial)/100
            
        data_out_names = {fuel: fuel for fuel in data_raw}
            
            
    elif sector == "LULUCF": 
        data,years = filter_file(name = "lulucf")
        data_out_names = {"Forests": "forest_land",
                          "Crop land": "crop_land",
                          "Grass land": "grass_land",
                          "Wet land": "wet_lands",
                         "Settlements": "settlements",
                          "Wood products": "harvested_wood_products"}

    times = pd.date_range(
        start = datetime(year = years[0], month = 1, day = 1),
        end = datetime(year = years[-1], month = 1, day = 1),
        freq="YS")
    
    data_out= {"data": {}}
    for name in data_out_names: 
        data_out["data"][name] = {"x": times,
                                  "y": np.array(data[data_out_names[name]])/1000}
    data_out["data"]["Other"] = {"x": times, 
                                 "y": np.zeros(len(times))}
    
    for sub_sector in data: 
        if sub_sector not in [data_out_names[name] for name in data_out_names] and sub_sector != "total":
            data_out["data"]["Other"]["y"] += np.array(data[sub_sector])/1000
         
    sum_sectors = np.zeros(len(times))
    for sub_sector in data_out["data"]:
        sum_sectors += np.array(data_out["data"][sub_sector]["y"])
        
    if sector not in ["LULUCF"]:
        uba_emissions = filter_uba_sectoral_emisssions()
        
        ### get rid of 2023 
        uba_emissions["data"][sector]["y"] = uba_emissions["data"][sector]["y"][:-1]
        uba_emissions["data"][sector]["x"] = uba_emissions["data"][sector]["x"][:-1]

        statistical_difference = np.array(uba_emissions["data"][sector]["y"][:-1]) - sum_sectors
        data_out["data"]["Other"]["y"] += np.array(statistical_difference)
    
        ### extend sectoral data 
        if uba_emissions["data"][sector]["x"][-1] not in data_out["data"]["Other"]["x"]:
            for sub_sector in data_out["data"]: 
                data_out["data"][sub_sector]["x"] = uba_emissions["data"][sector]["x"]
                sector_emissions = uba_emissions["data"][sector]["y"][-1] * (
                    data_out["data"][sub_sector]["y"][-1]/(sum_sectors[-1]+statistical_difference[-1]))
                data_out["data"][sub_sector]["y"] = np.append(data_out["data"][sub_sector]["y"], sector_emissions)
        
        data_out["data"]["Total"] = uba_emissions["data"][sector]
    else: 
        data_out["data"]["Total"] = {"x": data_out["data"][sub_sector]["x"],
                                     "y": sum_sectors}

    return data_out



def get_land_uses():
    cat_names = {"forest_land": "Forests",
                 "settlements": "Settlements",
                 "crop_land": "Crop land",
                 "grass_land": "Grass land",
                 "wet_land": "Wet land",
                 "other": "Other"
                 }
    
    data = {}
    for cat in cat_names:
        filepath  = "../../data_raw/national_inventory_report/lulucf_%s.txt" %(cat)
        fp = open(os.path.join(os.path.dirname(__file__), filepath), "r")
        lines = fp.readlines()
        
        years = []
        data_cat = []
        for line in lines: 
            splits = line.split(" ")
            years.append(int(splits[0]))
            if cat == "forest_land": 
                data_cat.append(int(splits[1])*1000) #given in kHa 
            else: 
                data_cat.append(int(splits[1])) #given in Ha
            
        data[cat] = {"years": years, "data": data_cat}
        
        
    times = pd.date_range(
        start = datetime(year = years[0], month = 1, day = 1),
        end = datetime(year = years[-1], month = 1, day = 1),
        freq="YS")
    
    data_out= {"data": {}}
    for cat in cat_names: 
        data_out["data"][cat_names[cat]] = {"x": times,
                                  "y": np.array(data[cat]["data"])/1000}  #kHa

    return data_out 



if __name__ == "__main__": 
    data = filt(sector = "LULUCF")
        
        
            
            
        
        


