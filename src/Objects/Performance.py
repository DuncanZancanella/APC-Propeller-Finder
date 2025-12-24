import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import pandas as pd
import re
import os
from Objects.ClassAPC import *
import scienceplots
from scipy.interpolate import RegularGridInterpolator

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

class Performance(APC_propeller): 

    def __init__(self):
        super().__init__()

    def read_data(self, prop):
        """
        Method for reading APC Performance files and saving the data.
        Returns an dataframe containing all respective data from each RPM.

        INPUTS:
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
    
    def plot(self, df_prop, RPM:int, key:int = 1):
        """
        Plot Ct, Cp and efficiency for a given RPM.

        INPUTS:
            df_prop = propeller dataframe based on read_data method
            RPM
            key = type of plot.

            key == 1: plot Ct, Cp and propeller efficiency
            key == 2: plot dynamic thrust for a given RPM
            key == 3: plot dynamic thrust for all RPM
        """

        df_rpm = df_prop[df_prop["RPM"] == RPM]
        if df_rpm.empty:
            raise ValueError("RPM not present in data range. \n " \
            f"The available RPM for this prop are: {df_prop["RPM"].unique()}")

        plt.style.use(['science', 'grid', 'notebook'])

        if key == 1:
            fig, ax1 = plt.subplots()
            # Left axis: Ct and Cp
            ax1.plot(df_rpm["J (Adv_Ratio)"], df_rpm["Ct"], label='Ct')
            ax1.plot(df_rpm["J (Adv_Ratio)"], df_rpm["Cp"], label='Cp')
            ax1.set_xlabel("J (Advance Ratio)")
            ax1.set_ylabel("Ct , Cp")
            ax1.legend(loc="lower left")

            # Right axis: Efficiency
            ax2 = ax1.twinx()
            ax2.plot(
                df_rpm["J (Adv_Ratio)"],
                100*df_rpm["Pe"],   # efficiency in %
                linestyle="--",
                label="η (%)"
            )
            ax2.set_ylabel("Efficiency (%)")
            # separate legend for right axis
            ax2.legend(loc="upper right")
            plt.title(f"RPM = {RPM}")
            plt.show()
        
        elif key == 2:
            plt.plot(0.44704*df_rpm["V (mph)"], df_rpm["Thrust (N)"])
            plt.xlabel("Velocity [m/s]")
            plt.ylabel("Thrust [N]")
            plt.show()
        
        elif key == 3:
            unique_rpm_values = df_prop["RPM"].unique()
            cmap = cm.plasma
            norm = mcolors.Normalize(
                vmin=unique_rpm_values.min(),
                vmax=unique_rpm_values.max()
            )
            fig, ax = plt.subplots(figsize=(7, 5))

            # --- Plot curves, color-coded by RPM
            for rpm in unique_rpm_values:
                df_rpm_plot = df_prop[df_prop["RPM"] == rpm]
                
                ax.plot(
                    0.44704 * df_rpm_plot["V (mph)"],
                    df_rpm_plot["Thrust (N)"],
                    color=cmap(norm(rpm)),
                    linewidth=2
                )

            ax.set_xlabel("Velocity [m/s]")
            ax.set_ylabel("Thrust [N]")
            ax.grid(True)

            sm = cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])

            cbar = fig.colorbar(sm, ax=ax)
            cbar.set_label("RPM")

            # Layout and show
            fig.tight_layout()
            plt.show()
        else:
            raise ValueError("Invalid key input. Check value.")


    def performance_map(self, df_prop, rpm_min = None, rpm_max = None, eta_range = []):
        """
        Plot propeller performance map.

        INPUTS
            df_prop = propeller dataframe
            rpm_min = minimum RPM value for plot
            rpm_max = maximum RPM value for plot
            eta_range = list of efficiency values to plot iso-lines
        """
    
        plt.style.use(['science', 'grid', 'notebook'])
        
        # --- Pre-processing ---
        df = df_prop.copy()

        # --- RPM range filtering ---
        if rpm_min is not None:
            df = df[df["RPM"] >= rpm_min]
        if rpm_max is not None:
            df = df[df["RPM"] <= rpm_max]
        if df.empty:
            raise ValueError("No data left after RPM filtering.")

        rpm_vals = np.sort(df["RPM"].unique())
        vel = np.linspace(df["V (mph)"].min(),
                        df["V (mph)"].max(), 300)
        
        # --- Regrid Thrust, Power and Efficiency in (RPM, V) space ---
        T = np.zeros((len(rpm_vals), len(vel)))
        P = np.zeros_like(T)
        ETA = np.zeros_like(T)
        for i, rpm in enumerate(rpm_vals):
            s = df[df["RPM"] == rpm].sort_values("V (mph)")
            T[i] = np.interp(vel, s["V (mph)"], s["Thrust (N)"])
            P[i] = np.interp(vel, s["V (mph)"], s["PWR (W)"])
            ETA[i] = np.interp(vel, s["V (mph)"], s["Pe"])

        # --- Interpolators ---
        T_fun = RegularGridInterpolator((rpm_vals, vel), T,
                                        bounds_error=False)
        P_fun = RegularGridInterpolator((rpm_vals, vel), P,
                                        bounds_error=False)
        ETA_fun = RegularGridInterpolator((rpm_vals, vel), ETA,
                                        bounds_error=False)
        
        # --- Dense evaluation grid ---
        RPMg, Vg = np.meshgrid(
            np.linspace(rpm_vals.min(), rpm_vals.max(), 250),
            vel,
            indexing="ij"
        )
        pts = np.c_[RPMg.ravel(), Vg.ravel()]
        Tg = T_fun(pts).reshape(RPMg.shape)
        Pg = P_fun(pts).reshape(RPMg.shape)
        ETAg = ETA_fun(pts).reshape(RPMg.shape)
        
        # --- Plot ---
        fig, ax = plt.subplots(figsize=(14, 8))
        # --- RPM colormap in (T, P) space ---
        cf = ax.contourf(
            Tg, Pg, RPMg,
            levels=60,
            cmap="plasma"
        )

        # --- Constant RPM tendency lines + labels ---
        for rpm in rpm_vals:
            s = df[df["RPM"] == rpm].sort_values("V (mph)")
            x = s["Thrust (N)"].values
            y = s["PWR (W)"].values
            ax.plot(x, y, color="black", lw=1, alpha=0.6)
            # Label near the low-speed point
            ax.text(
                x[0],
                y[0],
                f"{int(rpm)} RPM",
                fontsize=9,
                ha="left",
                va="center",
                color="black",
                clip_on=True
            )

        # --- Iso-efficiency (η) tendency line ---
        for eta in eta_range:
            cs_eta = ax.contour(
                Tg,
                Pg,
                ETAg,
                levels=[eta],
                colors="white",
                linestyles="--",
                linewidths=1.5
            )
            ax.clabel(
                cs_eta,
                fmt=lambda x: rf"$\eta = {x:.2f}$",
                inline=True,
                fontsize=11,
                colors="white"
            )

        # --- Formatting ---
        ax.set_xlabel("Thrust [N]")
        ax.set_ylabel("Required Power [W]")
        ax.grid(True, alpha=0.3)
        cbar = fig.colorbar(cf, ax=ax)
        cbar.set_label("RPM")
        plt.tight_layout()
        plt.show()





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
    



