# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 19:00:34 2024

@author: Bernhard
"""

import plotly.io as pio
pio.renderers.default = 'browser'
import plotly.express as px
from datetime import datetime 
import numpy as np 

from plot_single import plot_single_go, plot_with_toggle
from utils.filter import filter_eurostat_monthly
from utils.filter import filter_car_registrations
from utils.filter import filter_eurostat_cars
from utils.filter import filter_railways 
from utils import filter_national_inventory

set2 = px.colors.qualitative.Dark2
colors_cars = {"Electric": set2[0],
          "Hybrid plugin": set2[1],
          "Hybrid": set2[2],
          "Diesel": set2[6],
          "Gasoline": set2[7],
          "Other": set2[5]}


def get_car_vectors(data): 
    data_rel = {"data": {}}
    data_abs = {"data": {}}

    for cat in ["Electric", "Hybrid plugin", "Hybrid", "Diesel", "Gasoline", "Other"]: 
        data_rel["data"][cat] = {"x": list(data[cat].keys()),
                         "y": list(data[cat][time]*100/data["Total"][time] for time in data[cat])}
        data_abs["data"][cat] = {"x": list(data[cat].keys()),
                         "y": list(data[cat][time] for time in data[cat])}
    data_abs["data"]["Total"] = {"x": list(data[cat].keys()),
                     "y": list(data["Total"][time] for time in data[cat])}
            
    return data_rel, data_abs 
    


def plot():
    ### Road petroleum products 
    data_gasoline = filter_eurostat_monthly(name = "oil",
                                      code = "NRG_CB_OILM",
                                  start_year = 2010,
                              options = {"unit": "THS_T",
                                        "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                        "siec": "Motor gasoline [O4652]"},
                              unit = "THS_T", movmean = 12) 
    
    data_diesel = filter_eurostat_monthly(name = "oil",
                                    code = "NRG_CB_OILM",
                                  start_year = 2010,
                              options = {"unit": "THS_T",
                                        "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                        "siec": "Road diesel [O46711]"},
                              unit = "THS_T", movmean = 12)    

    data_plot = {"data": {"Diesel monthly": data_diesel["data"]["Monthly"],
                          "Diesel 12-Month average": data_diesel["data"]["12-Month average"],
                          "Gasoline monthly": data_gasoline["data"]["Monthly"],
                          "Gasoline 12-Month average": data_gasoline["data"]["12-Month average"]
                        },
                  "meta": {"code": "%s | %s" %(data_gasoline["meta"]["code"],
                                              data_diesel["meta"]["code"])
                          }
                  }
    plot_single_go(title = "<b>Road fuels</b>: monthly consumption (incl. biofuels)", 
                    filename = "AT_timeseries_road_fuels_consumption",
                    unit = "Fuel (thousand tons)", 
                    data_plot=data_plot,
                    legend_inside = False)    


    ### Road bio-petroleum products 
    data_gasoline = filter_eurostat_monthly(name = "oil",
                                  start_year = 2010,
                                  code = "NRG_CB_OILM",
                              options = {"unit": "THS_T",
                                        "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                        "siec": "Blended biogasoline [R5210B]"},
                              unit = "THS_T", movmean = 12) 
    
    data_diesel = filter_eurostat_monthly(name = "oil",
                                  start_year = 2010,
                                  code = "NRG_CB_OILM",
                              options = {"unit": "THS_T",
                                        "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                        "siec": "Blended biodiesels [R5220B]"},
                              unit = "THS_T", movmean = 12)    
    
    data_plot = {"data": {"Blended biodiesel monthly": data_diesel["data"]["Monthly"],
                          "Blended biodiesel 12-Month average": data_diesel["data"]["12-Month average"],
                          "Blended biogasoline monthly": data_gasoline["data"]["Monthly"],
                          "Blended biogasoline 12-Month average": data_gasoline["data"]["12-Month average"]
                          },
                "meta": {"code": "%s | %s" %(data_gasoline["meta"]["code"],
                                              data_diesel["meta"]["code"])
                          }
                }
            
    plot_single_go(title = "<b>Road biofuels</b>: monthly consumption (incl. biofuels)", 
                    filename = "AT_timeseries_road_biofuels_consumption",
                    unit = "Fuel (thousand tons)", 
                    data_plot=data_plot,
                    legend_inside = False)   
    
    ### Aviation fuel 
    data_oil = filter_eurostat_monthly(name = "oil",
                                  code = "NRG_CB_OILM",
                                  start_year = 2010,
                              options = {"unit": "THS_T",
                                        "nrg_bal": "Gross inland deliveries - observed [GID_OBS]",
                                        "siec": "Kerosene-type jet fuel [O4661]"},
                              unit = "THS_T", movmean = 12)

    plot_single_go(title = "<b>Kerosene / Aviation fuel</b>: monthly consumption Austria (incl. biofuels)", 
                    filename = "AT_timeseries_kerosene_consumption",
                    unit = "Fuel (thousand tons)", 
                    data_plot=data_oil)    


    
    ### Car registrations data 
    data = filter_car_registrations()
    data_rel, data_abs = get_car_vectors(data) 
    
    plot_with_toggle(title = "<b>AT new monthly car registrations:</b> fuel type share",
                  filename = "AT_timeseries_share_fuel_new_cars",
                  unit = "Share [%]", 
                  data_plot = data_rel,
                  show_plot = False,
                  colors = list([colors_cars[label] for label in colors_cars]),
                  source_text = "eurostat (road_eqr_carpda) & Statistik Austria",
                  initial_visible = "area",
                  plotmax_fac = 1)
    
    plot_with_toggle(title = "<b>AT new monthly car registrations:</b> fuel type absolute number",
                  filename = "AT_timeseries_number_fuel_new_cars",
                  unit = "Number", 
                  data_plot = data_abs,
                  show_plot = False,
                  colors = list([colors_cars[label] for label in colors_cars]),
                  source_text = "eurostat (road_eqr_carpda) & Statistik Austria",
                  initial_visible = "line")
        
    ### yearly with bars 
    data_yearly_raw = {cat: {} for cat in data_abs["data"]}
    for cat in data_abs["data"]: 
        years = []
        for t in range(len(data_abs["data"][cat]["x"])): 
            date = data_abs["data"][cat]["x"][t]
            if date.year in years: 
                date_save = datetime(year = date.year, month = 1, day = 1)
            else: 
                years.append(date.year) 
                date_save = date 
                data_yearly_raw[cat][date_save] = 0 
            data_yearly_raw[cat][date_save] += data_abs["data"][cat]["y"][t]


    data_yearly_abs = {"data": {cat: {"x": np.array([date for date in data_yearly_raw[cat]]),
                             "y": np.array([data_yearly_raw[cat][date] for date in data_yearly_raw[cat]])}
                       for cat in data_yearly_raw}}  
    
    data_yearly_rel = {"data": {}}
    for cat in data_yearly_abs["data"]: 
        data_yearly_rel["data"][cat] = {"x": data_yearly_abs["data"][cat]["x"],
                                        "y": data_yearly_abs["data"][cat]["y"]*100/data_yearly_abs["data"]["Total"]["y"]}
        
    year_last = data_abs["data"]["Total"]["x"][-1].year
    month_last = data_abs["data"]["Total"]["x"][-1].month
    
    data_yearly_rel["data"].pop("Total")
    data_yearly_abs["data"].pop("Total")
    
    
    plot_with_toggle(title = "<b>AT new yearly car registrations</b>: fuel type share",
                  filename = "AT_timeseries_share_fuel_new_cars_yearly",
                  unit = "Share [%]", 
                  data_plot = data_yearly_rel,
                  show_plot = False,
                  colors = list([colors_cars[label] for label in colors_cars]),
                  source_text = "eurostat (road_eqr_carpda) & Statistik Austria",
                  initial_visible = "bar",
                  info_text = f"Data {year_last} up to {month_last}/{year_last}",
                  legend_inside=False,
                  plotmax_fac = 1)
    
    plot_with_toggle(title = "<b>AT new yearly car registrations</b>: fuel type absolute number",
                  filename = "AT_timeseries_number_fuel_new_cars_yearly",
                  unit = "Number", 
                  data_plot = data_yearly_abs,
                  show_plot = False,
                  colors = list([colors_cars[label] for label in colors_cars]),
                  source_text = "eurostat (road_eqr_carpda) & Statistik Austria",
                  initial_visible = "bar",
                  info_text = f"Data {year_last} up to {month_last}/{year_last}",
                  legend_inside = False)   

        
    
    
    
    ### Car stock data 
    data, month, this_year = filter_eurostat_cars(file = "AT_cars_road_eqs_carpda")
    data_rel, data_abs = get_car_vectors(data) 

    info_text = ("Data of %i until %i/%i,"
                 " Hybrids of %i indclude also Plugin-Hybrids<br>" 
                 "Others before 2013 include also Hybrids" %(this_year,month,this_year,this_year))

    
    plot_with_toggle(title = "<b>AT registered cars:</b> fuel type share",
                  filename = "AT_timeseries_share_fuel_stock_cars",
                  unit = "Share [%]", 
                  data_plot = data_rel,
                  time_res = "yearly",
                  show_plot = False,
                  legend_inside = False,
                  colors = list([colors_cars[label] for label in colors_cars]),
                  source_text = "eurostat (road_eqs_carpda) and Statistik Austria",
                  info_text = info_text,
                  initial_visible = "bar",
                  plotmax_fac = 1)
        
    plot_with_toggle(title = "<b>AT registered cars:</b> fuel type absolute number",
                  filename = "AT_timeseries_number_fuel_stock_cars",
                  unit = "Number", 
                  data_plot = data_abs,
                  time_res = "yearly",
                  show_plot = False,
                  legend_inside = False,
                  colors = list([colors_cars[label] for label in colors_cars]),
                  source_text = "eurostat (road_eqs_carpda) and Statistik Austria",
                  info_text = info_text, 
                  initial_visible = "bar")
    
    
    ### Lorries registrations data 
    data = filter_eurostat_cars(file = "AT_lorries_road_eqr_lormot",
                                options = {"vehicle": "VG_LE3P5"})
    data_rel, data_abs = get_car_vectors(data) 
    
    plot_with_toggle(title = "<b>AT new lorry (≤3.5t) registrations:</b> fuel type share",
              filename = "AT_timeseries_share_fuel_new_lorries_le3p5",
              unit = "Share [%]", 
              data_plot = data_rel,
              time_res = "yearly",
              show_plot = False,
              colors = list([colors_cars[label] for label in colors_cars]),
              source_text = "eurostat (road_eqr_lormot)",
              initial_visible = "bar",
              plotmax_fac = 1)
    
    plot_with_toggle(title = "<b>AT new lorry (≤3.5t) registrations:</b> fuel type absolute number",
              filename = "AT_timeseries_number_fuel_new_lorries_le3p5",
              unit = "Number", 
              data_plot = data_abs,
              time_res = "yearly",
              show_plot = False,
              colors = list([colors_cars[label] for label in colors_cars]),
              source_text = "eurostat (road_eqr_lormot)",
              initial_visible = "bar")   
    

    data = filter_eurostat_cars(file = "AT_lorries_road_eqr_lormot",
                                options = {"vehicle": "LOR_GT3P5"})
    data_rel, data_abs = get_car_vectors(data) 
    
    plot_with_toggle(title = "<b>AT new lorry (>3.5t) registrations:</b> fuel type share",
              filename = "AT_timeseries_share_fuel_new_lorries_gt3p5",
              unit = "Share [%]", 
              data_plot = data_rel,
              time_res = "yearly",
              show_plot = False,
              colors = list([colors_cars[label] for label in colors_cars]),
              source_text = "eurostat (road_eqr_lormot)",
              initial_visible = "bar",
              plotmax_fac = 1)
    
    plot_with_toggle(title = "<b>AT new lorry (>3.5t) registrations:</b> fuel type absolute number",
              filename = "AT_timeseries_number_fuel_new_lorries_gt3p5",
              unit = "Number", 
              data_plot = data_abs,
              time_res = "yearly",
              show_plot = False,
              colors = list([colors_cars[label] for label in colors_cars]),
              source_text = "eurostat (road_eqr_lormot)",
              initial_visible = "bar")   
    

    ### railway network 
    data_abs, data_rel = filter_railways()
    
    plot_with_toggle(title = "<b>AT rail track lengths</b>: absolute length",
              filename = "AT_timeseries_rail_tracks_abs",
              unit = "Length (km)", 
              data_plot = data_abs,
              time_res = "yearly",
              show_plot = False,
              source_text = "eurostat (rail_if_line_tr) & Statistik Austria",
              initial_visible = "line")   
    
    plot_with_toggle(title = "<b>AT rail track lengths</b>: shares electrified/non-electrified",
              filename = "AT_timeseries_rail_tracks_rel",
              unit = "Share (%)", 
              data_plot = data_rel,
              time_res = "yearly",
              show_plot = False,
              source_text = "eurostat (rail_if_line_tr) & Statistik Austria",
              initial_visible= "bar",
              plotmax_fac = 1)  
    

    
if __name__ == "__main__": 
    print("Plotting ...")
    plot()
    