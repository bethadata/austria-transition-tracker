# -*- coding: utf-8 -*-
"""
Created on Sun May  5 11:30:59 2024

@author: Bernhard
"""

import os 
import pandas as pd 
import numpy as np
from datetime import datetime 


data_before =  pd.read_excel(os.path.join(os.path.dirname(__file__), 
                          "../../data_raw/statistik_austria/kfz-bestand_2023.xlsx"),
                          decimal = ",", skiprows = 1, sheet_name = "tab_2", skipfooter=1)

# number = data_2023["Unnamed: 1"]
# column = data_2023["Personenkraftwagen Kl. M1"]
# number = np.array(data_2023.iloc[:, [1]])
# column = np.array(data_2023.iloc[:, [0]])
