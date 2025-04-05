#Chord and Twist distribution plotter for APC Propellers

import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path

#propeller = "18x55MRP"
#geometry = np.loadtxt(propeller + ".txt")

def getPropeller(propeller_name):
    propeller = propeller_name.replace(".", "")
    geometry = np.loadtxt(propeller + "")
    return geometry

def getChord(geometry_data):
    r = geometry_data[:,0]
    R = max(r)

    plt.xlabel("r/R")
    plt.ylabel("c/R")

    #plt.title(f"APC Propeler: {propeller}")
    chord_distribution = geometry_data[:,1]
    plt.plot(r/R, chord_distribution/R, "o", color="black")
    plt.grid(True)
    plt.title("Distribuição de corda")
    plt.show()

    return chord_distribution

def getTwist(geometry_data):
    r = geometry_data[:,0]
    R = max(r)
    plt.xlabel("r/R")
    plt.ylabel("Degrees")
    #plt.title(f"APC Propeler: {propeller}")

    twist_distribution = geometry_data[:,7]
    plt.plot(r/R, twist_distribution, "o", color="black")
    plt.grid(True)
    plt.show()

    return twist_distribution

def readAPC_file(arquivo):
    with open(arquivo, 'r') as f:
        linhas = f.readlines()
    
    dados_tabulares = []
    
    for linha in linhas:
        try:
            # Tentamos converter a linha para float
            # Se a linha contiver números, ela será dividida e armazenada
            valores = list(map(float, linha.split()))
            # Só adicionamos a linha se ela contém 13 colunas (padrão de colunas do exemplo)
            if len(valores) == 13:
                dados_tabulares.append(valores)
        except ValueError:
            # Ignora a linha se não puder ser convertida para números (ou seja, não é dado tabular)
            continue
    
    # Converte a lista de listas para um array numpy
    return np.array(dados_tabulares)



def searchPropeller(propeller_code, directory):
    directory = Path(directory)
    #verifies if propeller enter code is correct
    if "-PERF.PE0" in propeller_code:

        # Procura pelo arquivo nos subdiretórios
        arquivos_encontrados = list(directory.rglob(propeller_code))

        if arquivos_encontrados:
            print(f"Propeller '{propeller_code}' found in: {arquivos_encontrados[0]}")
            return propeller_code
        else:
            print(f"Propeller '{propeller_code}' not found. Verify propeller code.s")
            return False

    else:
        new_code = propeller_code + "-PERF.PE0"
        return searchPropeller(new_code, directory)

        
diretorio = r"C:\Users\dunca\Desktop\UFSC\APC - Propeller data\APC - Propeller finder\APC - Geometry Data\PE0-FILES_WEB"

apc = "20x10" ##Nao usar ponto no dado de passo!!
propeller_code = searchPropeller(apc, diretorio)
print(propeller_code)

caminho = diretorio + "\\" + propeller_code
print(caminho)
helice = readAPC_file(caminho)
getChord(helice)

#input da helice 10x4.5
#busca na pasta
#pega geometria e faz as paradas

#orientação a objetos
#   classe APC_propeller
#       