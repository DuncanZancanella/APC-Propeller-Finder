import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
#import aeropy
import pandas as pd

class XFOIL():

    def __init__(self, file_path):
        self.file_path = file_path

    def getData(self):
        df = pd.read_csv(self.file_path, 
                         skiprows=11, 
                         delim_whitespace=True, 
                         names=["alpha", "CL", "CD", "CDp", "CM", "Top_Xtr", "Bot_Xtr"
                        ])
        return df
    
    def qprop_liftCoefficients(self, plot):
        df = self.getData()

        df = df[(df["alpha"] > -5) & (df["alpha"] < 10)] ##regressão limitada entre (-5, 10)
        alpha = df["alpha"]
        CL = df["CL"]
        Cl_max = max(CL)
        Cl_min = min(CL) 

        df_zero = df[df['alpha'] == 0] # pega a linha exatamente em zero
        Cl_zero = df_zero['CL'].values[0] #Cl_zero = real value got from XFOIL (only possible if the calculated xfoil has exactly alpha zero)

        Cl_a, Cl_0 = np.polyfit(alpha, CL, 1) # Cl(alpha) = Cl_a*(alpha) + Cl_0 ; where Cl_a is the slope
        print(f"Cl_a: {Cl_a*180/np.pi} [1/rad], Cl_0: {Cl_zero}")

        if plot:
            plt.plot(alpha, CL, label="xfoil")
            plt.plot(alpha, Cl_zero + alpha*Cl_a, label='regression')
            plt.xlabel("Alpha in degrees")
            plt.ylabel("Cl")
            plt.legend()
            plt.grid(True)
            plt.show()
        
        # Cl_0 is the interpolated value
        return Cl_a*(180/np.pi), Cl_zero, Cl_min, Cl_max #Cl-a is in degrees^(-1). For QPROP, CL_a must be in rad^(-1)
    
    """ CD2u and CD2l should be manually adjusted to find the fitted qprop curve """
    def qprop_dragCoefficients(self, plot, CD2u, CD2l):
        df = self.getData()
        df = df[(df["alpha"] > -5) & (df["alpha"] < 10)] ##regressão limitada entre (-5, 10)
        alpha = df['alpha']
        Cd = df["CD"]
        Cl = df['CL']

        df_zero = df[df['alpha'] == 0] # pega a linha exatamente em zero
        alpha_0 = df_zero['alpha']
        Cl_0 =  df_zero['CL'].values[0]
        Cd_0 = df_zero['CD'].values[0]


        """ find lift coefficient for minimun drag (CLCD0) """
        # Find the index of the row where CD is minimum
        min_cd_index = df["CD"].idxmin()

        # Extract the row with the minimum CD
        min_cd_row = df.loc[min_cd_index]

        # Create a new DataFrame with this row
        min_cd_df = pd.DataFrame([min_cd_row])
        CLCD0 = min_cd_df["CL"].values[0]


        """ get lower CdCl curve """
        df_lower = df[df['CL'] < CLCD0]
        alpha_lower = df_lower['alpha']
        Cd_lower = df_lower['CD']
        Cl_lower = df_lower['CL']

        """ get upper CdCl curve """
        df_upper = df[df['CL'] > CLCD0]
        alpha_upper = df_upper['alpha']
        Cd_upper = df_upper['CD']
        Cl_upper = df_upper['CL']


        if plot:
            plt.plot(Cd, Cl, label="original xfoil")
            #plt.plot(Cd_lower+ 0.01, Cl_lower, label="xfoil")
            #plt.plot(cd_fit_lower,cd_fit_lower, label='regression')
            plt.plot((Cd_0 + CD2u*(Cl_upper - CLCD0)**2)*(1)**(-0.5), Cl_upper, label="upper qprop")
            plt.plot((Cd_0 + CD2l*(Cl_lower - CLCD0)**2)*(1)**(-0.5), Cl_lower, label="lower qprop")
            plt.xlabel("Cd")
            plt.ylabel("Cl")
            plt.title("Cl vs Cd")
            plt.legend()
            plt.grid(True)
            plt.show()

        print(f"Cd_0: {Cd_0}, CLCD0: {CLCD0}")
        return Cd_0, CLCD0







#file_path = r"C:\Users\dunca\Desktop\APC - Propeller data\APC - Geometry Data-20250226T185701Z-001\APC - Geometry Data\XFOIL\NACA4412_xfoil.txt"
file_path = r"C:\Users\dunca\Desktop\APC - Propeller data\APC - Geometry Data-20250226T185701Z-001\APC - Geometry Data\XFOIL\NACA4412_Re.txt"

airfoil = XFOIL(file_path)
data = airfoil.getData()
print(airfoil.qprop_liftCoefficients(True))
print(airfoil.qprop_dragCoefficients(True, 0.012, 0.015))