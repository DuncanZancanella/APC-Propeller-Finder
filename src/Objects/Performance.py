import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import re
import os
from Objects.ClassAPC import *

#from sklearn.linear_model import LinearRegression
#from sklearn.preprocessing import PolynomialFeatures

""" --- METHODS ---
        1) read_apc_perfomance_data: read each rpm and saves in a dataframe

        To implement:
        2) find_StaticThurst_for_Power
        3) findProp_power(perfomancePath, Power, number)
            perfomancePath = folder that contains APC perfomance data ".dat" archives
            Power [W]
            number = number of closest propellers to Power
            This function searches the highest static thrusts for cloesest given Power data
        4) DynamicThrust
            Show v_air x Thurst curve for APC given data
        5) comparePropellers

"""

class Perfomance(APC_propeller): 

    def __init__(self):
        super().__init__()

    def read_data(self, prop):
        """
        Method for reading APC Performance files and saving the data.
        Returns an dataframe containing all respective data from each RPM.
        Inputs:
            prop = propeller name/code. Example "20x10E".
        """
        perf_DataPath = super().searchPropeller(propeller=prop, label='perf')

        if perf_DataPath is None:
            raise ValueError("Error: perfomance data path not found.")

        with open(perf_DataPath, 'r') as file:
            lines = file.readlines()

        data_start = None  # Linha onde começam os dados
        columns = None  # Lista de nomes das colunas
        current_rpm = None  # Valor do RPM atual
        data = []  # Lista para armazenar os dados

        # Identificar onde estão os dados
        for i, line in enumerate(lines):
            line = line.strip()

            # Identifica um novo bloco de RPM
            match = re.search(r'PROP RPM =\s+(\d+)', line)
            if match:
                current_rpm = int(match.group(1))
                data_start = None  # Reseta para encontrar a próxima tabela

            # Identifica a linha do cabeçalho da tabela
            elif re.match(r'\s*V\s+J\s+Pe\s+Ct', line):
                columns = ["V (mph)", "J (Adv_Ratio)", "Pe", "Ct", "Cp", 
                           "PWR (Hp)", "Torque (In-Lbf)", "Thrust (Lbf)", 
                           "PWR (W)", "Torque (N-m)", "Thrust (N)", 
                           "THR/PWR (g/W)", "Mach", "Reyn", "FOM"]  # Define os nomes das colunas sem "RPM"
                data_start = i + 2  # Pula a linha das unidades

            # Lê os dados numéricos após encontrar o cabeçalho
            elif data_start and i >= data_start:
                values = line.split()
                if len(values) == len(columns):  # Garante que a linha tem o número correto de colunas
                    values = [float(v) for v in values]  # Converte valores para float
                    data.append([current_rpm] + values)  # Adiciona o RPM na frente

        # Se não encontrou os dados, retorna erro
        if not data:
            raise ValueError("Error in finding data.")

        # Criar DataFrame
        perf_df = pd.DataFrame(data, columns=["RPM"] + columns)

        return perf_df


# --- TO UPDATE
    """
    def find_StaticThurst_for_Power(self, dataframe, power):
        """
        #Find max thurst for the given power, in an interval of [power - 50, power + 50]
    """
        # Filtrar os valores dentro da faixa de potência desejada
        #df_filtrado = dataframe[(dataframe["PWR (W)"] > (power - 50)) & (dataframe["PWR (W)"] < (power + 50)) & (dataframe["V (mph)"] == 0)]
        df_filtrado = dataframe[(dataframe["V (mph)"] == 0)]
        df_filtrado = df_filtrado.iloc[(df_filtrado["PWR (W)"] - power).abs().argsort()[:1] ] #acha duas linhas com valores mais proximos de power
        
        #filtra qual é a que tem maior tração estática
        #df_filtrado = df_filtrado.loc[df_filtrado["Thrust (N)"].idxmax()]

        # Se não houver valores na faixa, retornar None
        if df_filtrado.empty:
            return None  

        # Encontrar a linha com maior Thrust (N)
        #max_thrust_row = df_filtrado.loc[df_filtrado["Thrust (N)"].idxmax()]
        
        return df_filtrado
    """
    """
    def findProp_power(self, Power, number, type=None):
        """
        #Finds the propellers, closest to the power given, that have the biggest static thrust.
        #Inputs:
        #    Power = float[W]
        #    number = size of the output list of greatest propellers
    """
        StaticThrust = []
        PowerStatic = []
        archives = os.listdir(self.perfomance_path) #contain all file names
        for archive in archives:
        #    print(archive[5:], "E" in archive[5:]) DANDO ERRADO NO OUTPUT! (até entregando valores errados)
        #     # Garante que "type" seja string, evita erro se None
        #    if isinstance(type, str) and type.lower() in ("e", "eletric"):
                # Verifica se a string tem pelo menos 5 caracteres antes de fatiar
        #        if "E" in archive[5:]:
         #           continue

            perfomance = self.read_data(prop=archive)
            df = self.find_StaticThurst_for_Power(perfomance, Power)

            StaticThrust.append(df["Thrust (N)"].values[0])
            PowerStatic.append(df["PWR (W)"].values[0])

        #print(StaticThrust)

        Biggest = np.argsort(StaticThrust)[-number:][::-1] #5 maiores, do maior pro menos

        print(f" --- Propellers with highest thrust for {Power}W are: --- ")
        print(" --- (from highest to lowest)")
        for i in range(len(Biggest)):
            print(f"{i+1}) {archives[Biggest[i]]} \t Power: {PowerStatic[Biggest[i]]}W Thrust: {StaticThrust[Biggest[i]]}N")

        return Biggest #return position in archives
    """
    """
    def linreg(self, Vair, Thrust):
        # Converte para arrays NumPy e garante que as dimensões estejam corretas
        Vair = np.array(Vair).reshape(-1, 1)
        Thrust = np.array(Thrust).reshape(-1, 1)

        # Cria os termos polinomiais
        poly = PolynomialFeatures(degree=3)
        Vair_poly = poly.fit_transform(Vair)

        # Ajusta a regressão linear
        lin = LinearRegression()
        lin.fit(Vair_poly, Thrust)
        
        # Retorna os coeficientes do polinômio de terceiro grau
        a, b, c = lin.coef_[0][3], lin.coef_[0][2], lin.coef_[0][1]
        d = lin.intercept_[0]

        return a, b, c, d

    def polinomio_3oGrau(self, a, b, c, d, v):
        return a*np.power(v, 3) + b*np.power(v, 2) + c*v + d
    """
    



