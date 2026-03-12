import plotly.io as pio
pio.renderers.default = 'browser'
from loguru import logger 

from plot import plot_buildings
from plot import plot_fossil_fuels 
from plot import plot_agriculture 
from plot import plot_transport 
from plot import plot_industry 
from plot import plot_emissions_sectors
from plot import plot_energy 
from plot import plot_waste 
from plot import plot_energy_balance 
from plot import plot_food_consumption 
from plot import  plot_car_brands 

def plot_all():
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