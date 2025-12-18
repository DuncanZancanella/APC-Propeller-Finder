
from pathlib import Path
from abc import ABC, abstractmethod

""" --- Summary of methods 
    1) searchPropeller: verifica se a dada hélice está presente no caminho dado. Retorna o diretório do arquivo.

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
    
    # construtor
    def __init__(self):
        self.geometry_path = r"C:APC - Propeller Finder\APC - Geometry Data\PE0-FILES_WEB"
        self.perfomance_path = r"C:APC - Propeller Finder\APC - Perfomance Data\PERFILES2"
        self.propeller = None # Propeller name
        self.code = None
        self.directory = None

    def searchPropeller(self, propeller, label, verbose=False):
        """
        Enters the code of a certain propeller defined by "Diameter x Pitch(Type)" (in inches).

        Inputs:
            propeller = prop code/name. Example "20x10E", "9x10".
            label = "geo" for searching in geometry data, "perf for perfomance data
        Output:
            Propeller file directory.

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

        """
        self.code = str(propeller)

        if label == "geo":
            geometry_path = Path(self.geometry_path)
            #verifies if propeller enter code is correct
            if "-PERF.PE0" in self.code:

                # Procura pelo arquivo nos subdiretórios
                arquivos_encontrados = list(geometry_path.rglob(self.code))

                if arquivos_encontrados:
                    if verbose:
                        print(f"Propeller '{self.code}' found in: {arquivos_encontrados[0]}")
                    return arquivos_encontrados[0]
                else:
                    raise ValueError(f"Propeller '{self.code}' not found. Verify propeller code.")

            else:
                self.code = propeller + "-PERF.PE0" # atualiza input
                propeller = self.code
                return self.searchPropeller(propeller, label, verbose) #chamada recursiva onde os inputs ja foram atualizados
        
        elif label == "perf":
            perf_path = Path(self.perfomance_path)
            #verifies if propeller enter code is correct
            if "PER3_" in self.code:

                # Procura pelo arquivo nos subdiretórios
                arquivos_encontrados = list(perf_path.rglob(self.code))

                if arquivos_encontrados:
                    if verbose:
                        print(f"Propeller '{self.code}' found in: {arquivos_encontrados[0]}")
                    return arquivos_encontrados[0]
                else:
                    raise ValueError(f"Propeller '{self.code}' not found. Verify propeller code.")

            else:
                self.code = "PER3_" + propeller + ".dat" # atualiza input
                propeller = self.code
                return self.searchPropeller(propeller, label) #chamada recursiva onde os inputs ja foram atualizados
        else:
            raise ValueError(f"Invalid label. Verify if it refers to \'geo' or \'perf'." )

    @abstractmethod
    def read_data(self):
        """ Must be implemented by the subclass. """
        pass

