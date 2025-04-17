# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 19:10:31 2024

@author: Bernhard
"""

from source import download_eurostat
from plot import plot_all

### download all eurostat data 
download_eurostat.download_and_save()

### make all plots
plot_all.plot()