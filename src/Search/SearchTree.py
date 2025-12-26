from Objects.Performance import *

import joblib
from scipy.spatial import KDTree

""" Definition of the search tree, pre-processing and functions to find propellers based on performance data. """


class PropellerSearchTree(Performance):

    def __init__(self, pkl_filename="propeller_search_tree.pkl"):
        super().__init__()

        # - file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pkl_path = os.path.join(script_dir, pkl_filename)

        # - after first pre-processing 
        self.engine = joblib.load(pkl_path)
        self.df = self.engine['df']
        self.tree = self.engine['tree']

    def get_prop_id(self, archive_filename):
        # Pattern to capture: [Diameter] x [Pitch] [Type]
        # Example: 27x13E -> Group 1: 27, Group 2: 13.5, Group 3: E
        pattern = r"PER3_((\d+\.?\d*)x(\d+\.?\d*)(.*?))\.dat"

        match = re.search(pattern, archive_filename)
        if match:
            prop_id = match.group(1)   # Full ID
            diameter = match.group(2)  # Number before 'x'
            pitch = match.group(3)     # Number after 'x'
            prop_type = match.group(4) if match.group(4) else "Standard"
            return prop_id, diameter, prop_type
        else: 
            raise ValueError(f"ERROR in finding ID pattern. File error = {archive_filename}")

    def preprocess(self):
        """ Create the .csv file to generate a KDTree 
        
        """

        tree_df = pd.DataFrame()

        # --- Open each prop file and extract the characteristics
        archives = os.listdir(self.perfomance_path)
        for archive in archives:
            perfomance_df = self.read_data(prop=archive)

            # - extract propeller id info
            prop_id, diameter, prop_type = self.get_prop_id(archive)

            # - for each unique RPM, extract the data
            rpms = perfomance_df["RPM"].unique()
            for rpm in rpms:
                df_unique_rpm = perfomance_df.copy()
                df_unique_rpm = df_unique_rpm[df_unique_rpm["RPM"] == rpm] # filter rpm

                prop_metadata = {
                    'prop_id':  prop_id,
                    'prop_type': prop_type, #E, MR, W, ...
                    'filepath': archive,
                    'D (in)': diameter,
                    'RPM': rpm,
                    'maxThrust (N)': df_unique_rpm["Thrust (N)"].max(),
                    'maxPower (W)': df_unique_rpm["PWR (W)"].max(),
                    'maxTorque (Nm)': df_unique_rpm["Torque (N-m)"].max(),
                    'maxFoM': df_unique_rpm["FOM"].max(), #static
                    'max THR/PWR (g/W)': df_unique_rpm["THR/PWR (g/W)"].max(),
                    'J_array': df_unique_rpm["J (Adv_Ratio)"].to_numpy(),
                    'Ct_array': df_unique_rpm["Ct"].to_numpy(),
                    'Cp_array': df_unique_rpm["Cp"].to_numpy(), 
                    'Pe_array': df_unique_rpm["Pe"].to_numpy(), 
                }

                # - Add to pandas dataframe
                index_df = pd.DataFrame([prop_metadata])
                tree_df = pd.concat([tree_df, index_df], ignore_index=True)
        
        # - turn dataframe into csv
        tree_df.to_csv("APC_propeller_metadata.csv")

    def create_KDTree(self):
        """ Create a .pkg job to represent the KDTree """

        df = pd.read_csv("APC_propeller_metadata.csv")

        # - define spatial search parameters
        search_features = [
            'RPM', 'maxThrust (N)', 'maxPower (W)', 
            'maxTorque (Nm)', 'maxFoM', 'max THR/PWR (g/W)'
        ]

        # - create and scale the matrix used to define the search tree
        matrix = df[search_features].to_numpy()
        f_min = matrix.min(axis=0)
        f_max = matrix.max(axis=0)
        f_range = np.where((f_max - f_min) == 0, 1, f_max - f_min) # avoid division by zero if a column is constant
        scaled_matrix = (matrix - f_min) / f_range

        # - create and define the job
        tree = KDTree(scaled_matrix)

        search_engine = {
            'tree': tree,
            'df': df,
            'f_min': f_min,
            'f_range': f_range,
            'features': search_features
        }
        joblib.dump(search_engine, "propeller_search_tree.pkl")

        print('APC propeller search tree created. ')

    def search_by_range(self, constraints, sort_by):
        """
        Search fittest propeller based on the given range input parameters. 
        Outputs a dataframe with the propellers sorted by the given condition.

        INPUTS
            constraints = dictionary containing constraint name and range (min, max)
            sort_by = name of the parameter to sort in descending manner
        ---
        Parameters for input

            Propeller type: 'prop_type' = ['Standard','E','WE','MRF-RH', 'SF', 'MR', 'EP(F2B)', '-4', 'F', 'W', 'EP', 'R-RH', 'E-3', 'N', 'E(F2B)', '-3', 'E(3D)', 'PN', 'WPN', 'EPN', 'E(CD)', '(WCAR-T6)', 'C', '(F1-GT)', 'EP(CD)', 'E-4', 'WSF', 'NN', 'SFR-PC', 'SFR']

            Diameter: 'D (in)' 
            RPM: 'RPM'
            Maximum thrust: 'maxThrust (N)'
            Maximum required power: 'maxPower (W)'
            Maximum torque: 'maxTorque (Nm)'
            Maximum Figure of Merit: 'maxFoM'
            Maximum Thrust/Power: 'max THR/PWR (g/W)'

        """
        query_df = self.df.copy()
        
        for col, val in constraints.items():
            # check if filtering by prop_type (string/categorical)
            if col == 'prop_type':
                if isinstance(val, list):
                    # filter by a list of types: ['E', 'EPN']
                    query_df = query_df[query_df[col].isin(val)]
                else:
                    # filter by a single type string: 'E'
                    query_df = query_df[query_df[col] == val]
            
            # numeric range filtering
            else:
                c_min, c_max = val
                if c_min is not None:
                    query_df = query_df[query_df[col] >= c_min]
                if c_max is not None:
                    query_df = query_df[query_df[col] <= c_max]
                    
        if query_df.empty:
            raise ValueError("No propeller match the constraints.")
        else:
            return query_df.sort_values(by=sort_by, ascending=False)




# === One-time tree initialization

#initialize_tree = PropellerSearchTree()
#initialize_tree.preprocess()
#initialize_tree.create_KDTree()

