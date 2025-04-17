# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 14:04:43 2023

Energy balance: 
        https://ec.europa.eu/eurostat/databrowser/view/NRG_BAL_C/default/table?lang=en&category=nrg.nrg_quant.nrg_quanta.nrg_bal

@author: bernhardthaler
"""

import eurostat 
import json 

code = "NRG_BAL_C"

### siec (those are the different fuels)
siec_dict = eurostat.get_dic(code, "siec", full = False, frmt = "dict")
siec_dict_names = {siec_dict[key]: key for key in siec_dict}
  
### nace_r2 (those are the different sectors)
nrg_bal_sectors = eurostat.get_dic(code, "nrg_bal", full = False, frmt = "dict")

data_dict_raw = {siec: {} for siec in siec_dict_names}
years = [2013 +i for i in range(11)]
years = [2023]
for year in years:
    print("Saving energy balance: %s" %(year))
    
    data_dict = data_dict_raw.copy()
    
    for siec in siec_dict: 
        filter_pars = {"geo": "AT",
                        "siec": siec,
                        "startPeriod": year,
                        "endPeriod": year+1}
        
        data = eurostat.get_data_df(code, filter_pars = filter_pars)
        
        if data is not None: 
            data = data[data["unit"] == "TJ"]
            
            if len(data) > 0: 
                data_vec = []
                for sector in nrg_bal_sectors: 
                    if sector in list(data["nrg_bal"]): 
                        data_dict[siec_dict[siec]][nrg_bal_sectors[sector]] = float(
                            data[str(year)][data["nrg_bal"]==sector].iloc[0])/3600 #TWh
                    else: 
                        data_dict[siec_dict[siec]][nrg_bal_sectors[sector]] = 0

    with open("../data_raw/eurostat/energy_balances/AT_%i_en_bal_TWh.json" %(year), "w") as fp:
        json.dump(data_dict, fp, indent = 6)
           


