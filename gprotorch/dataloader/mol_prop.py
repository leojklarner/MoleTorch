"""
Instantiation of the abstract data loader class for
molecular property prediction datasets.
"""

import graphein.molecule as gm
import numpy as np
import pandas as pd
from gprotorch.dataloader import DataLoader
from rdkit.Chem import AllChem, Descriptors, MolFromSmiles


class DataLoaderMP(DataLoader):

    def __init__(self):
        super(DataLoaderMP, self).__init__()
        self.task = "molecular_property_prediction"
        self._features = None
        self._labels = None

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, value):
        self._features = value

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, value):
        self._labels = value

    def validate(self, drop=True):
        """Checks if the features are valid SMILES strings and (potentially)
        drops the entries that are not.

        Args:
            drop: whether to drop invalid entries

        """

        invalid_idx = []

        # iterate through the features
        for i in range(len(self.features)):

            # try to convert each SMILES to an rdkit molecule
            mol = MolFromSmiles(self.features[i])

            # if it does not work, save the index and print its position to the console
            if mol is None:
                invalid_idx.append(i)
                print(f"Invalid SMILES at position {i+1}: {self.features[i]}")

        if drop:
            self.features = np.delete(self.features, invalid_idx).tolist()
            self.labels = np.delete(self.labels, invalid_idx)

    def featurize(self, representation, bond_radius=3, nBits=2048, graphein_config=None):
        """Transforms SMILES into the specified molecular representation.

        Args:
            representation: the desired molecular representation, one of [fingerprints, fragments, fragprints]
            bond_radius: int giving the bond radius for Morgan fingerprints. Default is 3
            nBits: int giving the bit vector length for Morgan fingerprints. Default is 2048
            

        """

        # auxiliary function to calculate the fingerprint representation of a molecule
        def fingerprints():

            rdkit_mols = [MolFromSmiles(smiles) for smiles in self.features]
            fps = [AllChem.GetMorganFingerprintAsBitVect(mol, bond_radius, nBits=nBits) for mol in rdkit_mols]

            return np.asarray(fps)

        # auxiliary function to calculate the fragment representation of a molecule
        def fragments():

            # descList[115:] contains fragment-based features only
            # (https://www.rdkit.org/docs/source/rdkit.Chem.Fragments.html)
            # Update: in the new RDKit version the indices are [124:]
            fragments = {d[0]: d[1] for d in Descriptors.descList[124:]}
            frags = np.zeros((len(self.features), len(fragments)))
            for i in range(len(self.features)):
                mol = MolFromSmiles(self.features[i])
                try:
                    features = [fragments[d](mol) for d in fragments]
                except:
                    raise Exception(f'molecule {i}' + ' is not canonicalised')
                frags[i, :] = features

            return frags
        
        def graphs():
                return [gm.construct_graph(smiles=i, config=graphein_config) for i in self.features]

        valid_representations = ["fingerprints", "fragments", "fragprints", "graphs"]

        if representation == "fingerprints":

            self.features = fingerprints()

        elif representation == "fragments":

            self.features = fragments()

        elif representation == "fragprints":

            self.features = np.concatenate((fingerprints(), fragments()), axis=1)
            
        elif representation == "graphs":
            self.features = graphs()

        else:

            raise Exception(f"The specified representation choice {representation} is not a valid option."
                            f"Choose between {valid_representations}.")

    def load_benchmark(self, benchmark, path):
        """Loads features and labels from one of the included benchmark datasets
        and feeds them into the DataLoader.

        Args:
            benchmark: the benchmark dataset to be loaded, one of
            [Photoswitch, ESOL, FreeSolv, Lipophilicity]
            path: the path to the dataset in csv format

        """

        benchmarks = {
            "Photoswitch":      {"features": "SMILES",
                                 "labels": "E isomer pi-pi* wavelength in nm"},
            "ESOL":             {"features": "smiles",
                                 "labels": "measured log solubility in mols per litre"},
            "FreeSolv":         {"features": "smiles",
                                 "labels": "expt"},
            "Lipophilicity":    {"features": "smiles",
                                 "labels": "exp"},
        }

        if benchmark in benchmarks:

            df = pd.read_csv(path)
            # drop nans from the datasets
            nans = df[benchmarks[benchmark]["labels"]].isnull().to_list()
            nan_indices = [nan for nan, x in enumerate(nans) if x]
            self.features = df[benchmarks[benchmark]["features"]].drop(nan_indices).to_list()
            self.labels = df[benchmarks[benchmark]["labels"]].dropna().to_numpy().reshape(-1, 1)

        else:

            raise ValueError(f"The specified benchmark choice ({benchmark}) is not a valid option. "
                            f"Choose one of {list(benchmarks.keys())}.")


if __name__ == '__main__':
    loader = DataLoaderMP()
    loader.load_benchmark("ESOL", "../../data/property_prediction/ESOL.csv")
    print(loader)
