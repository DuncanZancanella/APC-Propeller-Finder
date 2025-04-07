
#import aeropy.aerodynamics
#import aeropy.airfoils
#import aeropy.airfoils.analysis
#import aeropy.airfoils.shapes
import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
#import aeropy
import pandas as pd

""" --- Summary of methods 
    1) searchPropeller: verifica se a dada hélice está presente no caminho dado
    2) readAPC_file: pega as 13 colunas principais  STATION, CHORD, PITCH (QUOTED), PITCH (LE-TE), PITCH (PRATHER), SWEEP, THICKNESS, TWIST, MAX-THICK, CROSS-SECTION ZHIGH, CGY, CGZ    
    3) getChord ---> generalizar funções 3 e 4 para 2
    4) getTwist

    A implementar:
        1) metodo para desligar print (**kwargs print=Boolean)
        2) poder ter ponto no codigo da helice. ex: 18x4.5
        3) executar Xfoil e Qprop para obter Ct e Cq (criacao de uma classe generica propeller e subclasse APC) 


"""

class APC_propeller():
    """
    APC Propellers database, containing the geometry and perfomance. 
    Implements methods for searching propellers.
    """
    
    #construtor
    def __init__(self):
        self.geometry_path = r"C:\Users\dunca\Desktop\UFSC\APC - Propeller data\APC - Propeller Finder\APC - Geometry Data\PE0-FILES_WEB"
        self.perfomance_path = r"C:\Users\dunca\Desktop\UFSC\APC - Propeller data\APC - Propeller Finder\APC - Perfomance Data\PERFILES2"
        self.propeller = None # Propeller name
        self.code = None
        self.directory = None

    def searchPropeller(self, propeller, label, display=False):
        """
        Enters the code of a certain propeller defined by "Diameter x Pitch(Type)" (in inches).
        Types of propellers:
            E = Eletric
            EP = Eletric Pusher
            EC = Eletric Carbon
            R = Reversible ESC (LH or RH)
            P = Sport Pusher
            SF = Slow Flyer
            WSF = Wide Slow Flyer
            N = Narrow
            MR = Multi Rotor
            W = Wide
        Inputs:
            propeller = prop code/name. Example "20x10E", "9x10".
            label = "geo" for searching in geometry data, "perf for perfomance data
        """
        self.code = str(propeller)

        if label == "geo":
            geometry_path = Path(self.geometry_path)
            #verifies if propeller enter code is correct
            if "-PERF.PE0" in self.code:

                # Procura pelo arquivo nos subdiretórios
                arquivos_encontrados = list(geometry_path.rglob(self.code))

                if arquivos_encontrados:
                    if display:
                        print(f"Propeller '{self.code}' found in: {arquivos_encontrados[0]}")
                    return arquivos_encontrados[0]
                else:
                    if display:
                        print(f"Propeller '{self.code}' not found. Verify propeller code.")
                    return False

            else:
                self.code = propeller + "-PERF.PE0" # atualiza input
                propeller = self.code
                return self.searchPropeller(propeller, label, display) #chamada recursiva onde os inputs ja foram atualizados
        
        elif label == "perf":
            perf_path = Path(self.perfomance_path)
            #verifies if propeller enter code is correct
            if "PER3_" in self.code:

                # Procura pelo arquivo nos subdiretórios
                arquivos_encontrados = list(perf_path.rglob(self.code))

                if arquivos_encontrados:
                    if display:
                        print(f"Propeller '{self.code}' found in: {arquivos_encontrados[0]}")
                    return arquivos_encontrados[0]
                else:
                    if display:
                        print(f"Propeller '{self.code}' not found. Verify propeller code.")
                    return False

            else:
                self.code = "PER3_" + propeller + ".dat" # atualiza input
                propeller = self.code
                return self.searchPropeller(propeller, label) #chamada recursiva onde os inputs ja foram atualizados
        else:
            print(f"Invalid label. Verify if it refers to \'geo' or \'perf'." )


    def readAPC_file(self):
        self.code = self.searchPropeller()
        caminho = self.directory + "\\" + self.code

        with open(caminho, 'r') as f:
            linhas = f.readlines()
        
        dados_tabulares = []
        
        for linha in linhas:
            try:
                # Tentamos converter a linha para float
                # Se a linha tiver números, ela será dividida e armazenada
                valores = list(map(float, linha.split()))
                # Só adicionamos a linha se ela contém 13 colunas (padrão de colunas do exemplo)
                if len(valores) == 13:
                    dados_tabulares.append(valores)
            except ValueError:
                # Ignora a linha se não puder ser convertida para números (ou seja, não é dado tabular)
                continue
        
        # Converte a lista de listas para um array numpy
        return np.array(dados_tabulares)
    
    def getChord(self):
        geometry_data = self.readAPC_file()
        r = geometry_data[:,0]
        R = max(r)

        plt.xlabel("r/R")
        plt.ylabel("c/R")

        plt.title(f"APC Propeller: {self.name}")
        chord_distribution = geometry_data[:,1]
        plt.plot(r/R, chord_distribution/R, "o", color="black")
        plt.grid(True)
        plt.show()

        return r, chord_distribution
    
    def getTwist(self):
        geometry_data = self.readAPC_file()
        r = geometry_data[:,0]
        R = max(r)
        plt.xlabel("r/R")
        plt.ylabel("Degrees")
        plt.title(f"APC Propeller: {self.name}")

        twist_distribution = geometry_data[:,7]
        plt.plot(r/R, twist_distribution, "o", color="black")
        plt.grid(True)
        plt.show()

        return r, twist_distribution
    
    
    def getThickness(self):
        geometry_data = self.readAPC_file()
        r = geometry_data[:,0]
        R = max(r)
        plt.xlabel("r/R")
        plt.ylabel("Thickness distribution [in]")
        plt.title(f"APC Propeller: {self.name}")

        thickness_distribution = geometry_data[:,8]
        plt.plot(r/R, thickness_distribution, "o", color="black")
        plt.grid(True)
        plt.show()

        return r, thickness_distribution #[IN]

    def plotPropeller(self):
        geometry_data = self.readAPC_file()
        r = geometry_data[:,0]
        R = max(r)

    def getData(self): ##FUNÇÃO INCORRETA: alterar para ler até determinada parte do arquivo, e não tudo
        """
        USADO PARA GEOMETRY DATA
        """
        self.code = self.searchPropeller()
        caminho = self.directory + "\\" + self.code

        with open(caminho, "r") as f:
            linhas = f.readlines()

        # Identificar a linha onde começam os dados numéricos
        for i, linha in enumerate(linhas):
            if linha.strip().startswith("STATION"):
                linha_inicial = i + 1  # A linha seguinte contém os dados
                break

        # Nomes das colunas conforme a estrutura do arquivo
        colunas = [
            "STATION (IN)", "CHORD (IN)", "PITCH (QUOTED)", "PITCH (LE-TE)", "PITCH (PRATHER)",
            "SWEEP (IN)", "THICKNESS RATIO", "TWIST (DEG)", "MAX-THICK (IN)",
            "CROSS-SECTION (IN**2)", "ZHIGH (IN)", "CGY (IN)", "CGZ (IN)"
        ]

        # Ler os dados usando pandas
        df = pd.read_csv(
            caminho, 
            skiprows=linha_inicial,  # Pula as linhas antes da tabela de dados
            delim_whitespace=True,  # Usa espaços como delimitadores
            names=colunas  # Define os nomes das colunas manualmente
        )

        # Exibir as primeiras linhas do DataFrame
        return df
    
    def QPROP_outputfile(self):
        r, chord = self.getChord()
        r, beta = self.getTwist()

        dados = np.column_stack((r, chord, beta))
        np.savetxt(f"APC{self.code}.txt", dados, fmt="%.3f", delimiter="    ", header="#r \t chord \t twist", comments='')
        return True



prop = APC_propeller()
geo_data = prop.searchPropeller(propeller="20x10E", label="perf")