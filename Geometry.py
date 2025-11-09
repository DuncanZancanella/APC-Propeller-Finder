import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import pandas as pd
import re
import os
from ClassAPC import *

class Geometry(APC_propeller):

    def __init__(self):
        super().__init__()

    def read_data(self, prop):
        """
        Method for reading APC Geometry files and saving the data.
        Returns an dataframe containing all respective data.

        Inputs:
            prop = propeller name/code. Example "20x10E".
        Outputs:
            dataframe containing all data in file, except:  MOMENT OF INERTIA (SNAIL-IN**2),
                 STATIC MOMENT, ONE SIDE (IN-LB),  SANITY CHECK DATA and NATURAL FREQUENCY DATA
        """

        geo_DataPath = super().searchPropeller(propeller=prop, label='geo')

        if geo_DataPath is False:
            raise ValueError("Error: geometry data path not found.")

        with open(geo_DataPath, 'r') as file:
            lines = file.readlines()

        # ---------
        # Read station matrix data
        # ---------
        data_start = None  # Linha onde começam os dados
        columns_data1 = ["STATION (IN)", "CHORD (IN)", 
                  "PITCH (QUOTED)", "PITCH (LE-TE)", "PITCH (PRATHER)",
                  "SWEEP (IN)", "THICKNESS RATIO", 
                  "TWIST (DEG)", "MAX-THICK (IN)", 
                  "CROSS-SECTION (IN**2)", "ZHIGH (IN)", "CGY (IN)", "CGZ (IN)"]
        data_1 = []          # Lista para armazenar os dados

        # Identificar onde estão os dados
        for i, line in enumerate(lines):
            line = line.strip()

            # Identifica a linha do cabeçalho (ex: começa com "STATION")
            if re.match(r'^STATION', line):
                data_start = i + 3  
                continue

            # Lê os dados numéricos após encontrar o cabeçalho e salva numa lista, que será convertida em um dataframe
            if data_start and i >= data_start:
                if not line:
                    break  # Para leitura ao encontrar linha vazia
                    
                values = line.split()
                #print(f"{i}: {values}")
                if len(values) == len(columns_data1):  # Confere se tem o mesmo número de colunas
                        data_1.append([float(v) for v in values])

        # ---------
        # Read specific data
        # ---------
        columns_generalprop_data = ["RADIUS", "HUBTRA", "BLADES", "TOTAL WEIGHT (Kg)", 
                                    "TOTAL VOLUME (IN**3)", "TOTAL PROJECTED AREA (IN**2)",
                                    "MOMENT OF INERTIA (Kg-M**2)",
                                    "AIRFOIL_1","AIRFOIL_1TR (IN)", 
                                    "AIRFOIL_2TR (IN)", "AIRFOIL_2"]
        generalprop_data = {}
        for line in lines:
            line = line.strip()

            if "RADIUS:" in line:
                match = re.search(r'RADIUS:\s*([\d.]+)', line)
                if match:
                    generalprop_data["RADIUS"] = float(match.group(1))

            elif "HUBTRA:" in line:
                match = re.search(r'HUBTRA:\s*([\d.]+)', line)
                if match:
                    generalprop_data["HUBTRA"] = float(match.group(1))

            elif "BLADES:" in line:
                match = re.search(r'BLADES:\s*(\d+)', line)
                if match:
                    generalprop_data["BLADES"] = float(match.group(1))

            elif "TOTAL WEIGHT (Kg)" in line:
                match = re.search(r'TOTAL WEIGHT \(Kg\)\s*=\s*([-\d.Ee]+)', line)
                if match:
                    generalprop_data["TOTAL WEIGHT (Kg)"] = float(match.group(1))

            elif "TOTAL VOLUME (IN**3)" in line:
                match = re.search(r'TOTAL VOLUME \(IN\*\*3\)\s*=\s*([-\d.Ee]+)', line)
                if match:
                    generalprop_data["TOTAL VOLUME (IN**3)"] = float(match.group(1))

            elif "TOTAL PROJECTED AREA (IN**2)" in line:
                match = re.search(r'TOTAL PROJECTED AREA \(IN\*\*2\)\s*=\s*([-\d.Ee]+)', line)
                if match:
                    generalprop_data["TOTAL PROJECTED AREA (IN**2)"] = float(match.group(1))

            elif "MOMENT OF INERTIA (Kg-M**2)" in line:
                match = re.search(r'MOMENT OF INERTIA \(Kg-M\*\*2\)\s*=\s*([-\d.Ee]+)', line)
                if match:
                    generalprop_data["MOMENT OF INERTIA (Kg-M**2)"] = float(match.group(1))

            elif "AIRFOIL1:" in line:
                match = re.search(r'AIRFOIL1:\s*([-\d.]+),\s*([A-Za-z0-9\-_.]+)', line)
                if match:
                    generalprop_data["AIRFOIL_1TR (IN)"] = float(match.group(1)) #Airfoil 1 transition start start station
                    generalprop_data["AIRFOIL_1"] = match.group(2)

            elif "AIRFOIL2:" in line:
                match = re.search(r'AIRFOIL2:\s*([-\d.]+),\s*([A-Za-z0-9\-_.]+)', line)
                if match:
                    generalprop_data["AIRFOIL_2TR (IN)"] = float(match.group(1)) #Airfoil 2 transition start end station
                    generalprop_data["AIRFOIL_2"] = match.group(2)


        # Se não encontrou os dados, retorna erro
        if not data_1 or not generalprop_data:
            raise ValueError("Error in finding geometry data.")

        # Criar DataFrame
        geo_df = pd.DataFrame(data_1, columns=columns_data1)
        geo_generaldf = pd.DataFrame([generalprop_data])

        return geo_df, geo_generaldf

# Teste

prop = Geometry()
df, df2 = prop.read_data("10x55MR")
#print(prop.searchPropeller("21x12E", label="geo", display=True))
print(df)
print(df2)
df2.to_csv('text.txt', index=False)
# TESTAR hélices indisponíveis "21x12E"