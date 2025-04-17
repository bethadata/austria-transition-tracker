# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 17:23:46 2024

@author: Bernhard
"""

import pandas as pd 
from datetime import datetime
import numpy as np 
import os 
import json 


car_categories = {"Diesel": ["Diesel (excluding hybrids) [DIE_X_HYB]"],
              "Gasoline": ["Petrol (excluding hybrids) [PET_X_HYB]"],
              "Hybrid": ["Hybrid electric-petrol [ELC_PET_HYB]", 
                         "Hybrid diesel-electric [ELC_DIE_HYB]"],
              "Hybrid plugin": ["Plug-in hybrid diesel-electric [ELC_DIE_PI]",
                                "Plug-in hybrid petrol-electric [ELC_PET_PI]"],
              "Electric": ["Electricity [ELC]"],
              "Other": ["Liquefied petroleum gases (LPG) [LPG]", 
                        "Natural Gas [GAS]", 
                        "Hydrogen and fuel cells [HYD_FCELL]", 
                        "Bioethanol [BIOETH]", 
                        "Biodiesel [BIODIE]", 
                        "Bi-fuel [BIFUEL]", 
                        "Other [OTH]"]}


months = {"Jaenner": 1, "Februar": 2, "Maerz": 3, "April": 4,
          "Mai": 5, "Juni": 6, "Juli": 7, "August": 8,
          "September": 9, "Oktober": 10, "November": 11, "Dezember": 12}

def pandas_to_dict(data, options, unit): 
    data_filtered = data[(data["unit"] == unit)]
    for option in options: 
        data_filtered = data_filtered[data_filtered[option] == options[option]]
        
    data_trim = {}
    for time in data_filtered.keys():
        ### monthly data 
        if "-" in time and len(time) == 7:
            if len(data_filtered[time]) == 0: 
                data_trim[time] = 0
            else:
                data_trim[time] = float(data_filtered[time].iloc[0])
            
        ### yearly data 
        elif ("20" in time or "19" in time) and len(time) == 4: 
            if len(data_filtered[time]) == 0: 
                data_trim[time] = 0
            else:
                data_trim[time] = float(data_filtered[time].iloc[0])
        
        if time in data_trim and np.isnan(data_trim[time]): 
            data_trim[time] = 0
            
    return data_trim 
        
        

def filter_eurostat_monthly(name = "meat",
                      code = "",
                       geo = "AT",
                       start_year = 1990,
                       options = {},
                       unit = "",
                       movmean = 4): 
    """ reads the raw eurostat data and processes it according to defined inupts 
    
    outputs are: 
        data_monthly
        data_monthly_mean 
    
    """
    
    data = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                              "../../data_raw/eurostat/%s_%s_%s.xlsx" %(geo, name, code)))
    data = data.fillna(0)
    data_trim = pandas_to_dict(data, options, unit)

    ### syntax change chicken => poultry of eurostat 
    if name == "meat" and options["meat"] == "Chicken [B7100]": 
        data_poultry = pandas_to_dict(data, 
                                      {"meat": "Poultry meat [B7000]",
                                      "meatitem": "Slaughterings [SLAUGHT]"}, 
                                      unit)
        for time in data_poultry.keys():
            date = datetime.strptime(time, "%Y-%m")
            if date >= datetime(year = 2022, month = 1, day = 1): 
                data_trim[time] = data_poultry[time]
                
            if (date >= datetime(year = 2004, month = 12, day = 1) and 
                date <= datetime(year = 2008, month = 12, day = 1)): 
                data_trim[time] = data_poultry[time]

    years_trim = [time for time in data_trim]
    for time in years_trim: 
        if sum(data[time]) > 0: 
            end_year = int(time.split("-")[0])
            last_month = int(time.split("-")[1])


    # end_year = int(years_trim[-1].split("-")[0])
    
    for time in data_trim: 
        if data_trim[time] > 0: 
            start_year_data = int(time.split("-")[0])
            break 
    start_year = max(start_year, start_year_data)
    
    times = pd.date_range(start = datetime(year = start_year, month = 1, day =1),
                          end = datetime(year = end_year+1, month = 1, day = 1),
                          freq="MS")

    # ### find last key with columns 
    # for month in range(1, 13):
    #     if "%i-%02i" %(end_year, month) in data: 
    #         if sum(data["%i-%02i" %(end_year, month)] > 0):
    #             last_month = month 

    times_plot = []
    values = []
    for time in times: 
        if time.year > end_year: 
            pass
        elif time.year == end_year and time.month > last_month: 
            pass 
        else: 
            time_key = "%i-%02i" %(time.year, time.month)
            if time_key not in data.keys(): value = 0 
            else: value = data_trim[time_key]
            
            times_plot.append(time)
            values.append(value)

    times_plot_mean = []
    values_mean = []
    
    for t in range(len(times_plot)-movmean+1):
        values_mean.append(np.mean(values[t:t+movmean]))
        times_plot_mean.append(times_plot[t+movmean-1])
        
    data_out = {"data": {"Monthly": {"x": times_plot,
                            "y": values},
                        "%i-Month average" %(movmean): {"x": times_plot_mean,
                                          "y": values_mean}
                        },
                "meta": {"movmean": movmean,
                         "code": code}
                }

    return data_out



def filter_car_registrations():
    """ 
    reads and combines car registration data, obtained from eurostat (until 2018) on
    yearly basis, and from statistik austria on monthly basis (starting 2019)
    
    """     
    
    ### 1st step, load eurostat and transform yearly to monthly data
    
    data_yearly = {}
    data_eurostat = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                              "../../data_raw/eurostat/AT_cars_road_eqr_carpda.xlsx"))
    years_eurostat = [2013,2014,2015,2016,2017,2018] 

    for cat in car_categories:
        data_yearly[cat] = {str(year): 0 for year in years_eurostat}
        for subcat in car_categories[cat]:            
            data_trim = pandas_to_dict(data_eurostat, 
                                       {"mot_nrg": subcat}, 
                                       "NR")
            for y in years_eurostat:
                data_yearly[cat][str(y)] += data_trim[str(y)]
    
    times_eurostat = pd.date_range(
        start = datetime(year = years_eurostat[0], month = 1, day = 1),
        end = datetime(year = years_eurostat[-1], month = 12, day = 1),
        freq="MS")
    
    data_monthly = {cat: {} for cat in car_categories}
    
    for time in times_eurostat: 
        for cat in car_categories: 
            value_year = data_yearly[cat][str(time.year)]
            data_monthly[cat][time] = value_year/12 
    
    data_total = {time: sum([data_monthly[cat][time] for cat in car_categories]) for 
                  time in times_eurostat}
    data_monthly["Total"] = data_total  
    
    ### 2nd step, add Statistik Austria data   
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]

    
    labels = {"Total": "Pkw insgesamt", 
              "Gasoline": "Benzin", 
              "Diesel": "Diesel",
              "Electric": "Elektro"}
    
    ### check which file exists 
    for year in years: 
        file_found = False 
        for month in reversed(months):   
            filename = "NeuzulassungenFahrzeugeJaennerBis%s%i" %(month, year)
            filepath = os.path.join(os.path.dirname(__file__), 
                "../../data_raw/statistik_austria/Fahrzeuge/%s.xlsx" %(filename))            
            if os.path.exists(filepath) and not file_found:
                file_found = True 
                month_list = list(months.keys())
                for month_name in month_list[:month_list.index(month)+1]:
                    time = pd.to_datetime(datetime(year = year, 
                                    month = month_list.index(month_name)+1,
                                    day = 1))

                    if month_name == "Maerz": month_name = "März"
                    elif month_name == "Jaenner": month_name = "Jänner"
                                        
                    data_sa = pd.read_excel(filepath, sheet_name = month_name)
                    number = data_sa["Unnamed: 1"]
                    column = data_sa["Tabelle 1a: Kfz-Neuzulassungen"]

                    for label in labels: 
                        found = False 
                        for c in range(len(column)): 
                            if str(column[c])[:len(labels[label])] == labels[label] and not found: 
                                found = True
                                data_monthly[label][time] = float(number[c])
                   
                    ### count hybrids separately tu sum up diesel and gasoline 
                    hybrids = 0
                    plugins = 0
                    for label in ["Benzin/Elektro", "Diesel/Elektro"]: 
                        found = False 
                        for c in range(len(column)): 
                            if str(column[c])[:14] == label and not found: 
                                hybrids += float(number[c])-float(number[c+1])
                                plugins += float(number[c+1])
                                found = True 
                                
                    data_monthly["Hybrid"][time] = hybrids 
                    data_monthly["Hybrid plugin"][time] = plugins 

                    data_monthly["Other"][time] =  (data_monthly["Total"][time] -
                                                    data_monthly["Diesel"][time] -
                                                    data_monthly["Gasoline"][time] - 
                                                    data_monthly["Electric"][time] - 
                                                    data_monthly["Hybrid"][time] - 
                                                    data_monthly["Hybrid plugin"][time])
    return data_monthly 


def filter_eurostat_yearly(name = "meat",
                      code = "",
                        geo = "AT",
                        options = {},
                        unit = "",
                        start_year = 1990,
                        end_year = 2100): 
    """ reads the raw eurostat data and processes it according to defined inupts 
    
    outputs are: 
        data_yearly 
    
    """
    
    data = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                              "../../data_raw/eurostat/%s_%s_%s.xlsx" %(geo, name, code)))
    data = data.fillna(0)
    data_trim = pandas_to_dict(data, options, unit)    

    ### find last key with columns 
    startyear_found = False 
    for year in range(start_year, end_year+1):
        if str(year) in data_trim and not startyear_found:
            start_year = year 
            startyear_found = True
        elif str(year) in data_trim: 
            end_year = year 
            
    times = pd.date_range(start = datetime(year = start_year, month = 1, day =1),
                          end = datetime(year = end_year, month = 1, day = 1),
                          freq="YS")
    times_plot = []
    values = []
    for time in times: 
        time_key = "%i" %(time.year)
        
        if time_key not in data_trim.keys(): 
            pass
        else:
            times_plot.append(time)
            values.append(data_trim[time_key])
        
        
    data_out = {"data": {name: {"x": times_plot,
                            "y": values},
                        },
                "meta": {"code": code}
                }
    return data_out

def filter_railways():
    data_total = filter_eurostat_yearly(name = "rail_tracks", code = "rail_if_line_tr",
                                  options = {"tra_infr":"Total [TOTAL]",
                                             "n_tracks": "Total [TOTAL]"},
                                  unit = "KM", start_year = 1900)
    data_electr = filter_eurostat_yearly(name = "rail_tracks", code = "rail_if_line_tr",
                                  options = {"tra_infr":"Electrified railway lines [RL_ELC]",
                                             "n_tracks": "Total [TOTAL]"},
                                  unit = "KM", start_year = 1990)
    data_non_electr = filter_eurostat_yearly(name = "rail_tracks", code = "rail_if_line_tr",
                                  options = {"tra_infr":"Non-electrified railway lines [RL_NELC]",
                                             "n_tracks": "Total [TOTAL]"},
                                  unit = "KM", start_year = 1990)
    names = {"Electrified": data_electr,
             "Non-electrified": data_non_electr,
             "Total": data_total}
    
    data_out = {"data": {name: {} for name in names}}
    for name in names: 
        x = names[name]["data"]["rail_tracks"]["x"]
        y = names[name]["data"]["rail_tracks"]["y"]
        data_out["data"][name]["x"] = x 
        data_out["data"][name]["y"] = y 

    data_rel = {"data": {"Electrified": {"x": data_out["data"]["Electrified"]["x"],
                                         "y": np.array(data_out["data"]["Electrified"]["y"])/np.array(data_out["data"]["Total"]["y"])
                                         },
                         "Non-electrified": {"x": data_out["data"]["Non-electrified"]["x"],
                                            "y": np.array(data_out["data"]["Non-electrified"]["y"])/np.array(data_out["data"]["Total"]["y"])
                                            },
                         }
                }
    
    return data_out, data_rel


def filter_eurostat_monnthly_to_yearly(name = "oil",
                                       code = "NRG_CB_OILM",
                                       geo = "AT",
                                       start_year = 2013,
                                       options = {"unit": "THS_T",
                                                  "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                                  "siec": "Oil products [O4600]"},
                                       unit = "THS_T"): 
    
    data_file = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                              "../../data_raw/eurostat/%s_%s_%s.xlsx" %(geo, name, code)))
    data_file = data_file.fillna(0)
    data_trim = pandas_to_dict(data_file, options, unit)

    
    ### find last key with columns 
    for year in [1990+i for i in range(100)]:
        for month in range(1, 13):
            if "%i-%02i" %(year, month) in data_file: 
                if sum(data_file["%i-%02i" %(year, month)] > 0):
                    last_year = year 
                    last_month = month 

    times_months = pd.date_range(start = datetime(year = start_year, month = 1, day =1),
                          end = datetime(year = last_year+1, month = 1, day = 1),
                          freq="ME")
    
    times_years = pd.date_range(start = datetime(year = start_year, month = 1, day =1),
                          end = datetime(year = last_year, month = 1, day = 1),
                          freq="YS")
    
    data = {year: 0 for year in range(start_year, last_year+1)}
    data_months = {}
    for time in times_months: 
        if time.year == last_year and time.month > last_month: 
            pass 
        else: 
            time_key = "%i-%02i" %(time.year, time.month)
            
            if time_key not in data_file.keys(): value = 0 
            else: value = data_trim[time_key]
            
            data[time.year] += value 
            data_months[time] = value
    
    values_extrapolated = np.zeros(len(times_years))
    

    if last_month != 12: 
        ### extrapolation of missing months 
        ### get medium consumption increase of months to last month of previous three years 
        facs = []
        years_to_consider = 10
        for year in [last_year-years_to_consider+i for i in range(years_to_consider)]:
            consumption_year = data[year]
            consumption_to_last_month = 0
            for time in times_months: 
                if time.year == year and time.month <= last_month: 
                    consumption_to_last_month += data_months[time]
            facs.append(consumption_year/consumption_to_last_month)
        fac_mean = np.mean(np.array(facs))
        values_extrapolated[-1] = data[last_year] * fac_mean 
        
    std_estimator = np.sqrt(np.var(facs)*len(facs)/(len(facs)-1))
    std_energy = data[last_year] * std_estimator/2
          
    data_out = {"data": {"Actual consumption": {"x": times_years,
                                                "y": [data[year] for year in data]},
                        "Extrapolated": {"x": times_years,
                                          "y": values_extrapolated}
                        },
                "meta": {"last_year": last_year,
                         "last_month": last_month,
                         "fac_mean": fac_mean,
                         "facs": facs,
                         "std_estimator": std_estimator,
                         "std_energy": std_energy,
                         "code": code}
                }

    return data_out


def extend_car_registr(data_out, filepath, year, skiprows = 2,
                       tot = "Personenkraftwagen Kl. M1 insgesamt", sheet_name = "tab_1" ): 
    data_ext =  pd.read_excel(filepath, decimal = ",", skiprows = skiprows, sheet_name = sheet_name)
    number = np.array(data_ext.iloc[:, [1]])
    column = np.array(data_ext.iloc[:, [0]])
    time_ext = datetime(year = year, month = 1, day = 1)
    data_out["Total"][time_ext] = float(number[column == tot][0])
    data_out["Diesel"][time_ext] = float(number[column == "Diesel"][0])
    data_out["Gasoline"][time_ext] = float(number[column == "Benzin inkl. Flex-Fuel"][0])
    data_out["Hybrid"][time_ext] = (float(number[column == "Benzin/Elektro (hybrid)"][0])+
                                float(number[column == "Diesel/Elektro (hybrid)"][0]))
    data_out["Electric"][time_ext] = float(number[column == "Elektro"][0])
    data_out["Other"][time_ext] = data_out["Total"][time_ext]-sum(
        [data_out[cat][time_ext] for cat in ["Diesel", "Gasoline", "Hybrid", "Electric"]])
    data_out["Hybrid plugin"][time_ext] = 0 
    
    return data_out


def filter_eurostat_cars(file = "AT_cars_road_eqs_carpda",
                         options = {}): 
    data_yearly = {}
    data_eurostat = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                              "../../data_raw/eurostat/%s.xlsx" %(file)))

    data_eurostat = data_eurostat.fillna(0)
        
    ## find range of years in dataframe 
    startyear_found = False 
    for year in [1990+i for i in range(100)]:
        if "%i" %(year) in data_eurostat and not startyear_found: 
            if sum(data_eurostat["%i" %(year)]) > 0:
                start_year = year
                startyear_found = True 
        elif "%i" %(year) in data_eurostat and sum(data_eurostat["%i" %(year)]) > 0:
            end_year = year 
        

    ### filter car data in categories 
    years_eurostat = [start_year+i for i in range(end_year+1-start_year)]
    for cat in car_categories:
        data_yearly[cat] = {str(year): 0 for year in years_eurostat}
        for subcat in car_categories[cat]:     
            options["mot_nrg"] = subcat 
            data_trim = pandas_to_dict(data_eurostat, 
                                       options, 
                                       "NR")
            for y in years_eurostat:
                data_yearly[cat][str(y)] += data_trim[str(y)]
    
    times_eurostat = pd.date_range(
        start = datetime(year = years_eurostat[0], month = 1, day = 1),
        end = datetime(year = years_eurostat[-1], month = 1, day = 1),
        freq="YS")

    data_out = {}
    for cat in car_categories: 
        data_out[cat] = {}
        for time in times_eurostat: 
            data_out[cat][time] = data_yearly[cat][str(time.year)]
    
    data_total = {time: sum([data_out[cat][time] for cat in car_categories]) for 
                  time in times_eurostat}
    data_out["Total"] = data_total  
    
    ### for pkw, extend data with more up to date statistik austria data 
    if file == "AT_cars_road_eqs_carpda":
        
        filepath = os.path.join(os.path.dirname(__file__), 
                                "../../data_raw/statistik_austria/Fahrzeuge/kfz-bestand_2024.xlsx")
        data_before = pd.read_excel(filepath, decimal = ",", skiprows = 1, sheet_name = "tab_2", skipfooter = 1)
        data_before = data_before.replace("-", 0).infer_objects(copy=False)
        years_before = [int(1995+i) for i in range(2013-1995)]
        data_out_2 = {cat: {} for cat in data_out}
        data_years = data_before["Jahr1"].astype(int)
        for year in years_before: 
            time = datetime(year = year, month = 1, day = 1)
            data_out_2["Total"][time] = float(data_before["Pkw"][data_years==year].iloc[0])
            data_out_2["Diesel"][time] = float(data_before["Diesel"][data_years==year].iloc[0])
            data_out_2["Gasoline"][time] = float(data_before["Benzin2"][data_years==year].iloc[0])
            data_out_2["Electric"][time] =  float(data_before["Elektro"][data_years==year].iloc[0])
            data_out_2["Other"][time] =  float(data_before["Sonstige Pkw3"][data_years==year].iloc[0])
            data_out_2["Hybrid plugin"][time] = 0 
            data_out_2["Hybrid"][time] = 0
        for time_i in data_out["Total"]: 
            for cat in data_out: 
                data_out_2[cat][time_i] = data_out[cat][time_i]
        
        data_out = data_out_2 
        
        ### get newest monthly data 
        this_year = datetime.today().year
        
        ### in case this year -1 is not present in eurostat 
        if years_eurostat[-1] < this_year-1: 
            # data_out = extend_car_registr(data_out, filepath, this_year-1, skiprows = 2, sheet_name = "tab_1")            
            filepath = os.path.join(os.path.dirname(__file__), 
                                    "../../data_raw/statistik_austria/Fahrzeuge/BestandFahrzeuge%s%iVorlaeufigeDaten.xlsx" %("Dezember", this_year-1))
            data_out = extend_car_registr(data_out, filepath, this_year-1, skiprows = 1,
                                          tot = "Pkw insgesamt", sheet_name = "Pkw")
        
        ### extend with  this-year's monthly data 
        file_found = False 
        for month in reversed(months):   
            filepath = os.path.join(os.path.dirname(__file__), 
                                    "../../data_raw/statistik_austria/Fahrzeuge/BestandFahrzeuge%s%iVorlaeufigeDaten.xlsx" %(month, this_year))
            if os.path.exists(filepath) and not file_found:
                file_found = True 
                month_found = months[month] 
                data_out = extend_car_registr(data_out, filepath, this_year, skiprows = 1,
                                              tot = "Pkw insgesamt", sheet_name = "Pkw_nach_Kraftstoff")
            
        if not file_found: 
            this_year -=1 
            month_found = 12
            
        return data_out, month_found, this_year 
    
    return data_out 
    
 



def filter_uba_emissions(): 
    data_raw = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                              "../../data_raw/umweltbundesamt/Treibhausgas-Emissionen und Zielpfade.xlsx"),
                              decimal = ",", skiprows = 2)
                         
    data_raw = data_raw.fillna(0)
    times = pd.to_datetime(data_raw["Jahr"], format = "%Y")[data_raw["Gesamte THG"] > 0]
    emissions_total = data_raw["Gesamte THG"][data_raw["Gesamte THG"] > 0]

    times_ets = times[data_raw["THG nach KSG"] > 0]
    emissions_esr =  data_raw["THG nach KSG"][data_raw["THG nach KSG"] > 0]
    emissions_ets = emissions_total[data_raw["THG nach KSG"] > 0] - emissions_esr 
    
    data = {"data": {"GHG emissions total": {"x": times,
                                             "y": emissions_total},
                     "GHG emissions Effor Sharing": {"x": times_ets,
                                           "y": emissions_esr},
                     "GHG emissions ETS": {"x": times_ets,
                                           "y": emissions_ets}}
            }
       
    return data 


def filter_uba_sectoral_emisssions(): 
    data_raw = pd.read_excel(os.path.join(os.path.dirname(__file__), 
                              "../../data_raw/umweltbundesamt/Mio. t CO₂-Äquivalent nach Jahr und Sektor.xlsx"),
                              decimal = ",", skiprows = 2)
    
    sectors = {"Transport": "Verkehr (inkl. nationalem Flugverkehr)",
               "Energy & Industry": "Energie & Industrie mit Emissionshandel",
               "Agriculture": "Landwirtschaft",
               "Buildings": "Gebäude",
               "Waste": "Abfallwirtschaft",
               "Fluorinated Gases": "F-Gase"}
    years = [1990+i for i in range(100)]
    for year in years: 
        if year in list(data_raw["Jahr"]): 
            last_year = year 
        
    times = pd.date_range(start = datetime(year=1990, month = 1, day =1),
                          end = datetime(year = last_year, month = 1, day = 1),
                          freq = "YS")
    data = {"data": {}}
    for sector in sectors: 
        data["data"][sector] = {"x": [], "y": []}
        for time in times: 
            data["data"][sector]["y"].append(float(data_raw[
                np.logical_and(data_raw["Sektor"] == sectors[sector],
                               data_raw["Jahr"] == time.year
                               )].iloc[0]["Summe von Mio. t CO₂-Äquivalent"]))
            data["data"][sector]["x"].append(time)
            
    return data 




def filter_eurostat_energy_balance(siecs = {"Natural gas": ["Natural gas"]}, 
                                   bals = ["Final consumption - transport sector - energy use"]): 
    
    years = [1990+i for i in range(100)]
    for year in years: 
        if os.path.exists(os.path.join(os.path.dirname(__file__), 
              "../../data_raw/eurostat/energy_balances/AT_%s_en_bal_TWh.json" %(year))):
                  last_year = year 
                  
    times = pd.date_range(start = datetime(year=1990, month = 1, day =1),
                          end = datetime(year = last_year, month = 1, day = 1),
                          freq = "YS")     

    data = {"data": {}}
    for siec in siecs: 
        data["data"][siec] =  {"x": times, "y": np.zeros(len(times))}
        
    for t in range(len(times)):
        with open(os.path.join(os.path.dirname(__file__), 
              "../../data_raw/eurostat/energy_balances/AT_%s_en_bal_TWh.json" %(times[t].year)), "r") as fp: 
            data_year = json.load(fp)
            
        for bal in bals: 
            for siec in siecs: 
                for sub_siec in siecs[siec]:
                    if np.isnan(data_year[sub_siec][bal]):
                        value = 0 
                    else: 
                        value = data_year[sub_siec][bal]
                        
                    data["data"][siec]["y"][t] += value 
                   
    return data 

if __name__ == "__main__": 
    
    data = filter_eurostat_monnthly_to_yearly()
  