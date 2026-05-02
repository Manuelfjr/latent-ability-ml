"""Helpers for turning clustering partitions into CLAIRE-style response matrices."""

from typing import Any, Callable, Dict, List

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm


class TransformPairwise:
    """Build a CLAIRE-style pairwise-agreement matrix from model partitions.

    Parameters
    ----------
    works : int, default=-1
        Number of parallel workers used by :meth:`generate_pij_matrix`.
        The default follows joblib's convention.

    Examples
    --------
    >>> from utils.handson import make_toy_clustering_partitions
    >>> tp = TransformPairwise(works=1)
    >>> matrix = tp.generate_pij_matrix(make_toy_clustering_partitions().T)
    >>> matrix.shape
    (4, 6)
    """

    def __init__(self, works: int = -1):
        """Store the worker configuration used during matrix generation.

        Parameters
        ----------
        works : int, default=-1
            Number of workers passed to joblib's ``Parallel`` backend.

        Returns
        -------
        None
            This initializer stores the configuration on the instance.

        Examples
        --------
        >>> tp = TransformPairwise(works=1)
        >>> tp.works
        1
        """
        self.works = works

    def calculate_pij_value(self, i: int) -> List[float]:
        """Compute one row of CLAIRE-style agreement scores.

        Parameters
        ----------
        i : int
            Row index of the focal model inside ``self.data``.

        Returns
        -------
        list[float]
            Agreement scores for every instance with respect to the focal
            model ``i``.

        Examples
        --------
        >>> from utils.handson import make_toy_clustering_partitions
        >>> tp = TransformPairwise(works=1)
        >>> tp.data = make_toy_clustering_partitions().T.to_numpy()
        >>> len(tp.calculate_pij_value(0))
        6
        """
        item_i = self.data[i]
        tmp = np.delete(self.data, i, axis=0)
        data_boolean = np.array([[k == j for k, j in zip(item_i, model_j)] for model_j in tmp])

        pij_values_row = []
        for idx3, b in enumerate(data_boolean.T):
            tmp2 = np.delete(data_boolean, idx3, axis=1)
            pij_value = np.sum(np.equal(b[:, None], tmp2)) / ((self.data.shape[1] - 1) * (self.data.shape[0] - 1))
            pij_values_row.append(pij_value)
        return pij_values_row

    def generate_pij_matrix(self, data: pd.DataFrame | np.ndarray | None = None) -> pd.DataFrame:
        """Generate the full ``pij`` agreement matrix.

        Parameters
        ----------
        data : pandas.DataFrame or numpy.ndarray or None, default=None
            Model-by-instance partition table. Rows must correspond to models
            and columns to instances.

        Returns
        -------
        pandas.DataFrame
            CLAIRE-style agreement matrix with the same shape as the input
            partition table.

        Examples
        --------
        >>> from utils.handson import make_toy_clustering_partitions
        >>> tp = TransformPairwise(works=1)
        >>> matrix = tp.generate_pij_matrix(make_toy_clustering_partitions().T)
        >>> matrix.shape
        (4, 6)
        """
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

    def combination_models(
        self,
        models: Dict[str, Callable[..., Any]],
        params: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, List[Any]]:
        """Instantiate a grid of models from parameter dictionaries.

        Parameters
        ----------
        models : dict[str, collections.abc.Callable[..., Any]]
            Mapping from model family names to constructors or callables.
        params : dict[str, list[dict[str, Any]]]
            Parameter grid keyed by the same family names used in ``models``.

        Returns
        -------
        dict[str, list[Any]]
            Instantiated model objects grouped by model family.

        Examples
        --------
        >>> tp = TransformPairwise()
        >>> built = tp.combination_models(
        ...     models={'dummy': lambda value=0: {'value': value}},
        ...     params={'dummy': [{'value': 1}, {'value': 2}]},
        ... )
        >>> len(built['dummy'])
        2
        """
        results = {}
        for params_model in params.keys():
            results[params_model] = []
            for arg in params[params_model]:
                results[params_model].append(models[params_model](**arg))
        return (
            results  # [models[params_model](**arg) for params_model in params.keys() for arg in params[params_model]]
        )
