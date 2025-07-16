# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 19:04:15 2024

@author: Bernhard
"""

from datetime import datetime, timedelta  
import pandas as pd 
import numpy as np 
import plotly.express as px
import matplotlib.pyplot as plt 
import os 

from plot_single import plot_single_go, plot_with_toggle
from utils.filter import filter_eurostat_monthly
from utils import filter_fossil_extrapolation
from utils.filter import filter_uba_sectoral_emisssions


### natural gas must be converted from TJ_GCV to TJ_NCV 
TJ_GCV_to_1000m3 = 0.03914 #TJ_GCV / 1000m3 
TJ_NCV_to_1000m3 = 0.03723 #TJ_NCV / 1000M3 


fossils = {"Natural gas": {"file": "gas",
                           "save_name": "natural_gas",
                           "code": "NRG_CB_GASM",
                           "options":  {"unit": "TJ_GCV",
                                        "nrg_bal": "Inland consumption - calculated as defined in MOS GAS [IC_CAL_MG]"},
                           "NCV": TJ_NCV_to_1000m3/TJ_GCV_to_1000m3/1000,   #TJ_NCV / (1000*TJ_GCV) 
                           "em_fac": 55.4},  #t_CO2 / TJ 
           "Gasoline": {"file": "oil",
                        "save_name": "gasoline",
                        "code": "NRG_CB_OILM",
                        "options":  {"unit": "THS_T",
                                     "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                     "siec": "Motor gasoline [O4652]"},
                        "NCV": 0.0418,
                        "em_fac": 71.3},
            "Diesel": {"file": "oil",
                         "save_name": "diesel",
                         "code": "NRG_CB_OILM",
                         "options":  {"unit": "THS_T",
                                      "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                      "siec": "Road diesel [O46711]"},
                         "NCV": 0.0424,
                         "em_fac": 71.3},
            "Heating gas oil": {"file": "oil",
                         "save_name": "heating_oil",
                         "code": "NRG_CB_OILM",
                         "options":  {"unit": "THS_T",
                                      "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                      "siec": "Heating and other gasoil [O46712]"},
                         "NCV": 0.0428,
                         "em_fac": 75},
            "Refinery gas": {"file": "oil",
                         "save_name": "refinery_gas",
                         "code": "NRG_CB_OILM",
                         "options":  {"unit": "THS_T",
                                      "nrg_bal": "Refinery fuel [RF]",
                                      "siec": "Refinery gas [O4610]"},
                         "NCV": 0.0306,
                         "em_fac": 64},
            "Hard coal - electricity sector": {"file": "coal",
                         "save_name": "hard_coal_electricity",
                         "code": "NRG_CB_SFFM",
                         "options":  {"unit": "THS_T",
                                      "nrg_bal": "Transformation input - electricity and heat generation - main activity producers [TI_EHG_MAP]",
                                      "siec": "Hard coal [C0100]"},
                         "NCV": 0.0299,
                         "em_fac": 95},
            "Hard coal - industry sector": {"file": "coal",
                         "save_name": "hard_coal_industry",
                         "code": "NRG_CB_SFFM",
                         "options":  {"unit": "THS_T",
                                      "nrg_bal": "Final consumption - industry sector [FC_IND]",
                                      "siec": "Hard coal [C0100]"},
                         "NCV": 0.0299,
                         "em_fac": 84},
            "Hard coal - coke ovens": {"file": "coal",
                         "save_name": "hard_coal_coke_ovens",
                         "code": "NRG_CB_SFFM",
                         "options":  {"unit": "THS_T",
                                      "nrg_bal": "Transformation input - coke ovens [TI_CO]",
                                      "siec": "Hard coal [C0100]"},
                         "NCV": 0.0299,
                         "em_fac": 84},
            "Coke oven coke": {"file": "coal",
                         "save_name": "coke_oven_coke",
                         "code": "NRG_CB_SFFM",
                         "options":  {"unit": "THS_T",
                                      "nrg_bal": "Gross inland deliveries - calculated [GID_CAL]",
                                      "siec": "Coke oven coke [C0311]"},
                         "NCV": 0.0282,
                         "em_fac": 94.6},
            }

units_plot = {"THS_T": "1000 tons",
              "TJ_GCV": "TJ<sub>GCV</sub>"}

# fossils = {"Natural gas": {"file": "gas",
#                             "save_name": "natural_gas",
#                             "code": "NRG_CB_GASM",
#                             "options":  {"unit": "TJ_GCV",
#                                         "nrg_bal": "Inland consumption - calculated as defined in MOS GAS [IC_CAL_MG]"},
#                             "NCV": TJ_NCV_to_1000m3/TJ_GCV_to_1000m3/1000,   #TJ_NCV / (1000*TJ_GCV) 
#                             "em_fac": 55.4}}  #t_CO2 / TJ 


fossil_categories = {"Gas": ["Natural gas"],
                     "Oil": ["Gasoline", "Diesel", "Heating gas oil", "Refinery gas"],
                     "Coal": ["Coke oven coke", "Hard coal - coke ovens",
                              "Hard coal - industry sector", "Hard coal - electricity sector"]}
months = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
          7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}


dark2 = px.colors.qualitative.Dark2
set2 = px.colors.qualitative.Set2
colors  = {"yearly_to": dark2[0],
            "yearly_from": set2[0],
            "extrapolated": set2[1]}


def separate_bios(data_monthly, f): 
    """ based on diesel and gasoline data, load also biofuel data and subtract them from 
    to be plotted data """ 
    
    if f == "Diesel": siec = "Blended biodiesels [R5220B]"
    if f == "Gasoline": siec = "Blended biogasoline [R5210B]"
    data_monthly_bio = filter_eurostat_monthly(name = "oil",
                                           code = "NRG_CB_OILM",
                                           options = {"unit": "THS_T",
                                                      "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                                      "siec": siec},
                                           unit = "THS_T",
                                           movmean = 12)
    movmean = 12 
    times_plot = data_monthly_bio["data"]["Monthly"]["x"]
    times_plot_mean = data_monthly_bio["data"]["%i-Month average" %(movmean)]["x"]
    values = np.array(data_monthly["data"]["Monthly"]["y"])
    values_mean = np.array(data_monthly["data"]["%i-Month average" %(movmean)]["y"])
    values_bio = np.array(data_monthly_bio["data"]["Monthly"]["y"])
    values_bio_mean = np.array(data_monthly_bio["data"]["%i-Month average" %(movmean)]["y"])
    
    data_monthly = {"data": {"%s Monthly" %(f): {"x": times_plot,
                                                 "y": values-values_bio},
                             "%s %i-Month average" %(f, movmean): {"x": times_plot_mean,
                                                                           "y": values_mean-values_bio_mean},
                             "Bio-%s Monthly " %(f): {"x": times_plot,
                                                     "y": values_bio},
                             "Bio-%s %i-Month average" %(f, movmean): {"x": times_plot_mean,
                                                                               "y": values_bio_mean},                                     
                             },
                    "meta": {"code": "NRG_CB_OILM"}
                    }
    return data_monthly 


def extrapolate_fossil_fuels(plot = False):
    """ extrapolate the consumption data of fossil fuels to the end of year based on historic factors """
    
    consumption = {}
    emissions_yearly = {"data": {}}
    
    for f in fossils: 
        ### MONTHLY 
        data_monthly = filter_eurostat_monthly(name = fossils[f]["file"],
                                               code = fossils[f]["code"],
                                               options = fossils[f]["options"],
                                               unit = fossils[f]["options"]["unit"],
                                               movmean = 12)
        legend_inside = True 
        if f in ["Diesel", "Gasoline"]: 
            legend_inside = False 
            data_monthly  = separate_bios(data_monthly, f) 

        plot_single_go(title = "<b>%s</b>: monthly consumption" %(f), 
                        filename = "AT_timeseries_consumption_%s_monthly" %(fossils[f]["save_name"]),
                        unit =  "Consumption (%s)" %(units_plot[fossils[f]["options"]["unit"]]),
                        data_plot=data_monthly, 
                        unit_fac = 1,
                        show_plot = plot,
                        legend_inside = legend_inside)
        
        ### rename bio values so that they can be processed 
        if f in ["Diesel", "Gasoline"]: 
            data_monthly["data"]["Monthly"] = data_monthly["data"]["%s Monthly" %(f)]
        
        ### YEARLY AND EXTRAPOLATION 
        data_raw = filter_fossil_extrapolation.cut_data_fossil(data_monthly)
        data_extrapolated = filter_fossil_extrapolation.extrapolate_data_fossil(data_raw)

        years = [year for year in data_raw["values_year_to_last_month"]]

        times_years = pd.date_range(start = datetime(year = years[0], month = 1, day =1),
                              end = datetime(year = years[-1], month = 1, day = 1),
                              freq="YS")
        
        ### values up to latest month 
        values_year_to_last_month = [data_raw["values_year_to_last_month"][year] for year in data_raw["values_year_to_last_month"]]
        last_month = datetime.strptime(str(data_raw["meta"]["last_month"]), "%m")
        data = {"data": {"Observed: Jan - %s" %(last_month.strftime("%b")):
                         {"x": times_years,
                          "y": np.array(values_year_to_last_month)},
                         }}
        colors_plot = [colors["yearly_to"]] 

        if last_month.month != 12: 
            ### values from latest month on 
            values_year_from_last_month = [data_raw['values_year_from_last_month'][year] for year in data_raw['values_year_from_last_month']]
            last_month_plus = datetime.strptime(str(data_raw["meta"]["last_month"]+1), "%m")
            data["data"]["Observed: %s - Dec" %(last_month_plus.strftime("%b"))] =  {
                "x": times_years,
                "y": np.array(values_year_from_last_month)}
            colors_plot.append(colors["yearly_from"])
            
            ### extrapolation data from latest month on 
            values_extrapolated = np.zeros(len(times_years))
            values_extrapolated[-1] = data_extrapolated["extrapolated_year"]-data_extrapolated["consumption_to_month"]
            data["data"]["Extrapolated: %s - Dec" %(last_month_plus.strftime("%b"))] =  {
                "x": times_years,
                "y": np.array(values_extrapolated)}
            colors_plot.append(colors["extrapolated"])
        else:
            values_year_from_last_month = np.zeros(len(times_years))
            values_extrapolated = np.zeros(len(times_years))

        ### sum up consumption data for emission estimation 
        yearly_consumptions = (np.array(values_year_to_last_month)+
                               np.array(values_year_from_last_month) + 
                               np.array(values_extrapolated)) 
        
        data["data"]["Total"] = {"x": times_years,
                                 "y": yearly_consumptions}
        
        plot_single_go(title = "<b>%s</b>: yearly consumption" %(f),
                      filename = "AT_timeseries_consumption_%s_yearly" %(fossils[f]["save_name"]),
                      unit = "Consumption (%s)" %(units_plot[fossils[f]["options"]["unit"]]),
                      data_plot = data,
                      time_res = "yearly",
                      colors = colors_plot,
                      show_plot = plot,
                      unit_fac= 1, 
                      source_text = "eurostat (%s)" %(fossils[f]["code"]),
                      info_text = "Extrapolations based on monthly available data scaled with past trends",
                      plot_type = "bar")
    
        consumption[f] = {"data": {times_years[t]: yearly_consumptions[t] for t in range(len(times_years))},
                          "fac_mean": data_extrapolated["fac_mean"],
                          "std_energy": data_extrapolated["std_energy"]}
        
        
    for cat in fossil_categories:
        for f in fossil_categories[cat]: 
            fac = fossils[f]["NCV"]*fossils[f]["em_fac"]/1000
            values = np.array([consumption[f]["data"][t] for t in consumption[f]["data"]])*fac
            if cat in emissions_yearly["data"]: 
                emissions_yearly["data"][cat]["y"] += values 
            else: 
                emissions_yearly["data"][cat] = {"x": [t for t in consumption[f]["data"]],
                                     "y": values}    
                
    plot_with_toggle(title = "<b>Austrian CO2 emissions by fuels</b>: yearly (incl. projection)",
                  filename = "AT_timeseries_emissions_fuels_yearly",
                  unit = "Emissions (Mt<sub>CO2</sub>)",
                  data_plot = emissions_yearly,
                  time_res = "yearly",
                  show_plot = plot,
                  unit_fac= 1, 
                  source_text = "eurostat & own estimation | data of not fully available years are projected",
                  initial_visible = "bar")           
        
    return consumption 
    
def plot_emissions_fuels(): 
    
    data = {"data": {}}
    
    for cat in fossil_categories:
        for f in fossil_categories[cat]:
            fac = fossils[f]["NCV"]*fossils[f]["em_fac"]/1000
            
            ### MONTHLY 
            data_monthly = filter_eurostat_monthly(name = fossils[f]["file"],
                                                   code = fossils[f]["code"],
                                                   options = fossils[f]["options"],
                                                   unit = fossils[f]["options"]["unit"],
                                                   movmean = 12)
            if f in ["Diesel", "Gasoline"]: 
                data_monthly  = separate_bios(data_monthly, f) 
                
            ### rename bio values so that they can be processed 
            if f in ["Diesel", "Gasoline"]: 
                data_monthly["data"]["Monthly"] = data_monthly["data"]["%s Monthly" %(f)]
            
            ### YEARLY AND EXTRAPOLATION 
            data_raw = filter_fossil_extrapolation.cut_data_fossil(data_monthly)
    
            if cat in data["data"]: 
                data["data"][cat]["y"] += np.array([data_raw['values_months'][t]*fac for t in
                      data_raw['values_months']])
            else: 
                data["data"][cat] = {"x": [t for t in data_raw['values_months']],
                                     "y": np.array([data_raw['values_months'][t]*fac for t in
                                           data_raw['values_months']])}
       
        # ### 12 month averaging 
        # movmean = 12 
        # values_mean = []
        # times_mean = []
        # for t in range(len(data["data"][cat]["x"])-movmean+1):
        #     values_mean.append(np.mean(data["data"][cat]["y"][t:t+movmean]))
        #     times_mean.append(data["data"][cat]["x"][t+movmean-1])
            
        # data["data"][cat+" (12-Month average)"] = {"x": times_mean,
        #                                            "y": values_mean}
        
        
    plot_single_go(title = "<b>Austrian CO2 emissions by fuels</b>: monthly",
                  filename = "AT_timeseries_emissions_fuels_monthly",
                  unit = "Emissions (Mt<sub>CO2</sub>)",
                  data_plot = data,
                  time_res = "monthly",
                  show_plot = False,
                  unit_fac= 1, 
                  source_text = "eurostat & own estimation",
                  plot_type = "line")
    
    return data_raw

def extrapolate_emissions_by_cons(consumption, 
                          years_extrapolate = [2024,2025], 
                          train_start = 2019,
                          train_end = 2023,
                          plot = False): 

    times_train = pd.date_range(start = datetime(year = train_start, month = 1, day =1),
                          end = datetime(year = train_end, month = 1, day = 1),
                          freq="YS")    
    emissions_fuels = {}
    for f in consumption: 
        emissions_fuels[f] = []
        for t in times_train:
            emissions_fuels[f].append(consumption[f]["data"][t]*fossils[f]["NCV"]*fossils[f]["em_fac"]/1000)


    emissions_train = np.zeros(len(times_train))
    for f in fossils: 
        emissions_train = emissions_train + np.array(emissions_fuels[f])

    emissions_real = filter_uba_sectoral_emisssions()
    emissions_energy_years = []
    for time in times_train: 
        ind = emissions_real["data"]["Transport"]["x"].index(time)
        emissions_energy_years.append(emissions_real["data"]["Transport"]["y"][ind]+
                                     emissions_real["data"]["Buildings"]["y"][ind]+
                                     emissions_real["data"]["Energy & Industry"]["y"][ind])

    facs = []
    for t in range(len(times_train)):
        e_real = emissions_energy_years[t]
        e_train = emissions_train[t]
        facs.append(e_real/e_train)

    fac_mean = np.mean(np.array(facs))
    # fac_mean = np.average(np.array(facs), weights = np.linspace(1,3,len(facs)))
    # fac_mean = facs[-1]
    std_estimator = np.sqrt(np.var(facs)*len(facs)/(len(facs)-1.5))
    
    ### ESTIMATE EMISSIONS AND EXTRAPOLATE     
    times_projected = pd.date_range(start = datetime(year = years_extrapolate[0], month = 1, day =1),
                          end = datetime(year = years_extrapolate[-1], month = 1, day = 1),
                          freq="YS")

    emissions_energy_model = [0 for i in range(len(times_projected))]
    emissions_energy_projected = []
    std_emission_projected = []
    std_consumption_projected = [0 for i in range(len(times_projected))]
    total_std = []
    
    for i in range(len(times_projected)):
        time_project = times_projected[i]
        
        ### project energy emissions by projected consumption 
        for f in fossils: 
            emissions_energy_model[i] += consumption[f]["data"][time_project]*fossils[f]["NCV"]*fossils[f]["em_fac"]/1000
        emissions_energy_projected.append(emissions_energy_model[i]*fac_mean)

        ### estimate std of projection (energy-based to total emissions)
        std_emission_projected.append(emissions_energy_projected[i]*std_estimator)
    
        ### estimated std of extrapolation 
        for f in consumption: 
            ### in case no projection was made to projection year, set error to zero (full data available)
            time_project_plus_one = datetime(year = years_extrapolate[i]+1, month= 1, day=1)
            if time_project_plus_one in consumption[f]["data"]:
                pass 
            else:
                std_consumption_projected[i] += (consumption[f]["std_energy"]*fossils[f]["NCV"]*fossils[f]["em_fac"]/1000 
                                         * fac_mean)
            
        total_std.append(std_emission_projected[i] + std_consumption_projected[i])
            
    ### for agriculture, fluorinated gases and waste, extrapolate current emission trends 
    emissions_rest_years = (np.array(emissions_real["data"]["Agriculture"]["y"]) + 
                            np.array(emissions_real["data"]["Waste"]["y"]) + 
                            np.array(emissions_real["data"]["Fluorinated Gases"]["y"])) 
    
    emissions_energy_years = (np.array(emissions_real["data"]["Transport"]["y"]) + 
                            np.array(emissions_real["data"]["Buildings"]["y"]) + 
                            np.array(emissions_real["data"]["Energy & Industry"]["y"]))     
    
    times_historic = emissions_real["data"]["Agriculture"]["x"]
    emissions_historic = emissions_energy_years+emissions_rest_years
    ind_last = times_historic.index(times_train[-1])
    
    emission_rest_trend_year = (emissions_rest_years[ind_last]-emissions_rest_years[ind_last-3])/3    
    
    emissions_rest_projected = []
    projected_emissions = [emissions_historic[ind]]
    times_projected_plot = [times_historic[ind]]
    for i in range(len(times_projected)):
        emissions_rest_projected.append(emissions_rest_years[ind_last] + (i+1)*emission_rest_trend_year)
        projected_emissions.append(emissions_energy_projected[i] + emissions_rest_projected[i])
        times_projected_plot.append(times_projected[i])

    times_total = times_historic + times_projected_plot[1:]
    emissions_energy_sectors = list(emissions_energy_years) + emissions_energy_projected
    emissions_rest_sectors = list(emissions_rest_years) + emissions_rest_projected
    
    data_plot = {"data": {"Energy sectors": {"x": times_total,
                                              "y": emissions_energy_sectors},
                          "Other sectors": {"x": times_total,
                                            "y": emissions_rest_sectors},
                          "Projeted emissions": {"x": times_projected_plot,
                                                 "y": projected_emissions},
                          "Historic emissions": {"x": times_historic,
                                                 "y": emissions_historic}
                          }}
    
    data_plot["meta"] = {"uncertainty": {"Projeted emissions": [0] + total_std},
                         "areas": ["Energy sectors", "Other sectors"]}
    
    if plot:
        plot_single_go(title = "<b>Austrian GHG emissions</b>: projection",
                      filename = "AT_timeseries_emissions_projection_yearly",
                      unit = "Emissions (Mt<sub>CO2e</sub>)",
                      data_plot = data_plot,
                      time_res = "yearly",
                      show_plot = plot,
                      unit_fac= 1, 
                      source_text = f"Umweltbundesamt, eurostat & own projection (train years {train_start}-{train_end})",
                      plot_type = "line")
    
    data_out = {"emissions_energy_projected": emissions_energy_projected,
                "std_emission_projected": std_emission_projected,
                "std_consumption_projected": std_consumption_projected,
                "emissions_rest_projected": emissions_rest_projected}
    
    
    return data_out
    


def extrapolate_emissions(plot = True): 
    consumption = extrapolate_fossil_fuels(plot = False)
    extrapolate_emissions_by_cons(consumption, plot = plot) 
    

def plot_extrapolation_demo(): 
    """ plot a simple demo to show how the extrapolation of fossil fuel consumption works """ 
    year_plot = 2022
    
    ### commodity extrapolation demo 
    demos = ["Natural gas", "Diesel", "Coke oven coke"]
    data_plot = {}
    
    for f in demos: 
        data_monthly = filter_eurostat_monthly(name = fossils[f]["file"],
                                                code = fossils[f]["code"],
                                                options = fossils[f]["options"],
                                                unit = fossils[f]["options"]["unit"],
                                                movmean = 12)
        data_raw = filter_fossil_extrapolation.cut_data_fossil(data_monthly)
                
        data_plot[f] = {}
        last_months = np.arange(1,13)
        data_plot[f] = {"last_months": last_months,
                        "extrapolated_data": [],
                        "std_data": [],
                        "actual_consumption_year": [data_raw["values_year"][year_plot] for i in range(12)],
                        "actual_consumption_to_month": [],
                        "facs_mean": []}
        
        for last_month in last_months: 
            data = filter_fossil_extrapolation.extrapolate_data_fossil(data_raw, 
                                            last_year_raw = year_plot, 
                                            last_month_raw = last_month)
            
            data_plot[f]["extrapolated_data"].append(data["extrapolated_year"])
            data_plot[f]["std_data"].append(data["std_energy"])
            data_plot[f]["actual_consumption_to_month"].append(data["consumption_to_month"])
            data_plot[f]["facs_mean"].append(data["fac_mean"])
        data_plot[f]["unit"] = fossils[f]["options"]["unit"]
    
    filter_fossil_extrapolation.plot_data_fossils(data_plot, 
                                                  year_plot = year_plot)
    
    ### emissions estimations demo 
    data_out = {}
    last_months = np.arange(1,13)
    for last_month in last_months: 
        print("Projecting from month %i/12" %(last_month))
        consumption = {}
        for f in fossils: 
            data_monthly = filter_eurostat_monthly(name = fossils[f]["file"],
                                                    code = fossils[f]["code"],
                                                    options = fossils[f]["options"],
                                                    unit = fossils[f]["options"]["unit"],
                                                    movmean = 12)
            if f in ["Diesel", "Gasoline"]: 
                data_monthly  = separate_bios(data_monthly, f) 
                data_monthly["data"]["Monthly"] = data_monthly["data"]["%s Monthly" %(f)]
        
            data_raw = filter_fossil_extrapolation.cut_data_fossil(data_monthly)
            data_extrapolated = filter_fossil_extrapolation.extrapolate_data_fossil(data_raw, 
                                            last_year_raw = year_plot, 
                                            last_month_raw = last_month)
            times_years = pd.date_range(start = datetime(year = 2008, month = 1, day =1),
                                  end = datetime(year = year_plot, month = 1, day = 1),
                                  freq="YS")
            
            values_year_to_last_month = [data_raw["values_year_to_last_month"][time.year] for time in times_years]
            values_year_from_last_month = [data_raw['values_year_from_last_month'][time.year] for time in times_years]
            yearly_consumptions = (np.array(values_year_to_last_month)+
                                    np.array(values_year_from_last_month))
            yearly_consumptions[-1] = data_extrapolated["extrapolated_year"] 

            consumption[f] =  {"data": {times_years[t]: yearly_consumptions[t] for t in range(len(times_years))},
                              "fac_mean": data_extrapolated["fac_mean"],
                              "std_energy": data_extrapolated["std_energy"]}
            
        data = extrapolate_emissions_by_cons(consumption, 
                                      year_extrapolate = year_plot,
                                      train_start = 2008,
                                      train_end = year_plot-1,
                                      plot = False)    
            
        data_out[last_month] = {"emissions_model": data["emissions_rest_projected"]+data["emissions_energy_projected"],
                        "std_emission_projected":  data["std_emission_projected"],
                        "std_consumption_projected": data["std_consumption_projected"]}

    
    emissions_real = filter_uba_sectoral_emisssions()
    emissions_year = 0
    time_projected = times_years[-1]
    ind = emissions_real["data"]["Transport"]["x"].index(time_projected)
    for sector in  ["Transport", "Energy & Industry", "Agriculture", "Buildings", "Waste", "Fluorinated Gases"]:
        emissions_year += emissions_real["data"][sector]["y"][ind]

    projected_emissions = np.array([data_out[month]["emissions_model"] for month in last_months])
    error_emission_projection = np.array([data_out[month]["std_emission_projected"] for month in last_months])
    error_consumption_projection = np.array([data_out[month]["std_consumption_projected"] for month in last_months])
    emission_errors = error_emission_projection + error_consumption_projection

    fig,ax = plt.subplots(2,1)
    fig.set_size_inches(7,2*3)
    ax[0].plot(last_months, np.ones(len(last_months))*emissions_year, label = "Actual emissions") 
    ax[0].plot(last_months, projected_emissions, label = "Projected emissions") 

    ax[0].fill_between(last_months, 
                        projected_emissions-emission_errors/2,
                        projected_emissions+emission_errors/2,
                        alpha = 0.3,
                        label = "Estimated standard deviation")
    
    ax[0].set_title("CO2 emission extrapolatoin of 2022 using monthly data") 
    ax[0].set_ylim([0, emissions_year*1.2])
    ax[0].legend() 
    ax[0].set_ylabel("CO2 emissions (Mt_CO2e)")
    ax[0].grid() 


    ax[1].plot(last_months, error_consumption_projection, label = "Uncertainty fossil fuel consumtion extrapolation") 
    ax[1].plot(last_months, error_emission_projection, label = "Uncertainty emission scaling") 
    ax[1].set_ylim([0, max([max(error_consumption_projection),
                            max(error_emission_projection)])*1.1])
    ax[1].legend() 
    ax[1].set_ylabel("CO2 emissions (Mt_CO2e)")
    ax[1].set_xlabel("Month")
    ax[1].grid() 
    
    plt.tight_layout() 
    plt.savefig(os.path.join(os.path.dirname(__file__), 
                             "../../docs/assets/images/emissions_projection_2022.png"), dpi = 400)
    

    return data_out 
    

def plot_emission_estimate_demo(): 
    emissions = {}
    end_year = 2022 
    start_year = 2008
    times = pd.date_range(start = datetime(year = start_year, month = 1, day =1),
                          end = datetime(year = end_year, month = 1, day = 1),
                          freq="YS")
                              
    for f in fossils: 
        ### MONTHLY 
        data_monthly = filter_eurostat_monthly(name = fossils[f]["file"],
                                               code = fossils[f]["code"],
                                               options = fossils[f]["options"],
                                               unit = fossils[f]["options"]["unit"],
                                               movmean = 12)
        if f in ["Diesel", "Gasoline"]: 
            data_monthly = separate_bios(data_monthly, f)
            data_monthly["data"]["Monthly"] = data_monthly["data"]["%s Monthly" %(f)]

        
        ### YEARLY AND EXTRAPOLATION 
        data_raw = filter_fossil_extrapolation.cut_data_fossil(data_monthly)
        
        emissions_years = []
        for time in times: 
            emissions_years.append(data_raw["values_year"][time.year])
        emissions[f] = np.array(emissions_years)*fossils[f]["NCV"]*fossils[f]["em_fac"]/1000
        

    total_emissions = np.zeros(len(times))
    for f in fossils: 
        total_emissions = total_emissions +  emissions[f]
        
    emissions_real = filter_uba_sectoral_emisssions()
    emissions_energy_years = []
    for time in times: 
        ind = emissions_real["data"]["Transport"]["x"].index(time)
        emissions_energy_years.append(emissions_real["data"]["Transport"]["y"][ind]+
                                     emissions_real["data"]["Buildings"]["y"][ind]+
                                     emissions_real["data"]["Energy & Industry"]["y"][ind])



    facs = []
    for t in range(len(times)):
        actual_emissions = emissions_energy_years[t]
        calculated_emissions = total_emissions[t]
        facs.append(actual_emissions/calculated_emissions)
    
    fac_mean = np.mean(np.array(facs))
    std_estimator = np.sqrt(np.var(facs)*len(facs)/(len(facs)-1.5))
    
    emissions_extrapolated = np.zeros(len(times))
    emission_errors = np.zeros(len(times))
    for t in range(len(times)):
        emissions_extrapolated[t] = total_emissions[t]*fac_mean
        emission_errors[t] = total_emissions[t]*std_estimator
        
    fig,ax = plt.subplots(2,1)
    fig.set_size_inches(7,2*3)

    ax[0].plot(times, total_emissions, label = "Estimated emissions") 
    ax[0].plot(times, emissions_energy_years, label = "Actual emissions Energy-sectors") 
    ax[0].legend() 
    ax[0].set_ylim([0, max(emissions_energy_years)*1.1])
    ax[0].set_ylabel("CO2 emissions (Mt)")
    ax[0].grid() 
    
    
    ax[1].plot(times, emissions_extrapolated, label = "Scaled emissions") 
    ax[1].plot(times, emissions_energy_years, label = "Actual emissions Energy-sectors") 

    ax[1].fill_between(times, 
                          emissions_extrapolated-emission_errors,
                          emissions_extrapolated+emission_errors,
                          alpha = 0.3,
                          label = "Scaling standard deviation")
    ax[1].set_ylim([0, max(emissions_energy_years)*1.1])
    ax[1].legend() 
    ax[1].set_ylabel("CO2 emissions (Mt)")
    ax[1].set_xlabel("Year")
    ax[1].grid() 
    
    plt.tight_layout() 
    plt.savefig(os.path.join(os.path.dirname(__file__), 
                             "../../docs/assets/images/emissions_estimation.png"), dpi = 400)
    
    return emissions    




def plot_ng_separation(): 
    TJ_NCV_to_1000m3 = 0.03723 #TJ_NCV / 1000M3 
    TJ_GCV_to_1000m3 = 0.03914 #TJ_GCV / 1000m3 
    cats = {"Total": "Inland consumption - calculated as defined in MOS GAS [IC_CAL_MG]",
            "Public electricity / heat": "Transformation input - electricity and heat generation - main activity producers [TI_EHG_MAP]",
            "Buildings": "Final consumption - other sectors [FC_OTH]"}
    data = {"data": {}}
    for cat in cats:
        data_monthly = filter_eurostat_monthly(name = fossils["Natural gas"]["file"],
                                               code = fossils["Natural gas"]["code"],
                                               options =  {"unit": "TJ_GCV",
                                                            "nrg_bal": cats[cat]},
                                               start_year = 2019,
                                               unit = fossils["Natural gas"]["options"]["unit"],
                                               movmean = 12)
        
        data["data"][cat] = {"x": data_monthly["data"]["Monthly"]["x"],
                             "y": np.array(data_monthly["data"]["Monthly"]["y"])*TJ_GCV_to_1000m3/ TJ_NCV_to_1000m3 / 3.6e3}
    

    buildings_temp = np.zeros(len(data["data"]["Total"]["x"]))
    buildings_temp[-len(data["data"]["Buildings"]["y"]):] = data["data"]["Buildings"]["y"]
    
    elec_temp = np.zeros(len(data["data"]["Total"]["x"]))
    elec_temp[-len(data["data"]["Public electricity / heat"]["y"]):] = data["data"]["Public electricity / heat"]["y"]
    
    data["data"]["Public electricity / heat"]["y"] = elec_temp
    data["data"]["Buildings"]["y"] = buildings_temp
    
    data["data"]["Public electricity / heat"]["x"] = data["data"]["Total"]["x"]
    data["data"]["Buildings"]["x"] = data["data"]["Total"]["x"]

    
    data["data"]["Industry / Other"] = {"x": data["data"]["Total"]["x"],
                         "y": data["data"]["Total"]["y"] - (
                             data["data"]["Public electricity / heat"]["y"]+
                             data["data"]["Buildings"]["y"])}
    
    ### bring total on top
    data_plot = {"data": {"Industry / Other": data["data"]["Industry / Other"],
                          "Buildings": data["data"]["Buildings"],
                          "Public electricity / heat": data["data"]["Public electricity / heat"],
                          "Total": data["data"]["Total"]}}
    plot_with_toggle(title = "<b>Austria:</b> monthly natural gas consumption by sector",
                  filename = "AT_timeseries_gas_sectoral_consumption_monthly",
                  unit = "Energy (TWh)", 
                  data_plot = data_plot,
                  time_res = "monthly",
                  show_plot = False,
                  source_text = "eurotsat (NRG_CB_GASM)",
                  info_text = "Bulidings data before 09/2023 not available.",
                  initial_visible = "bar")


    ### yearly with bars 
    
    max_month = data_plot["data"][cat]["x"][-1].month 
    
    if max_month == 12: 
        data_yearly_raw = {cat: {} for cat in data_plot["data"]}

        for cat in data_plot["data"]: 
            years = []
            for t in range(len(data_plot["data"][cat]["x"])): 
                date = data_plot["data"][cat]["x"][t]
                if date.year in years: 
                    date_save = datetime(year = date.year, month = 1, day = 1)
                else: 
                    years.append(date.year) 
                    date_save = datetime(year = date.year, month = 1, day = 1)
                    data_yearly_raw[cat][date_save] = 0 
                data_yearly_raw[cat][date_save] += data_plot["data"][cat]["y"][t]
    
        data_yearly_abs = {"data": {cat: {"x": np.array([date for date in data_yearly_raw[cat]]),
                                  "y": np.array([data_yearly_raw[cat][date] for date in data_yearly_raw[cat]])}
                            for cat in data_yearly_raw}}  
        
    
        plot_with_toggle(title = "<b>Austria:</b> yearly natural gas consumption by sector",
                      filename = "AT_timeseries_gas_sectoral_consumption_yearly",
                      unit = "Energy (TWh)", 
                      data_plot = data_yearly_abs,
                      time_res = "yearly",
                      show_plot = True,
                      source_text = "eurotsat (NRG_CB_GASM)",
                      info_text = "Bulidings data before 09/2023 not available.",
                      initial_visible = "bar")
        
    else: 
        data_yearly_raw = {}
        for cat in data_plot["data"]: 
            if cat != "Total": 
                data_yearly_raw[f"{cat}: Jan-{months[max_month]}"] = {}
                data_yearly_raw[f"{cat}: {months[max_month+1]}-Dec"] = {} 
            else: 
                data_yearly_raw["Total"] = {}
        
        for cat in data_plot["data"]: 
            if cat != "Total": 
                years = []
                for t in range(len(data_plot["data"][cat]["x"])): 
                    date = data_plot["data"][cat]["x"][t]
                    if date.year in years: 
                        date_save = datetime(year = date.year, month = 1, day = 1)
                    else: 
                        years.append(date.year) 
                        date_save = datetime(year = date.year, month = 1, day = 1)
                        data_yearly_raw[f"{cat}: Jan-{months[max_month]}"][date_save] = 0 
                        data_yearly_raw[f"{cat}: {months[max_month+1]}-Dec"][date_save] = 0 
                    if data_plot["data"][cat]["x"][t].month <= max_month: 
                        data_yearly_raw[f"{cat}: Jan-{months[max_month]}"][date_save] += data_plot["data"][cat]["y"][t]
                    else: 
                        data_yearly_raw[f"{cat}: {months[max_month+1]}-Dec"][date_save] += data_plot["data"][cat]["y"][t]
            else: 
                years = []
                for t in range(len(data_plot["data"][cat]["x"])): 
                    date = data_plot["data"][cat]["x"][t]
                    if date.year in years: 
                        date_save = datetime(year = date.year, month = 1, day = 1)
                    else: 
                        years.append(date.year) 
                        date_save = datetime(year = date.year, month = 1, day = 1)
                        data_yearly_raw[cat][date_save] = 0 
                    data_yearly_raw[cat][date_save] += data_plot["data"][cat]["y"][t]
                    
        data_yearly_abs = {"data": {cat: {"x": np.array([date for date in data_yearly_raw[cat]]),
                                  "y": np.array([data_yearly_raw[cat][date] for date in data_yearly_raw[cat]])}
                            for cat in data_yearly_raw}}  
        
    
        plot_with_toggle(title = "<b>Austria:</b> yearly natural gas consumption by sector",
                      filename = "AT_timeseries_gas_sectoral_consumption_yearly",
                      unit = "Energy (TWh)", 
                      data_plot = data_yearly_abs,
                      time_res = "yearly",
                      colors = [dark2[0], set2[0], dark2[1], set2[1], dark2[2], set2[2]],
                      show_plot = True,
                      source_text = "eurotsat (NRG_CB_GASM)",
                      info_text = "Bulidings data before 09/2023 not available.",
                      initial_visible = "bar")
        
        

    return data
                                           
    
if __name__ == "__main__":
    print("Plotting ...")
    # extrapolate_fossil_fuels()
    # data = extrapolate_emissions(plot = True)
    
    data = plot_ng_separation()
    
    # data = plot_extrapolation_demo()
    # plot_emission_estimate_demo()
    
    # data = plot_emissions_fuels()
