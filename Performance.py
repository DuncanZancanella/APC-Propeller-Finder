import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import pandas as pd
import re
import os
from ClassAPC import *

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

""" METHOD FOR SEARCHING PROPELLER
1) ReadFile for each rpm and find the maximum power, < max_power, and save RPM and Thrust data
2) do the above process and compare each data to find maximum thrust
"""
""" --- METHODS ---
        1) read_apc_perfomance_data: le cada rpm e salva num dataframe
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

    def find_StaticThurst_for_Power(self, dataframe, power):
        """
        Find max thurst for the given power, in an interval of [power - 50, power + 50]
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

    def findProp_power(self, Power, number, type=None):
        """
        Finds the propellers, closest to the power given, that have the biggest static thrust.
        Inputs:
            Power = float[W]
            number = size of the output list of greatest propellers
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

    def DynamicThrust(self, propPath, Power, density):
        """
        NECESSARIO ATUALIZAR
        """
        density_seaLevel = 1.225

        df_performance = Perfomance.read_data(propPath, prop=None)
        df_closestPower = Perfomance.find_StaticThurst_for_Power(df_performance, Power)

        RPM = df_closestPower["RPM"].iloc[0]
        
        df_interestData = df_performance[(df_performance["RPM"] == RPM)]

        V_air = df_interestData["V (mph)"]*0.44704
        T = df_interestData["Thrust (N)"]* (density/density_seaLevel)

        # Regressão polinomial
        a, b, c, d = Perfomance.linreg(V_air, T)
        v1 = np.linspace(0, 30, 100)
        T1 = Perfomance.polinomio_3oGrau(a, b, c, d, v1)
        plt.plot(v1, T1, label="Regressão", color="black")

        plt.plot(V_air, T, "x", label="Dados fornecidos pela APC")
        plt.title(f"Tração dinâmica para RPM = {RPM}")
        plt.xlabel("Velocidade do ar [m/s]")
        plt.ylabel("Tração [N]")
        plt.ylim(0, 50)
        plt.xlim(0, 30)
        plt.grid(True)
        plt.legend()
        plt.show()

        #print(df_interestData)

    def get_perfomance(self, prop, RPM, plot=True):
        """ 
        Returns propeller's Figure of Merit (FoM), Ct and Cp for a given RPM (if available in database).
        Inputs:
            prop = propeller code
            RPM
            plot = True/False
        """
        pass

    def comparePropellers(self, propPath1, propPath2, Power, density):
        density_seaLevel = 1.225

        df_performance1 = Perfomance.read_apc_performance_data(propPath1)
        df_closestPower1 = Perfomance.find_StaticThurst_for_Power(df_performance1, Power)
        RPM1 = df_closestPower1["RPM"].iloc[0]
        df_interestData1 = df_performance1[(df_performance1["RPM"] == RPM1)]
        V_air = df_interestData1["V (mph)"]*0.44704
        T = df_interestData1["Thrust (N)"]* (density/density_seaLevel)

        df_performance2 = Perfomance.read_apc_performance_data(propPath2)
        df_closestPower2 = Perfomance.find_StaticThurst_for_Power(df_performance2, 600)
        RPM2 = df_closestPower2["RPM"].iloc[0]
        df_interestData2 = df_performance2[(df_performance2["RPM"] == RPM2)]
        V_air2 = df_interestData2["V (mph)"]*0.44704
        T2 = df_interestData2["Thrust (N)"]* (density/density_seaLevel)



        plt.plot(V_air, T, "x", label="Prop 1")
        plt.plot(V_air2, T2, "x", label="Prop 2")
        plt.xlabel("Velocidade do ar [m/s]")
        plt.ylabel("Tração [N]")
        plt.ylim(0, 50)
        plt.xlim(0, 30)
        plt.grid(True)
        plt.legend()
        plt.show()



prop = Perfomance()
df = prop.read_data("20x10E")
df.to_excel('perftest.xlsx')
print(df)
#prop.findProp_power(Power=600, number=10, type="E")


