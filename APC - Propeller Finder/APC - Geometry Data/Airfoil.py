
from airfoils import Airfoil as foil
import numpy as np
import matplotlib.pyplot as plt

class airfoil_section():

    """
    assumes its NACA4
    r = relative radial position along the blade
    beta = twist angle

    """

    def __init__(self, NACA4, chord, r, beta):
        self.chord = chord
        self.r = r
        self.foil = airfoilNACA4(NACA4, chord)
        self.beta = beta
        self.x, self.y_up, self.y_low = (self.foil).coordinates()
        
        self.twisting_blade()

    def twisting_blade(self):
        beta = np.deg2rad(self.beta)
        x_old = self.x
        camber_line = self.foil.camberLine()

        self.x = self.chord + (x_old - self.chord)*np.cos(beta) + self.y_up*np.sin(beta)
        self.y_up = (self.chord - x_old)*np.sin(beta) + self.y_up*np.cos(beta)
        self.y_low = (self.chord - x_old)*np.sin(beta) - self.y_low*np.cos(beta)
    
    def plot2D(self):
        plt.plot(self.x, self.y_low, "black")
        plt.plot(self.x, self.y_up, "black")
        plt.grid(True)
        plt.axis('equal')
        plt.plot(self.x[15], self.y_low[15], 'x')
        plt.plot(self.x[15], self.y_up[15], 'x')
        plt.plot(self.x[75], self.y_low[75], 'x')
        plt.plot(self.x[75], self.y_up[75], 'x')
        plt.plot(self.x[50], self.y_low[50], 'x')
        plt.plot(self.x[50], self.y_up[50], 'x')
        plt.show()

        
    

class airfoilNACA4():

    def __init__(self, code, chord):
        """
            definition of normalized airfoil
        """
        airfoil = foil.NACA4(code[1] + code[0] + code[2:])
        self.chord = chord
        
        self.xy = airfoil.all_points
        x_norm = np.linspace(0, 1, 100) #100 points
        self.camber_Line = airfoil.camber_line(x_norm)
        y_low_norm = airfoil.y_lower(x_norm)
        y_upper_norm = airfoil.y_upper(x_norm)


        self.x = chord*x_norm
        self.y_low = chord*y_low_norm
        self.y_upper = chord*y_upper_norm
        self.y = np.concatenate((self.y_low, self.y_upper))

    def plot(self):
        plt.plot(self.x, self.y_low, "black")
        plt.plot(self.x, self.y_upper, "black")
        plt.grid(True)
        plt.axis('equal')
        plt.show()
        
    def coordinates(self):
        return self.x, self.y_upper, self.y_low
    
    def camberLine(self):
        return self.camber_Line
        


#lucas = airfoilNACA4('4412', 0.8)
#print(np.shape(lucas.xy))
#lucas.plot()

robertin = airfoil_section('4412', 0.8, 1, 0)
robertin.plot2D()


