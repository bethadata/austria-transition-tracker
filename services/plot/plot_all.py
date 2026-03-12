# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 12:02:41 2024

@author: Bernhard
"""
    
import plotly.io as pio
pio.renderers.default = 'browser'

from . import plot_buildings
from . import plot_fossil_fuels 
from . import plot_agriculture 
from . import plot_transport 
from . import plot_industry 
from . import plot_emissions_sectors
from . import plot_energy 
from . import plot_waste 
from . import plot_energy_balance 
from . import plot_food_consumption 
from . import  plot_car_brands 

def plot_all():
    print("Plotting ... ")
    plot_buildings.plot()
    plot_fossil_fuels.extrapolate_fossil_fuels(plot = False)
    plot_fossil_fuels.extrapolate_emissions(plot = False)
    plot_fossil_fuels.plot_emissions_fuels()
    plot_fossil_fuels.plot_ng_separation()
    plot_agriculture.plot()
    plot_transport.plot()
    plot_industry.plot()
    plot_waste.plot()
    plot_emissions_sectors.plot()
    plot_energy.plot()
    plot_energy_balance.plot()
    plot_food_consumption.plot()
    # plot_car_brands.plot()
    
    
if __name__ == "__main__": 
    plot_all()