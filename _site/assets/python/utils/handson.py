"""Utilities for the Bristol latent-ability workshop notebooks."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans, SpectralClustering
from sklearn.datasets import make_blobs, make_circles, make_classification, make_moons
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    adjusted_rand_score,
    balanced_accuracy_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    f1_score,
    silhouette_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from utils.transform import TransformPairwise


def set_project_root(level: int = 1) -> Path:
    """Add the project root to ``sys.path`` and return that path.

    Parameters
    ----------
    level : int, default=1
        Number of parent levels to walk upward from the directory that
        contains this file before appending the result to ``sys.path``.

    Returns
    -------
    pathlib.Path
        Resolved project directory that was appended to ``sys.path``.

    Examples
    --------
    >>> root = set_project_root(level=1)
    >>> root.exists()
    True
    """
    project_dir = Path(__file__).resolve().parent
    for _ in range(level):
        project_dir = project_dir.parent
    sys.path.append(str(project_dir))
    return project_dir


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    """Evaluate the logistic function elementwise.

    Parameters
    ----------
    x : numpy.ndarray or float
        Input value or array of values on the real line.

    Returns
    -------
    numpy.ndarray or float
        Logistic transform of ``x`` with values in ``(0, 1)``.

    Examples
    --------
    >>> round(float(sigmoid(0.0)), 2)
    0.5
    """
    x = np.asarray(x, dtype=float)
    return 1.0 / (1.0 + np.exp(-x))


def logit(p: np.ndarray | float) -> np.ndarray | float:
    """Apply a clipped logit transform to probabilities.

    Parameters
    ----------
    p : numpy.ndarray or float
        Probability value or array of probability values. Inputs are clipped
        to avoid infinities at ``0`` and ``1``.

    Returns
    -------
    numpy.ndarray or float
        Log-odds representation of ``p``.

    Examples
    --------
    >>> round(float(logit(0.5)), 2)
    0.0
    """
    p = np.asarray(p, dtype=float)
    p = np.clip(p, 1e-6, 1.0 - 1e-6)
    return np.log(p / (1.0 - p))


def make_toy_classification_dataset(
    n_samples: int = 300,
    class_sep: float = 1.0,
    flip_y: float = 0.02,
    weights: tuple[float, float] = (0.5, 0.5),
    random_state: int = 42,
) -> pd.DataFrame:
    """Create a 2D classification dataset for workshop demos.

    Parameters
    ----------
    n_samples : int, default=300
        Number of examples to generate.
    class_sep : float, default=1.0
        Separation factor passed to ``sklearn.datasets.make_classification``.
    flip_y : float, default=0.02
        Fraction of labels to flip in order to inject mild noise.
    weights : tuple[float, float], default=(0.5, 0.5)
        Class proportions for the binary dataset.
    random_state : int, default=42
        Seed used by scikit-learn during data generation.

    Returns
    -------
    pandas.DataFrame
        DataFrame with ``feature_1``, ``feature_2``, ``label``, and
        ``example_id`` columns.

    Examples
    --------
    >>> df = make_toy_classification_dataset(n_samples=12, random_state=0)
    >>> list(df.columns)
    ['feature_1', 'feature_2', 'label', 'example_id']
    """
    features, labels = make_classification(
        n_samples=n_samples,
        n_features=2,
        n_informative=2,
        n_redundant=0,
        n_repeated=0,
        n_clusters_per_class=1,
        class_sep=class_sep,
        flip_y=flip_y,
        weights=list(weights),
        random_state=random_state,
    )

    df = pd.DataFrame(features, columns=["feature_1", "feature_2"])
    df["label"] = labels
    df["example_id"] = np.arange(len(df))
    return df


def get_default_supervised_models(random_state: int = 42) -> dict[str, object]:
    """Return the default supervised model pool used in the workshop.

    Parameters
    ----------
    random_state : int, default=42
        Seed forwarded to models that expose a ``random_state`` argument.

    Returns
    -------
    dict[str, object]
        Dictionary mapping short model names to initialized scikit-learn
        estimators.

    Examples
    --------
    >>> models = get_default_supervised_models()
    >>> sorted(models)
    ['decision_tree', 'knn', 'logistic_regression']
    """
    return {
        "logistic_regression": LogisticRegression(max_iter=500),
        "decision_tree": DecisionTreeClassifier(max_depth=4, random_state=random_state),
        "knn": KNeighborsClassifier(n_neighbors=15),
    }


def _build_probability_like_scores(model: object, X_test: pd.DataFrame) -> np.ndarray:
    """Extract probability-like scores from a fitted binary classifier.

    Parameters
    ----------
    model : object
        Fitted estimator with ``predict_proba``, ``decision_function``, or
        ``predict``.
    X_test : pandas.DataFrame
        Feature matrix to score.

    Returns
    -------
    numpy.ndarray
        One score per row in ``X_test``, scaled to behave like a probability.

    Examples
    --------
    >>> class DummyModel:
    ...     def predict(self, X):
    ...         return np.ones(len(X))
    >>> scores = _build_probability_like_scores(DummyModel(), pd.DataFrame({'x': [0, 1]}))
    >>> scores.tolist()
    [1.0, 1.0]
    """
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X_test)[:, 1]

    if hasattr(model, "decision_function"):
        return sigmoid(np.asarray(model.decision_function(X_test), dtype=float))

    return np.asarray(model.predict(X_test), dtype=float)


def evaluate_models_on_dataset(
    df: pd.DataFrame,
    scenario: str,
    models: dict[str, object] | None = None,
    test_size: float = 0.30,
    random_state: int = 42,
) -> pd.DataFrame:
    """Fit several classifiers and return a long prediction table.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset created from the workshop helpers. It must include
        ``feature_1``, ``feature_2``, and ``label`` columns.
    scenario : str
        Human-readable label attached to every prediction row.
    models : dict[str, object] or None, default=None
        Optional estimator dictionary. When ``None``, the default supervised
        model pool is used.
    test_size : float, default=0.30
        Fraction of the dataset reserved for the test split.
    random_state : int, default=42
        Seed used in the train/test split and, when applicable, by the
        default estimators.

    Returns
    -------
    pandas.DataFrame
        Long-form dataframe with one row per test example and model,
        including predictions, probabilities, correctness, and a difficulty
        proxy.

    Examples
    --------
    >>> df = make_toy_classification_dataset(n_samples=40, random_state=0)
    >>> results = evaluate_models_on_dataset(df, scenario='demo', random_state=0)
    >>> {'model', 'correct', 'predicted_probability'}.issubset(results.columns)
    True
    """
    if models is None:
        models = get_default_supervised_models(random_state=random_state)

    features = df[["feature_1", "feature_2"]]
    labels = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=test_size,
        random_state=random_state,
        stratify=labels,
    )

    rows: list[pd.DataFrame] = []
    for model_name, model in models.items():
        model.fit(X_train, y_train)
        probabilities = _build_probability_like_scores(model, X_test)
        predictions = (probabilities >= 0.5).astype(int)

        result = X_test.copy()
        result["example_id"] = X_test.index.to_numpy()
        result["label"] = y_test.to_numpy()
        result["predicted_label"] = predictions
        result["predicted_probability"] = probabilities
        result["correct"] = (result["label"] == result["predicted_label"]).astype(int)
        result["difficulty_proxy"] = 1.0 - np.abs(probabilities - 0.5) * 2.0
        result["scenario"] = scenario
        result["model"] = model_name
        rows.append(result.reset_index(drop=True))

    return pd.concat(rows, ignore_index=True)


def summarize_classification_results(results: pd.DataFrame, scenario: str | None = None) -> pd.DataFrame:
    """Summarize supervised predictions at the model level.

    Parameters
    ----------
    results : pandas.DataFrame
        Long prediction table returned by :func:`evaluate_models_on_dataset`.
    scenario : str or None, default=None
        Optional scenario label used to filter ``results`` before computing
        the summary.

    Returns
    -------
    pandas.DataFrame
        Metrics table with accuracy, balanced accuracy, F1, and mean
        difficulty proxy per model.

    Examples
    --------
    >>> df = make_toy_classification_dataset(n_samples=40, random_state=0)
    >>> results = evaluate_models_on_dataset(df, scenario='demo', random_state=0)
    >>> summary = summarize_classification_results(results)
    >>> 'accuracy' in summary.columns
    True
    """
    if scenario is not None:
        results = results.loc[results["scenario"] == scenario].copy()

    summary = (
        results.groupby(["scenario", "model"], as_index=False)
        .apply(
            lambda frame: pd.Series(
                {
                    "accuracy": accuracy_score(frame["label"], frame["predicted_label"]),
                    "balanced_accuracy": balanced_accuracy_score(frame["label"], frame["predicted_label"]),
                    "f1": f1_score(frame["label"], frame["predicted_label"]),
                    "mean_difficulty_proxy": frame["difficulty_proxy"].mean(),
                }
            ),
            include_groups=False,
        )
        .reset_index(drop=True)
    )
    return summary


def summarize_instance_difficulty(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate supervised predictions at the example level.

    Parameters
    ----------
    results : pandas.DataFrame
        Long prediction table returned by :func:`evaluate_models_on_dataset`.

    Returns
    -------
    pandas.DataFrame
        One row per example with agreement, mean confidence, and a difficulty
        proxy aggregated across the model pool.

    Examples
    --------
    >>> df = make_toy_classification_dataset(n_samples=40, random_state=0)
    >>> results = evaluate_models_on_dataset(df, scenario='demo', random_state=0)
    >>> summary = summarize_instance_difficulty(results)
    >>> 'disagreement' in summary.columns
    True
    """
    summary = (
        results.groupby(["scenario", "example_id", "feature_1", "feature_2", "label"], as_index=False)
        .agg(
            mean_correct=("correct", "mean"),
            mean_predicted_probability=("predicted_probability", "mean"),
            mean_difficulty_proxy=("difficulty_proxy", "mean"),
            disagreement=("predicted_label", "nunique"),
        )
        .sort_values(["scenario", "mean_correct", "mean_difficulty_proxy"], ascending=[True, True, False])
    )
    summary["disagreement"] = (summary["disagreement"] > 1).astype(int)
    return summary


def plot_classification_dataset(df: pd.DataFrame, ax=None):
    """Plot a 2D supervised dataset colored by class label.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset with ``feature_1``, ``feature_2``, and ``label`` columns.
    ax : matplotlib.axes.Axes or None, default=None
        Existing axes on which to draw. When ``None``, a new figure and axes
        are created.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the scatter plot.

    Examples
    --------
    >>> df = make_toy_classification_dataset(n_samples=20, random_state=0)
    >>> ax = plot_classification_dataset(df)
    >>> ax.get_title()
    'Toy classification problem'
    """
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))

    for label, group in df.groupby("label"):
        ax.scatter(group["feature_1"], group["feature_2"], label=f"class {label}", alpha=0.75)

    ax.set_title("Toy classification problem")
    ax.set_xlabel("feature_1")
    ax.set_ylabel("feature_2")
    ax.legend()
    return ax


def plot_example_difficulty(summary: pd.DataFrame, ax=None):
    """Plot supervised example difficulty in feature space.

    Parameters
    ----------
    summary : pandas.DataFrame
        Example-level summary returned by
        :func:`summarize_instance_difficulty`.
    ax : matplotlib.axes.Axes or None, default=None
        Existing axes on which to draw. When ``None``, a new figure and axes
        are created.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the difficulty scatter plot.

    Examples
    --------
    >>> df = make_toy_classification_dataset(n_samples=40, random_state=0)
    >>> results = evaluate_models_on_dataset(df, scenario='demo', random_state=0)
    >>> summary = summarize_instance_difficulty(results)
    >>> ax = plot_example_difficulty(summary)
    >>> ax.get_ylabel()
    'feature_2'
    """
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))

    scatter = ax.scatter(
        summary["feature_1"],
        summary["feature_2"],
        c=summary["mean_difficulty_proxy"],
        s=80 + 120 * summary["disagreement"],
        cmap="magma",
        alpha=0.8,
        edgecolor="black",
        linewidth=0.3,
    )
    ax.set_title("Example difficulty proxy and model disagreement")
    ax.set_xlabel("feature_1")
    ax.set_ylabel("feature_2")
    plt.colorbar(scatter, ax=ax, label="difficulty proxy")
    return ax

def make_toy_clustering_dataset(
    scenario: str = "easy_blobs",
    n_samples: int = 320,
    random_state: int = 42,
) -> pd.DataFrame:
    """Create a small 2D clustering dataset for workshop experiments.

    Parameters
    ----------
    scenario : str, default='easy_blobs'
        Dataset template to generate. Supported values are
        ``'easy_blobs'``, ``'hard_moons'``, and ``'hard_circles'``.
    n_samples : int, default=320
        Number of instances to generate.
    random_state : int, default=42
        Seed forwarded to the scikit-learn dataset generator.

    Returns
    -------
    pandas.DataFrame
        DataFrame with feature columns, teaching labels, instance ids, and
        the originating scenario name.

    Examples
    --------
    >>> df = make_toy_clustering_dataset('easy_blobs', n_samples=12, random_state=0)
    >>> {'feature_1', 'feature_2', 'label', 'instance_id'}.issubset(df.columns)
    True
    """
    if scenario == "easy_blobs":
        features, labels = make_blobs(
            n_samples=n_samples,
            centers=[(-2.5, -2.0), (2.5, 2.0)],
            cluster_std=[0.8, 0.9],
            random_state=random_state,
        )
    elif scenario == "hard_moons":
        features, labels = make_moons(
            n_samples=n_samples,
            noise=0.12,
            random_state=random_state,
        )
    elif scenario == "hard_circles":
        features, labels = make_circles(
            n_samples=n_samples,
            noise=0.08,
            factor=0.45,
            random_state=random_state,
        )
    else:
        raise ValueError(f"Unsupported scenario: {scenario}")

    df = pd.DataFrame(features, columns=["feature_1", "feature_2"])
    df["label"] = labels
    df["instance_id"] = np.arange(len(df))
    df["scenario_name"] = scenario
    return df


def get_default_clustering_models(n_clusters: int = 2, random_state: int = 42) -> dict[str, object]:
    """Return the default clustering model pool used in the workshop.

    Parameters
    ----------
    n_clusters : int, default=2
        Number of clusters expected from each estimator.
    random_state : int, default=42
        Seed forwarded to stochastic estimators in the model pool.

    Returns
    -------
    dict[str, object]
        Dictionary mapping short model names to initialized clustering
        estimators.

    Examples
    --------
    >>> models = get_default_clustering_models(n_clusters=2)
    >>> sorted(models)
    ['agglomerative', 'kmeans', 'spectral']
    """
    return {
        "kmeans": KMeans(n_clusters=n_clusters, n_init=20, random_state=random_state),
        "agglomerative": AgglomerativeClustering(n_clusters=n_clusters),
        "spectral": SpectralClustering(
            n_clusters=n_clusters,
            affinity="nearest_neighbors",
            assign_labels="kmeans",
            random_state=random_state,
        ),
    }


def evaluate_clustering_models_on_dataset(
    df: pd.DataFrame,
    scenario: str,
    models: dict[str, object] | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Fit a clustering model pool and return long-form assignments.

    Parameters
    ----------
    df : pandas.DataFrame
        Input clustering dataset with ``feature_1``, ``feature_2``, and
        ``label`` columns.
    scenario : str
        Human-readable label attached to every assignment row.
    models : dict[str, object] or None, default=None
        Optional clustering estimator dictionary. When ``None``, the default
        clustering pool is used.
    random_state : int, default=42
        Seed used when constructing the default model pool.

    Returns
    -------
    pandas.DataFrame
        Long dataframe with one row per instance and model, including the
        predicted cluster id.

    Examples
    --------
    >>> df = make_toy_clustering_dataset('easy_blobs', n_samples=40, random_state=0)
    >>> assignments = evaluate_clustering_models_on_dataset(df, scenario='demo', random_state=0)
    >>> 'predicted_cluster' in assignments.columns
    True
    """
    features = df[["feature_1", "feature_2"]]
    labels = df["label"]
    n_clusters = int(labels.nunique())

    if models is None:
        models = get_default_clustering_models(n_clusters=n_clusters, random_state=random_state)

    rows: list[pd.DataFrame] = []
    for model_name, model in models.items():
        predicted_cluster = np.asarray(model.fit_predict(features))
        result = df[["instance_id", "feature_1", "feature_2", "label"]].copy()
        result["predicted_cluster"] = predicted_cluster
        result["scenario"] = scenario
        result["model"] = model_name
        rows.append(result)

    return pd.concat(rows, ignore_index=True)


def summarize_clustering_results(assignments: pd.DataFrame) -> pd.DataFrame:
    """Compute aggregate clustering metrics from long-form assignments.

    Parameters
    ----------
    assignments : pandas.DataFrame
        Long assignment table returned by
        :func:`evaluate_clustering_models_on_dataset`.

    Returns
    -------
    pandas.DataFrame
        Metrics table with ARI and internal clustering metrics per model.

    Examples
    --------
    >>> df = make_toy_clustering_dataset('easy_blobs', n_samples=40, random_state=0)
    >>> assignments = evaluate_clustering_models_on_dataset(df, scenario='demo', random_state=0)
    >>> summary = summarize_clustering_results(assignments)
    >>> 'ari' in summary.columns
    True
    """
    rows: list[dict[str, float | str]] = []
    for (scenario, model), frame in assignments.groupby(["scenario", "model"]):
        X = frame[["feature_1", "feature_2"]].to_numpy()
        y_true = frame["label"].to_numpy()
        y_pred = frame["predicted_cluster"].to_numpy()
        n_pred_clusters = len(np.unique(y_pred))

        metrics = {
            "scenario": scenario,
            "model": model,
            "ari": adjusted_rand_score(y_true, y_pred),
            "n_predicted_clusters": n_pred_clusters,
            "silhouette": np.nan,
            "calinski_harabasz": np.nan,
            "davies_bouldin": np.nan,
        }
        if 1 < n_pred_clusters < len(frame):
            metrics["silhouette"] = silhouette_score(X, y_pred)
            metrics["calinski_harabasz"] = calinski_harabasz_score(X, y_pred)
            metrics["davies_bouldin"] = davies_bouldin_score(X, y_pred)
        rows.append(metrics)

    return pd.DataFrame(rows).sort_values(["scenario", "ari"], ascending=[True, False]).reset_index(drop=True)


def summarize_clustering_instance_difficulty(assignments: pd.DataFrame) -> pd.DataFrame:
    """Estimate instance difficulty from clustering-model agreement.

    Parameters
    ----------
    assignments : pandas.DataFrame
        Long assignment table returned by
        :func:`evaluate_clustering_models_on_dataset`.

    Returns
    -------
    pandas.DataFrame
        One row per instance with mean agreement and a derived difficulty
        proxy.

    Examples
    --------
    >>> df = make_toy_clustering_dataset('easy_blobs', n_samples=40, random_state=0)
    >>> assignments = evaluate_clustering_models_on_dataset(df, scenario='demo', random_state=0)
    >>> summary = summarize_clustering_instance_difficulty(assignments)
    >>> 'difficulty_proxy' in summary.columns
    True
    """
    key_cols = ["instance_id", "feature_1", "feature_2", "label", "scenario"]
    partitions = assignments.pivot(index="model", columns="instance_id", values="predicted_cluster").sort_index()
    # response_matrix = build_claire_response_matrix(partitions)
    tp = TransformPairwise(1)
    response_matrix = tp.generate_pij_matrix(partitions)

    base = assignments[key_cols].drop_duplicates().sort_values("instance_id").reset_index(drop=True)
    base["mean_model_agreement"] = response_matrix.mean(axis=0).reindex(base["instance_id"]).to_numpy()
    base["difficulty_proxy"] = 1.0 - base["mean_model_agreement"]
    return base.sort_values(["difficulty_proxy", "instance_id"], ascending=[False, True]).reset_index(drop=True)


def plot_clustering_dataset(
    df: pd.DataFrame,
    ax: plt.Axes | None = None,
    title: str = "Toy clustering dataset",
) -> plt.Axes:
    """Plot a clustering dataset colored by teaching labels.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset with ``feature_1``, ``feature_2``, and ``label`` columns.
    ax : matplotlib.axes.Axes or None, default=None
        Existing axes on which to draw. When ``None``, a new figure and axes
        are created.
    title : str, default='Toy clustering dataset'
        Plot title used on the returned axes.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the clustering scatter plot.

    Examples
    --------
    >>> df = make_toy_clustering_dataset('easy_blobs', n_samples=20, random_state=0)
    >>> ax = plot_clustering_dataset(df)
    >>> ax.get_title()
    'Toy clustering dataset'
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))

    for label, group in df.groupby("label"):
        ax.scatter(group["feature_1"], group["feature_2"], label=f"group {label}", alpha=0.75)

    ax.set_title(title)
    ax.set_xlabel("feature_1")
    ax.set_ylabel("feature_2")
    ax.legend()
    return ax


def plot_clustering_instance_difficulty(
    summary: pd.DataFrame,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot agreement-based clustering difficulty in feature space.

    Parameters
    ----------
    summary : pandas.DataFrame
        Instance-level summary returned by
        :func:`summarize_clustering_instance_difficulty`.
    ax : matplotlib.axes.Axes or None, default=None
        Existing axes on which to draw. When ``None``, a new figure and axes
        are created.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the clustering difficulty scatter plot.

    Examples
    --------
    >>> df = make_toy_clustering_dataset('easy_blobs', n_samples=40, random_state=0)
    >>> assignments = evaluate_clustering_models_on_dataset(df, scenario='demo', random_state=0)
    >>> summary = summarize_clustering_instance_difficulty(assignments)
    >>> ax = plot_clustering_instance_difficulty(summary)
    >>> ax.get_xlabel()
    'feature_1'
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))

    scatter = ax.scatter(
        summary["feature_1"],
        summary["feature_2"],
        c=summary["difficulty_proxy"],
        s=100,
        cmap="magma",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.3,
    )
    ax.set_title("Instance difficulty proxy from model agreement")
    ax.set_xlabel("feature_1")
    ax.set_ylabel("feature_2")
    plt.colorbar(scatter, ax=ax, label="difficulty proxy")
    return ax


def binary_irt_probability(
    theta: np.ndarray | float,
    difficulty: np.ndarray | float,
    discrimination: np.ndarray | float = 1.0,
) -> np.ndarray:
    """Compute a binary 2PL success probability.

    Parameters
    ----------
    theta : numpy.ndarray or float
        Respondent ability value or array of ability values.
    difficulty : numpy.ndarray or float
        Item difficulty value or array of difficulty values.
    discrimination : numpy.ndarray or float, default=1.0
        Item discrimination slope in the 2PL model.

    Returns
    -------
    numpy.ndarray
        Probability of success under the logistic 2PL model.

    Examples
    --------
    >>> round(float(binary_irt_probability(0.0, difficulty=0.0, discrimination=1.0)), 2)
    0.5
    """
    theta = np.asarray(theta, dtype=float)
    difficulty = np.asarray(difficulty, dtype=float)
    discrimination = np.asarray(discrimination, dtype=float)
    return sigmoid(discrimination * (theta - difficulty))


def make_binary_item_bank(
        content: list[dict[str, float | str]] | None = None
    ) -> pd.DataFrame:
    """Create a compact item bank for binary IRT and 2PL demos.

    Parameters
    ----------
    content : list[dict[str, float | str]] or None, default=None
        Optional list of item dictionaries. When ``None``, a three-item
        starter bank is returned.

    Returns
    -------
    pandas.DataFrame
        Item bank with ``item``, ``difficulty``, and ``discrimination``
        columns.

    Examples
    --------
    >>> bank = make_binary_item_bank()
    >>> list(bank.columns)
    ['item', 'difficulty', 'discrimination']
    """
    if content is None:
        content = [
            {"item": "easy_item", "difficulty": -1.0, "discrimination": 0.8},
            {"item": "medium_item", "difficulty": 0.0, "discrimination": 1.2},
            {"item": "hard_item", "difficulty": 1.0, "discrimination": 1.6},
        ]
    return pd.DataFrame(content)


def plot_binary_iccs(
    item_bank: pd.DataFrame,
    theta: np.ndarray | None = None,
    ax: plt.Axes | None = None,
    title: str = "Binary IRT / 2PL item characteristic curves",
) -> plt.Axes:
    """Plot binary IRT or 2PL item characteristic curves.

    Parameters
    ----------
    item_bank : pandas.DataFrame
        Item bank with ``item``, ``difficulty``, and ``discrimination``
        columns.
    theta : numpy.ndarray or None, default=None
        Ability grid used to evaluate the curves. When ``None``, a default
        grid in ``[-3, 3]`` is used.
    ax : matplotlib.axes.Axes or None, default=None
        Existing axes on which to draw. When ``None``, a new figure and axes
        are created.
    title : str, default='Binary IRT / 2PL item characteristic curves'
        Plot title shown on the returned axes.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the ICC plot.

    Examples
    --------
    >>> ax = plot_binary_iccs(make_binary_item_bank())
    >>> ax.get_ylim()
    (0.0, 1.05)
    """
    if theta is None:
        theta = np.linspace(-3.0, 3.0, 300)
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))

    for row in item_bank.itertuples(index=False):
        probs = binary_irt_probability(theta, difficulty=row.difficulty, discrimination=row.discrimination)
        ax.plot(
            theta,
            probs,
            label=f"{row.item} (disc={row.discrimination:.1f}, diff={row.difficulty:.1f})",
        )

    ax.set_title(title)
    ax.set_xlabel("latent ability")
    ax.set_ylabel("probability of a correct response")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax


def beta4_expected_response(
    theta: np.ndarray | float,
    difficulty: np.ndarray | float,
    discrimination_sign: np.ndarray | float,
    discrimination_magnitude: np.ndarray | float,
    discrimination: np.ndarray | float | None = None,
) -> np.ndarray:
    """Compute a Beta4-style expected bounded response.

    Parameters
    ----------
    theta : numpy.ndarray or float
        Ability value or array of ability values in ``(0, 1)``.
    difficulty : numpy.ndarray or float
        Item difficulty value or array of values in ``(0, 1)``.
    discrimination_sign : numpy.ndarray or float
        Sign component of the Beta4 discrimination parameter.
    discrimination_magnitude : numpy.ndarray or float
        Magnitude component of the Beta4 discrimination parameter.
    discrimination : numpy.ndarray or float or None, default=None
        Optional precomputed effective discrimination. When ``None``, the
        product of sign and magnitude is used.

    Returns
    -------
    numpy.ndarray
        Expected bounded response for the given latent quantities.

    Examples
    --------
    >>> round(float(beta4_expected_response(0.5, 0.5, 1.0, 1.0)), 2)
    0.5
    """
    theta = np.asarray(theta, dtype=float)
    difficulty = np.asarray(difficulty, dtype=float)
    theta = np.clip(theta, 1e-6, 1.0 - 1e-6)
    difficulty = np.clip(difficulty, 1e-6, 1.0 - 1e-6)

    if discrimination is None:
        discrimination = np.asarray(discrimination_sign, dtype=float) * np.asarray(
            discrimination_magnitude, dtype=float
        )
    else:
        discrimination = np.asarray(discrimination, dtype=float)

    theta_odds = theta / (1.0 - theta)
    difficulty_odds = difficulty / (1.0 - difficulty)
    denominator = 1.0 + np.power(difficulty_odds, discrimination) * np.power(theta_odds, -discrimination)
    return 1.0 / denominator


def make_beta4_item_bank(
        content: list[dict[str, float | str]] | None = None
) -> pd.DataFrame:
    """Create a compact item bank for Beta4 workshop examples.

    Parameters
    ----------
    content : list[dict[str, float | str]] or None, default=None
        Optional list of item dictionaries. When ``None``, a small starter
        bank is created and an ``effective_discrimination`` column is added.

    Returns
    -------
    pandas.DataFrame
        Beta4 item bank with difficulty, sign, magnitude, and effective
        discrimination columns.

    Examples
    --------
    >>> bank = make_beta4_item_bank()
    >>> 'effective_discrimination' in bank.columns
    True
    """
    if content is None:
        content = [
                {
                    "item": "clear_signal",
                    "difficulty": 0.15,
                    "discrimination_sign": 0.40,
                    "discrimination_magnitude": 1.0,
                },
                {
                    "item": "borderline_case",
                    "difficulty": 0.50,
                    "discrimination_sign": 0.75,
                    "discrimination_magnitude": 1.2,
                },
                {
                    "item": "rare_pattern",
                    "difficulty": 0.82,
                    "discrimination_sign": 0.95,
                    "discrimination_magnitude": 1.5,
                },
            ]
    content = pd.DataFrame(content)
    if "effective_discrimination" not in content.columns:
        content["effective_discrimination"] = (
            content["discrimination_sign"] * content["discrimination_magnitude"]
        )
    return content


def plot_beta4_iccs(
    item_bank: pd.DataFrame,
    theta: np.ndarray | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot Beta4-style item curves on an ability grid in ``(0, 1)``.

    Parameters
    ----------
    item_bank : pandas.DataFrame
        Item bank returned by :func:`make_beta4_item_bank`.
    theta : numpy.ndarray or None, default=None
        Ability grid used to evaluate the curves. When ``None``, a default
        grid in ``(0.01, 0.99)`` is used.
    ax : matplotlib.axes.Axes or None, default=None
        Existing axes on which to draw. When ``None``, a new figure and axes
        are created.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the Beta4 curve family.

    Examples
    --------
    >>> ax = plot_beta4_iccs(make_beta4_item_bank())
    >>> ax.get_title()
    'Beta4-style item characteristic curves'
    """
    if theta is None:
        theta = np.linspace(0.01, 0.99, 300)
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))

    for row in item_bank.itertuples(index=False):
        if hasattr(row, "discrimination_sign") and hasattr(row, "discrimination_magnitude"):
            sign = row.discrimination_sign
            magn = row.discrimination_magnitude
        else:
            sign, magn = None, None

        probs = beta4_expected_response(
            theta=theta,
            difficulty=row.difficulty,
            discrimination_sign=row.discrimination_sign,
            discrimination_magnitude=row.discrimination_magnitude,
            discrimination=row.effective_discrimination
        )
        ax.plot(
            theta,
            probs,
            label=(
                f"{row.item} (" + f"aj={row.effective_discrimination if row.effective_discrimination is not None else sign * magn:.2f}, " +
                f"d={row.difficulty:.1f})"
            ),
        )

    ax.set_title("Beta4-style item characteristic curves")
    ax.set_xlabel(r"$\theta_i$")
    ax.set_ylabel(r"$E[p_{ij} | \theta_i, \delta_{j}, \tau_j, \omega_j]$")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="best")
    return ax


def plot_beta4_family(
    parameter_pairs: list[tuple[float, float, float]],
    theta: np.ndarray | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot an explicit family of Beta4 curves for discussion.

    Parameters
    ----------
    parameter_pairs : list[tuple[float, float, float]]
        Sequence of tuples encoding difficulty, discrimination sign,
        discrimination magnitude, and optionally effective discrimination.
    theta : numpy.ndarray or None, default=None
        Ability grid used to evaluate the curves. When ``None``, a default
        grid in ``(0.01, 0.99)`` is used.
    ax : matplotlib.axes.Axes or None, default=None
        Existing axes on which to draw. When ``None``, a new figure and axes
        are created.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the plotted curve family.

    Examples
    --------
    >>> ax = plot_beta4_family([(0.4, 1.0, 1.2, None)])
    >>> ax.get_title()
    'Beta4 family'
    """
    if theta is None:
        theta = np.linspace(0.01, 0.99, 300)
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))

    for difficulty, discrimination_sign, discrimination_magnitude, effective_discrimination in parameter_pairs:
        probs = beta4_expected_response(
            theta=theta,
            difficulty=difficulty,
            discrimination_sign=discrimination_sign,
            discrimination_magnitude=discrimination_magnitude,
            discrimination=effective_discrimination
        )
        if effective_discrimination is None:
            effective_discrimination = discrimination_sign * discrimination_magnitude
        ax.plot(
            theta,
            probs,
            label=(
                f"d={difficulty:.2f}, sign={discrimination_sign:.2f}, "
                f"mag={discrimination_magnitude:.2f}, aj={effective_discrimination:.2f}"
            ),
        )

    ax.set_title("Beta4 family")
    ax.set_xlabel("latent ability")
    ax.set_ylabel("expected response probability")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax


def make_model_ability_grid(
    n_models: int = 6,
    low: float = 0.10,
    high: float = 0.90,
) -> pd.DataFrame:
    """Create an ordered grid of latent abilities for synthetic models.

    Parameters
    ----------
    n_models : int, default=6
        Number of synthetic models to create.
    low : float, default=0.10
        Lowest ability value in the grid.
    high : float, default=0.90
        Highest ability value in the grid.

    Returns
    -------
    pandas.DataFrame
        DataFrame with ``model`` and ``ability`` columns.

    Examples
    --------
    >>> grid = make_model_ability_grid(n_models=3, low=0.2, high=0.8)
    >>> grid['ability'].round(2).tolist()
    [0.2, 0.5, 0.8]
    """
    abilities = np.linspace(low, high, n_models)
    return pd.DataFrame(
        {
            "model": [f"model_{index + 1}" for index in range(n_models)],
            "ability": abilities,
        }
    )


def simulate_beta4_responses(
    n_models: int = 6,
    item_bank: pd.DataFrame | None = None,
    random_state: int = 7,
) -> pd.DataFrame:
    """Simulate model-item responses under a Beta4-style latent setup.

    Parameters
    ----------
    n_models : int, default=6
        Number of synthetic models to simulate.
    item_bank : pandas.DataFrame or None, default=None
        Optional Beta4 item bank. When ``None``, the default starter bank is
        used.
    random_state : int, default=7
        Seed for the random generator that samples observed binary outcomes.

    Returns
    -------
    pandas.DataFrame
        Long dataframe with model ids, latent quantities, expected response,
        and observed correctness.

    Examples
    --------
    >>> responses = simulate_beta4_responses(n_models=3, random_state=0)
    >>> {'model', 'item', 'observed_correct'}.issubset(responses.columns)
    True
    """
    if item_bank is None:
        item_bank = make_beta4_item_bank()

    rng = np.random.default_rng(random_state)
    abilities = make_model_ability_grid(n_models=n_models)
    rows: list[dict[str, float | int | str]] = []

    for ability_row in abilities.itertuples(index=False):
        for item_row in item_bank.itertuples(index=False):
            probability = float(
                beta4_expected_response(
                    theta=ability_row.ability,
                    difficulty=item_row.difficulty,
                    discrimination_sign=item_row.discrimination_sign,
                    discrimination_magnitude=item_row.discrimination_magnitude,
                )
            )
            rows.append(
                {
                    "model": ability_row.model,
                    "ability": ability_row.ability,
                    "item": item_row.item,
                    "difficulty": item_row.difficulty,
                    "discrimination_sign": item_row.discrimination_sign,
                    "discrimination_magnitude": item_row.discrimination_magnitude,
                    "effective_discrimination": item_row.effective_discrimination,
                    "expected_probability": probability,
                    "observed_correct": int(rng.binomial(1, probability)),
                }
            )

    return pd.DataFrame(rows)


def summarize_latent_results(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate simulated Beta4 responses at the model level.

    Parameters
    ----------
    df : pandas.DataFrame
        Long response dataframe returned by :func:`simulate_beta4_responses`.

    Returns
    -------
    pandas.DataFrame
        Model-level table with latent ability, expected score, and observed
        accuracy.

    Examples
    --------
    >>> responses = simulate_beta4_responses(n_models=3, random_state=0)
    >>> summary = summarize_latent_results(responses)
    >>> 'expected_score' in summary.columns
    True
    """
    return (
        df.groupby(["model", "ability"], as_index=False)
        .agg(
            expected_score=("expected_probability", "mean"),
            observed_accuracy=("observed_correct", "mean"),
        )
        .sort_values("ability")
    )


def make_response_matrix(df: pd.DataFrame, value_column: str = "observed_correct") -> pd.DataFrame:
    """Convert long-form responses into a model-by-item matrix.

    Parameters
    ----------
    df : pandas.DataFrame
        Long response dataframe with ``model`` and ``item`` columns.
    value_column : str, default='observed_correct'
        Column used as the matrix value.

    Returns
    -------
    pandas.DataFrame
        Pivoted response matrix indexed by model and columned by item.

    Examples
    --------
    >>> responses = simulate_beta4_responses(n_models=3, random_state=0)
    >>> matrix = make_response_matrix(responses)
    >>> matrix.index.name, matrix.columns.name
    ('model', 'item')
    """
    return df.pivot(index="model", columns="item", values=value_column).sort_index()


def make_toy_clustering_partitions() -> pd.DataFrame:
    """Return a tiny pool of clustering partitions for a CLAIRE demo.

    Parameters
    ----------
    None
        This helper takes no explicit arguments.

    Returns
    -------
    pandas.DataFrame
        Instance-by-model table of cluster assignments that can be transposed
        into CLAIRE's model-by-instance format.

    Examples
    --------
    >>> partitions = make_toy_clustering_partitions()
    >>> partitions.shape
    (6, 4)
    """
    return pd.DataFrame(
        {
            "instance_1": [0, 0, 0, 0],
            "instance_2": [0, 0, 0, 1],
            "instance_3": [0, 0, 1, 1],
            "instance_4": [1, 1, 1, 0],
            "instance_5": [1, 1, 1, 0],
            "instance_6": [1, 1, 0, 1],
        },
        index=["model_a", "model_b", "model_c", "model_d"],
    ).T


def build_claire_response_matrix(partitions: pd.DataFrame) -> pd.DataFrame:
    """Compute a CLAIRE-style agreement matrix from clustering partitions.

    Parameters
    ----------
    partitions : pandas.DataFrame
        Model-by-instance partition table in which rows are models and columns
        are instances.

    Returns
    -------
    pandas.DataFrame
        Agreement-based response matrix with the same shape as ``partitions``.

    Examples
    --------
    >>> partitions = make_toy_clustering_partitions().T
    >>> response_matrix = build_claire_response_matrix(partitions)
    >>> response_matrix.shape == partitions.shape
    True
    """
    model_names = list(partitions.index)
    instance_names = list(partitions.columns)
    responses = pd.DataFrame(index=model_names, columns=instance_names, dtype=float)

    for model_name in model_names:
        for instance_name in instance_names:
            agreements: list[int] = []
            current_label = partitions.loc[model_name, instance_name]
            for other_model in model_names:
                if other_model == model_name:
                    continue
                for other_instance in instance_names:
                    if other_instance == instance_name:
                        continue
                    same_cluster_model = int(
                        current_label == partitions.loc[model_name, other_instance]
                    )
                    same_cluster_other = int(
                        partitions.loc[other_model, instance_name]
                        == partitions.loc[other_model, other_instance]
                    )
                    agreements.append(int(same_cluster_model == same_cluster_other))
            responses.loc[model_name, instance_name] = float(np.mean(agreements))

    return responses


def estimate_case_statistics(response_matrix: pd.DataFrame) -> pd.DataFrame:
    """Estimate simple item statistics from a response matrix.

    Parameters
    ----------
    response_matrix : pandas.DataFrame
        Model-by-item response matrix with values between ``0`` and ``1``.

    Returns
    -------
    pandas.DataFrame
        Table with observed success rate and a simple estimated difficulty per
        item.

    Examples
    --------
    >>> matrix = build_claire_response_matrix(make_toy_clustering_partitions().T)
    >>> stats = estimate_case_statistics(matrix)
    >>> 'estimated_difficulty' in stats.columns
    True
    """
    observed_success = response_matrix.mean(axis=0)
    difficulty = 1.0 - observed_success
    return (
        pd.DataFrame(
            {
                "item": response_matrix.columns,
                "observed_success_rate": observed_success.values,
                "estimated_difficulty": difficulty.values,
            }
        )
        .sort_values("estimated_difficulty", ascending=False)
        .reset_index(drop=True)
    )


def compute_claire_like_scores(response_matrix: pd.DataFrame) -> pd.DataFrame:
    """Create a simple CLAIRE-like model ranking from a response matrix.

    Parameters
    ----------
    response_matrix : pandas.DataFrame
        Model-by-item response matrix with values between ``0`` and ``1``.

    Returns
    -------
    pandas.DataFrame
        Model-level table with observed accuracy and a difficulty-weighted
        CLAIRE-like score.

    Examples
    --------
    >>> matrix = build_claire_response_matrix(make_toy_clustering_partitions().T)
    >>> summary = compute_claire_like_scores(matrix)
    >>> 'claire_like_score' in summary.columns
    True
    """
    case_stats = estimate_case_statistics(response_matrix).set_index("item")
    difficulty_weights = 1.0 + case_stats.loc[response_matrix.columns, "estimated_difficulty"]
    weighted_scores = response_matrix.mul(difficulty_weights, axis=1)

    summary = pd.DataFrame(
        {
            "model": response_matrix.index,
            "observed_accuracy": response_matrix.mean(axis=1).values,
            "claire_like_score": weighted_scores.mean(axis=1).values,
        }
    )
    return summary.sort_values("claire_like_score", ascending=False).reset_index(drop=True)


def plot_latent_accuracy(summary: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Axes:
    """Plot observed and expected performance against latent ability.

    Parameters
    ----------
    summary : pandas.DataFrame
        Model-level summary returned by :func:`summarize_latent_results`.
    ax : matplotlib.axes.Axes or None, default=None
        Existing axes on which to draw. When ``None``, a new figure and axes
        are created.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the latent-accuracy comparison plot.

    Examples
    --------
    >>> responses = simulate_beta4_responses(n_models=3, random_state=0)
    >>> ax = plot_latent_accuracy(summarize_latent_results(responses))
    >>> ax.get_ylabel()
    'proportion correct'
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4))

    ax.plot(summary["ability"], summary["observed_accuracy"], marker="o", label="observed accuracy")
    ax.plot(summary["ability"], summary["expected_score"], marker="s", label="expected probability")
    ax.set_title("Performance by latent ability")
    ax.set_xlabel("latent ability")
    ax.set_ylabel("proportion correct")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax
