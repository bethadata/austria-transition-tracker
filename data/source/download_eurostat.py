# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 17:10:55 2024

@author: Bernhard
"""

import eurostat 
import pandas as pd 
import os 

def download_and_save(name = "",
                      code = "",
                      start_period = 1990, 
                      options = [],
                      geo = ["AT"],
                      filters = {}):
    print("Downloading data %s ..." %(name))
    
    ### load already present data 
    filepath = "../data_raw/eurostat/%s_%s_%s.xlsx" %(geo[0], name, code)
    if os.path.exists(filepath): 
        df_old = pd.read_excel(filepath)
        times_old = df_old.keys()
    else:
        times_old = []
        
    # print(times)
    
    my_filter_pars = {'startPeriod': start_period, 
                      'geo': geo}
    
    options_dict = {}
    for option in options: 
        specs = eurostat.get_par_values(code, option)
        names = eurostat.get_dic(code, option, frmt = "dict")
        options_dict[option] = {"specs": specs, "names": names}
        my_filter_pars[option] = specs 
        
    for f in filters: 
        my_filter_pars[f] = filters[f]
        
    data = eurostat.get_data_df(code, filter_pars=my_filter_pars)
    
    for option in options_dict:
        for spec in options_dict[option]["specs"]:
            data = data.replace(spec, options_dict[option]["names"][spec].strip() + " ["+spec+"]")
    
    df = pd.DataFrame(data)
    df.to_excel("../data_raw/eurostat/%s_%s_%s.xlsx" %(geo[0], name, code))
    
    times_new = df.keys() 
    for time in times_new: 
        if time not in times_old and sum(df[time].notnull()) > 0:
            print("New data point: %s" %(time))
    
if __name__ == "__main__": 
    
    ### meat production 
    download_and_save(name = "meat", 
                      code = "apro_mt_pheadm", 
                      options = ["meat", "meatitem"])
    
    ## cow milk 
    download_and_save(name = "milk", 
                      code = "apro_mk_colm", 
                      options = ["dairyprod"])    
    
    ## inorganic fertilzers 
    download_and_save(name = "fertilizer", 
                      code = "aei_fm_usefert", 
                      options = [])   
    
    ### gas consumption 
    download_and_save(name = "gas", 
                      code = "NRG_CB_GASM", 
                      options = ['siec', 'nrg_bal'])

    ### coal consumption 
    download_and_save(name = "coal", 
                      code = "NRG_CB_SFFM", 
                      options = ['siec', 'nrg_bal'])    
    
    ### oil consumption 
    download_and_save(name = "oil", 
                      code = "NRG_CB_OILM", 
                      options = ['siec', 'nrg_bal'])    
    
    ### car registrations 
    download_and_save(name = "cars", 
                      code = "road_eqr_carpda", 
                      options = ["mot_nrg"])      
    
    ### stock of cars 
    download_and_save(name = "cars", 
                      code = "road_eqs_carpda", 
                      options = ["mot_nrg"])   

    ### lorry registration 
    download_and_save(name = "lorries", 
                      code = "road_eqr_lormot", 
                      options = ["mot_nrg"])   
    
    
    ### gas energy balance 
    download_and_save(name = "natural_gas_en_bal", 
                      code = "nrg_bal_c",
                      options = ["siec", "nrg_bal"],
                      filters = {"unit": "GWH",
                                  "siec": "G3000"})       
    
    ### oil energy balance 
    download_and_save(name = "oil_en_bal", 
                      code = "nrg_bal_c",
                      options = ["siec", "nrg_bal"],
                      filters = {"unit": "GWH",
                                  "siec": "O4000XBIO"})       

    ### coal energy balance C0000X0350-0370
    download_and_save(name = "coal_en_bal", 
                      code = "nrg_bal_c",
                      options = ["siec", "nrg_bal"],
                      filters = {"unit": "GWH",
                                  "siec": "C0000X0350-0370"})  
    
    
    ### livestock population 
    download_and_save(name = "bovine_population", 
                      code = "apro_mt_lscatl",
                      options = ["animals"],
                      filters = {"month": "M12"})  
    
    download_and_save(name = "pig_population", 
                      code = "apro_mt_lspig",
                      options = ["animals"],
                      filters = {"month": "M12"})      
    
    download_and_save(name = "sheep_population", 
                      code = "apro_mt_lssheep",
                      options = ["animals"],
                      filters = {"month": "M12"})      
    
    download_and_save(name = "goat_population", 
                      code = "apro_mt_lsgoat",
                      options = ["animals"],
                      filters = {"month": "M12"})   

    download_and_save(name = "electricity_fuel_type", 
                      code = "nrg_cb_pem",
                      options = ["siec"])       
    
    ### rail network 
    download_and_save(name = "rail_tracks", 
                      code = "rail_if_line_tr",
                      options = ["tra_infr"]) 
        

     