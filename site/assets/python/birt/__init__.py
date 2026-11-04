"""Stand-in for ``birt.Beta3`` when the tutorial runs Python in the browser.

The real package (``pip install birt-gd``) needs TensorFlow, which Pyodide does
not ship. The server and Colab use the real package; this file is only loaded
by the in-browser fallback. Same model and interface, fitted in numpy by
:func:`utils.handson.fit_beta3`.
"""

import numpy as np
import pandas as pd

from utils.handson import fit_beta3


class Beta3:
    """Beta3-IRT fitted by gradient descent (birt-gd, github.com/Manuelfjr/birt-gd).

    Parameters
    ----------
    learning_rate : float, default=1
        Gradient descent step size.
    epochs : int, default=10000
        Maximum number of epochs.
    n_respondents : int, default=20
        Number of models evaluated (columns of the matrix passed to ``fit``).
    n_items : int, default=100
        Number of items (rows of the matrix passed to ``fit``).
    n_inits : int, default=1000
        Initial epochs with discrimination fixed at 1.
    n_workers : int, default=-1
        Number of CPUs to use.
    random_seed : int, default=1
        Seed of the initial values.
    tol : float, default=1e-5
        Convergence tolerance on the loss.

    Attributes
    ----------
    abilities : numpy.ndarray
        Ability of each respondent, in ``(0, 1)``.
    difficulties : numpy.ndarray
        Difficulty of each item, in ``(0, 1)``.
    discriminations : numpy.ndarray
        Discrimination of each item.

    Notes
    -----
    In the browser this is a numpy stand-in with the same model
    (:func:`utils.handson.fit_beta3`); the optimiser arguments are accepted
    but not used. On the server and in Colab, the real ``birt-gd`` runs.
    """

    def __init__(self, learning_rate=1, epochs=10000, n_respondents=20, n_items=100,
                 n_inits=1000, n_workers=-1, random_seed=1, tol=10**(-5)):
        self.n_respondents = n_respondents
        self.n_items = n_items

    def fit(self, X, y=None):
        """Fit the model to ``X``, an items-by-respondents matrix of values in ``[0, 1]``."""
        responses = pd.DataFrame(np.asarray(X, dtype=float).T)
        abilities, items = fit_beta3(responses)
        self.abilities = abilities.to_numpy()
        self.difficulties = items["difficulty"].to_numpy()
        self.discriminations = items["discrimination"].to_numpy()
        return self
