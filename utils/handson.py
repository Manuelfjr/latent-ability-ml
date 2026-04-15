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


def set_project_root(level: int = 1) -> Path:
    """Add the project root to ``sys.path`` and return it."""
    project_dir = Path(__file__).resolve().parent
    for _ in range(level):
        project_dir = project_dir.parent
    sys.path.append(str(project_dir))
    return project_dir


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    """Numerically stable logistic function."""
    x = np.asarray(x, dtype=float)
    return 1.0 / (1.0 + np.exp(-x))


def logit(p: np.ndarray | float) -> np.ndarray | float:
    """Safe logit transform for probabilities in ``(0, 1)``."""
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
    """Create a 2D classification dataset for workshop demos."""
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
    """Return a compact set of models for side-by-side evaluation."""
    return {
        "logistic_regression": LogisticRegression(max_iter=500),
        "decision_tree": DecisionTreeClassifier(max_depth=4, random_state=random_state),
        "knn": KNeighborsClassifier(n_neighbors=15),
    }


def _build_probability_like_scores(model: object, X_test: pd.DataFrame) -> np.ndarray:
    """Return probabilities when available, otherwise scale decision scores."""
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
    """Train several classifiers and return a long prediction dataframe."""
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
    """Compute a compact metrics table from a prediction dataframe."""
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
    """Aggregate per-example behavior across several supervised models."""
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


def plot_classification_dataset(df: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Axes:
    """Scatter plot for a toy classification dataset."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))

    for label, group in df.groupby("label"):
        ax.scatter(group["feature_1"], group["feature_2"], label=f"class {label}", alpha=0.75)

    ax.set_title("Toy classification problem")
    ax.set_xlabel("feature_1")
    ax.set_ylabel("feature_2")
    ax.legend()
    return ax


def plot_example_difficulty(summary: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Axes:
    """Visualize which examples are ambiguous or produce disagreement."""
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
    """Create a 2D clustering dataset with labels kept only for teaching support."""
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
    """Return a compact pool of clustering models for workshop comparisons."""
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
    """Fit a small set of clustering models and return per-instance assignments."""
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
    """Compute compact clustering metrics from a long assignment dataframe."""
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
    """Estimate instance difficulty from agreement across clustering models."""
    key_cols = ["instance_id", "feature_1", "feature_2", "label", "scenario"]
    partitions = assignments.pivot(index="model", columns="instance_id", values="predicted_cluster").sort_index()
    response_matrix = build_claire_response_matrix(partitions)

    base = assignments[key_cols].drop_duplicates().sort_values("instance_id").reset_index(drop=True)
    base["mean_model_agreement"] = response_matrix.mean(axis=0).reindex(base["instance_id"]).to_numpy()
    base["difficulty_proxy"] = 1.0 - base["mean_model_agreement"]
    return base.sort_values(["difficulty_proxy", "instance_id"], ascending=[False, True]).reset_index(drop=True)


def plot_clustering_dataset(
    df: pd.DataFrame,
    ax: plt.Axes | None = None,
    title: str = "Toy clustering dataset",
) -> plt.Axes:
    """Scatter plot for a clustering toy problem."""
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
    """Visualize difficult clustering instances based on model agreement."""
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
    """Binary IRT probability under the logistic 2PL form."""
    theta = np.asarray(theta, dtype=float)
    difficulty = np.asarray(difficulty, dtype=float)
    discrimination = np.asarray(discrimination, dtype=float)
    return sigmoid(discrimination * (theta - difficulty))


def make_binary_item_bank(
        content: list[dict[str, float | str]] | None = None
    ) -> pd.DataFrame:
    """Return a tiny item bank for binary IRT and 2PL demos."""
    if content is None:
        content = [
            {"item": "easy_item", "difficulty": 0.1, "discrimination": 0.8},
            {"item": "medium_item", "difficulty": 0.5, "discrimination": 1.2},
            {"item": "hard_item", "difficulty": 0.9, "discrimination": 1.6},
        ]
    return pd.DataFrame(content)


def plot_binary_iccs(
    item_bank: pd.DataFrame,
    theta: np.ndarray | None = None,
    ax: plt.Axes | None = None,
    title: str = "Binary IRT / 2PL item characteristic curves",
) -> plt.Axes:
    """Plot classical binary IRT curves."""
    if theta is None:
        theta = np.linspace(0.01, 0.99, 300)
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
    """Compute a simple Beta4-style expected response curve on ``(0, 1)``."""
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
    """Return a compact item bank for the Beta4 workshop examples."""
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
    """Plot Beta4-style curves over abilities in ``(0, 1)``."""
    if theta is None:
        theta = np.linspace(0.01, 0.99, 300)
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))

    for row in item_bank.itertuples(index=False):
        probs = beta4_expected_response(
            theta=theta,
            difficulty=row.difficulty,
            discrimination_sign=row.discrimination_sign,
            discrimination_magnitude=row.discrimination_magnitude,
        )
        ax.plot(
            theta,
            probs,
            label=(
                f"{row.item} (d={row.difficulty:.2f}, "
                f"sign={row.discrimination_sign:.2f}, mag={row.discrimination_magnitude:.2f})"
            ),
        )

    ax.set_title("Beta4-style item characteristic curves")
    ax.set_xlabel("latent ability")
    ax.set_ylabel("expected response probability")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="best")
    return ax


def plot_beta4_family(
    parameter_pairs: list[tuple[float, float, float]],
    theta: np.ndarray | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot a small family of Beta4 curves for discussion."""
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
    """Create an ordered list of models and latent abilities in ``(0, 1)``."""
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
    """Simulate model-item responses under a Beta4-style latent-ability setting."""
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
    """Aggregate simulated latent-ability results at model level."""
    return (
        df.groupby(["model", "ability"], as_index=False)
        .agg(
            expected_score=("expected_probability", "mean"),
            observed_accuracy=("observed_correct", "mean"),
        )
        .sort_values("ability")
    )


def make_response_matrix(df: pd.DataFrame, value_column: str = "observed_correct") -> pd.DataFrame:
    """Convert long responses into a model-item matrix."""
    return df.pivot(index="model", columns="item", values=value_column).sort_index()


def make_toy_clustering_partitions() -> pd.DataFrame:
    """Return a tiny pool of clustering partitions for a CLAIRE demo."""
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
    """Compute CLAIRE's agreement-based response matrix for a small pool of partitions."""
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
    """Estimate simple item statistics from a binary response matrix."""
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
    """Create a latent-aware ranking inspired by CLAIRE's response-matrix view."""
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
    """Plot observed performance against latent ability."""
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
