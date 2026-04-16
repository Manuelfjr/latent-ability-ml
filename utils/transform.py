from typing import Dict, List

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm


class TransformPairwise:
    def __init__(self, works: int = -1):
        self.works = works

    def calculate_pij_value(self, i: int) -> List[float]:
        item_i = self.data[i]
        tmp = np.delete(self.data, i, axis=0)
        data_boolean = np.array([[k == j for k, j in zip(item_i, model_j)] for model_j in tmp])

        pij_values_row = []
        for idx3, b in enumerate(data_boolean.T):
            tmp2 = np.delete(data_boolean, idx3, axis=1)
            pij_value = np.sum(np.equal(b[:, None], tmp2)) / ((self.data.shape[1] - 1) * (self.data.shape[0] - 1))
            pij_values_row.append(pij_value)
        return pij_values_row

    def generate_pij_matrix(self, data: pd.DataFrame = None) -> pd.DataFrame:
        if data is None:
            raise ValueError("`data` must be provided as a pandas DataFrame or numpy ndarray.")

        if isinstance(data, pd.DataFrame):
            self.columns = data.columns
            self.data = data.values
        elif isinstance(data, np.ndarray):
            self.columns = None
            self.data = data
        else:
            raise TypeError("`data` must be a pandas DataFrame or numpy ndarray.")

        num_samples = self.data.shape[0]
        pij_values = Parallel(n_jobs=self.works)(delayed(self.calculate_pij_value)(i) for i in tqdm(range(num_samples)))
        self.transformed_matrix = np.array(pij_values)
        return pd.DataFrame(self.transformed_matrix, columns=self.columns)

    def combination_models(self, models: Dict[str, callable], params: Dict[str, List[Dict[str, any]]]) -> Dict:
        results = {}
        for params_model in params.keys():
            results[params_model] = []
            for arg in params[params_model]:
                results[params_model].append(models[params_model](**arg))
        return (
            results  # [models[params_model](**arg) for params_model in params.keys() for arg in params[params_model]]
        )
