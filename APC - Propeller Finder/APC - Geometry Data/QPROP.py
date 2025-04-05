import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
#import aeropy
import pandas as pd

"""
Class QPROP is used to read qprop outputs and generate useful graphs for the team
P vs V vs eta, RPM, 

Para implementar:
    1) P vs RPM
    2) T vs RPM (static thrust)

"""

class QPROP():
    def __init__(self, file_path):
        self.file_path = file_path
        #self.motor = motor_path
        #self.propeller = propeller_path

    def getData(self):
        df = pd.read_csv(self.file_path, 
                         skiprows=16, 
                         delim_whitespace=True, 
                         names=["V","RPM","Dbeta","T","Q(N-m)","Pshaft","Volts","Amps",
                                "effmot","effprop","adv","CT","CP","DV","eff",
                                "Pelec","Pprop","cl_avg","cd_avg"
                        ])
        return df
    
    def PropellerCoefficients(self, Re, H_rho):
        """
        do QPROP, os dados estão fixos para um mesmo RPM
        adv = advance ratio
        Re = Reynolds in which the readings were got
        H_rho = altitude-densidade estimada no cálculo (com base na altura do local, temperatura e pressão) em metros
        """ 
        data = self.getData()

        # Filtrando apenas valores onde a eficiência é maior que zero
        mask = data["effprop"] > 0
        mask = data["effprop"] < 1.0
        adv_filtered = data["adv"][mask]
        CT_filtered = data["CT"][mask]
        CP_filtered = data["CP"][mask]
        eff_filtered = data["effprop"][mask] * 100  # Convertendo eficiência para %

        fig, ax1 = plt.subplots()

        # Primeiro eixo Y (CT e CP)
        ax1.plot(adv_filtered, CT_filtered, label="CT", color="blue")
        ax1.plot(adv_filtered, CP_filtered, label="CP", color="red")
        ax1.set_ylabel("CT / CP")
        ax1.set_xlabel("Razão de avanço (J)")
        ax1.grid(True)
        ax1.legend(loc="upper left")

        # Segundo eixo Y (Eficiência em %)
        ax2 = ax1.twinx()
        ax2.plot(adv_filtered, eff_filtered, label="Eficiência", color="green", linestyle="dashed")
        ax2.set_ylabel("Eficiência (%)")
        ax2.legend(loc="upper right")

        plt.title(f"Desempenho da Hélice em Re = {Re}, altitude-densidade em {H_rho}m")
        plt.show()

    def DynamicThrust(self):
        """
        plot Ct, Cp and propeller eficciency
        """
        data = self.getData()

        plt.plot(data["V"], data["T"])
        plt.ylabel("Tração [N]")
        plt.xlabel("Velocidade do ar [m/s]")
        plt.xlim(0, 35)
        plt.ylim(0, 45)
        plt.title("Tração Dinâmica")
        plt.grid(True)
        plt.show()

    def PowerAnalysis(self):
        """
        Pelec = Power required by the motor to produce shaft power
        Pprop = Power delivered by the propeller to the air
        """

        data = self.getData()

        plt.plot(data["V"], data["Pelec"], label="Potência requerida")
        plt.plot(data["V"], data["Pprop"], label="Potência disponível")
        plt.xlabel("Velocidade do ar [m/s]")
        plt.ylabel("Potência [W]")
        plt.grid(True)
        plt.legend()
        plt.show()

    def PowerThurst(self):

        data = self.getData()

        fig, ax1 = plt.subplots()
        ax1.set_xlim(0, 0.6)
        ax1.set_ylim(0, 800)

        # Primeiro eixo Y (CT e CP)
        ax1.plot(data['adv'], data['Pshaft'], label='Potência', color="red")
        ax1.set_ylabel("Potência [W]")
        ax1.set_xlabel("Razão de avanço (J)")
        ax1.grid(True)
        ax1.legend(loc="upper left")

        # Segundo eixo Y (Eficiência em %)
        ax2 = ax1.twinx()
        ax2.plot(data['adv'], data['T'], color="green", label="Tração", linestyle="dashed")
        ax2.set_ylabel("Tração [N]")
        ax2.legend(loc="upper right")
        ax2.set_ylim(0, 45)

        plt.show()




qpropData_path = r"C:\Users\dunca\Desktop\APC - Propeller data\APC - Geometry Data-20250226T185701Z-001\APC - Geometry Data\qprop20x10E.txt"
prop = QPROP(qpropData_path)
prop.DynamicThrust()
prop.PropellerCoefficients(200000, 1250)
#prop.PowerAnalysis()
prop.PowerThurst()