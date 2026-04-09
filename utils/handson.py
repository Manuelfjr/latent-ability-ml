"""Utilities for the Bristol CDT latent ability workshop notebooks."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import train_test_split


def set_project_root(level: int = 1) -> Path:
    """Add the project root to ``sys.path`` and return it."""
    project_dir = Path(__file__).resolve().parent
    for _ in range(level):
        project_dir = project_dir.parent
    sys.path.append(str(project_dir))
    return project_dir


def make_toy_classification_dataset(
    n_samples: int = 300,
    class_sep: float = 1.0,
    flip_y: float = 0.02,
    weights: tuple[float, float] = (0.5, 0.5),
    random_state: int = 42,
) -> pd.DataFrame:
    """Create a 2D classification dataset for evaluation demos."""
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
    return df


def evaluate_logistic_workflow(
    df: pd.DataFrame,
    test_size: float = 0.30,
    random_state: int = 42,
) -> tuple[pd.DataFrame, LogisticRegression]:
    """Train a logistic model and return test predictions with summary fields."""
    features = df[["feature_1", "feature_2"]]
    labels = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=test_size,
        random_state=random_state,
        stratify=labels,
    )

    model = LogisticRegression()
    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    results = X_test.copy()
    results["label"] = y_test.to_numpy()
    results["predicted_label"] = predictions
    results["predicted_probability"] = probabilities
    results["correct"] = (results["label"] == results["predicted_label"]).astype(int)
    results["difficulty_proxy"] = 1.0 - np.abs(probabilities - 0.5) * 2.0
    return results.reset_index(drop=True), model


def summarize_classification_results(results: pd.DataFrame, scenario: str) -> pd.DataFrame:
    """Compute a compact metrics table for a prediction dataframe."""
    return pd.DataFrame(
        [
            {
                "scenario": scenario,
                "accuracy": accuracy_score(results["label"], results["predicted_label"]),
                "balanced_accuracy": balanced_accuracy_score(results["label"], results["predicted_label"]),
                "f1": f1_score(results["label"], results["predicted_label"]),
                "mean_difficulty_proxy": results["difficulty_proxy"].mean(),
            }
        ]
    )


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    """Numerically stable logistic function."""
    return 1.0 / (1.0 + np.exp(-np.asarray(x)))


def softplus(x: np.ndarray | float) -> np.ndarray | float:
    """Numerically stable softplus transform."""
    x = np.asarray(x)
    return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0)


def beta4_expected_response(
    theta_logit: np.ndarray,
    difficulty_logit: float,
    discrimination_sign: float,
    discrimination_magnitude: float,
) -> np.ndarray:
    """Compute the expected ICC under the beta4-IRT parameterization.

    The implementation follows the beta4-IRT expectation using:

    - theta_i = sigmoid(t_i)
    - delta_j = sigmoid(d_j)
    - omega_j = softplus(o_j)
    - beta_j = tanh(b_j)
    - a_j = omega_j * beta_j
    """
    theta = theta_logit  # np.clip(sigmoid(theta_logit), 1e-6, 1.0 - 1e-6)
    delta = difficulty_logit  # float(np.clip(sigmoid(difficulty_logit), 1e-6, 1.0 - 1e-6))
    omega = discrimination_magnitude  # float(softplus(discrimination_magnitude))
    beta = discrimination_sign  # float(np.tanh(discrimination_sign))
    discrimination = omega * beta

    delta_odds = delta / (1.0 - delta)
    theta_odds = theta / (1.0 - theta)
    denominator = 1.0 + (np.power(delta_odds, discrimination) * np.power(theta_odds, -discrimination))
    return 1.0 / denominator


def make_item_bank(dict_values: list[dict[str, str | float]] = None) -> pd.DataFrame:
    """Return a tiny item bank for beta4-IRT ICC demonstrations."""
    if dict_values is None:
        return pd.DataFrame(
            [
                {
                    "item": "easy_item",
                    "difficulty": 0.1, # -1.2,
                    "discrimination_sign": 0.5,
                    "discrimination_magnitude": 2,
                },
                {
                    "item": "medium_item",
                    "difficulty": 0.3, # 0.0,
                    "discrimination_sign": 0.5,
                    "discrimination_magnitude": 2,
                },
                {
                    "item": "hard_item",
                    "difficulty": 0.7, # 1.2,
                    "discrimination_sign": 0.5,
                    "discrimination_magnitude": 2,
                },
            ]
        )
    else:
        return pd.DataFrame(dict_values)


def simulate_latent_ability_dataset(
    n_models: int = 5,
    item_bank: pd.DataFrame | None = None,
    random_state: int = 7,
) -> pd.DataFrame:
    """Simulate model-item responses using a simple 3PL-style mechanism."""
    rng = np.random.default_rng(random_state)
    if item_bank is None:
        item_bank = make_item_bank()

    abilities = np.linspace(-1.2, 1.2, n_models)
    model_names = [f"model_{index + 1}" for index in range(n_models)]
    rows: list[dict[str, float | int | str]] = []

    for model_name, ability in zip(model_names, abilities):
        for row in item_bank.itertuples(index=False):
            probability = float(
                beta4_expected_response(
                    theta_logit=np.array([ability]),
                    difficulty_logit=row.difficulty,
                    discrimination_sign=row.discrimination_sign,
                    discrimination_magnitude=row.discrimination_magnitude,
                )[0]
            )
            effective_discrimination = float(
                softplus(row.discrimination_magnitude) * np.tanh(row.discrimination_sign)
            )
            outcome = int(rng.binomial(1, probability))
            rows.append(
                {
                    "model": model_name,
                    "ability": ability,
                    "item": row.item,
                    "difficulty": row.difficulty,
                    "discrimination_sign": row.discrimination_sign,
                    "discrimination_magnitude": row.discrimination_magnitude,
                    "effective_discrimination": effective_discrimination,
                    "probability_correct": probability,
                    "observed_correct": outcome,
                }
            )

    return pd.DataFrame(rows)


def summarize_latent_results(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate latent ability simulation results at model level."""
    summary = (
        df.groupby(["model", "ability"], as_index=False)
        .agg(
            mean_probability=("probability_correct", "mean"),
            observed_accuracy=("observed_correct", "mean"),
            mean_item_difficulty=("difficulty", "mean"),
        )
        .sort_values("ability")
    )
    return summary


def plot_classification_dataset(df: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Axes:
    """Scatter plot for the toy classification data."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))

    for label, group in df.groupby("label"):
        ax.scatter(group["feature_1"], group["feature_2"], label=f"class {label}", alpha=0.75)

    ax.set_title("Toy classification problem")
    ax.set_xlabel("feature_1")
    ax.set_ylabel("feature_2")
    ax.legend()
    return ax


def plot_iccs(
    item_bank: pd.DataFrame,
    theta: np.ndarray | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot beta4-IRT ICCs for a small item bank."""
    if theta is None:
        theta = np.linspace(-4, 4, 300)
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))

    for row in item_bank.itertuples(index=False):
        probs = beta4_expected_response(
            theta_logit=theta,
            difficulty_logit=row.difficulty,
            discrimination_sign=row.discrimination_sign,
            discrimination_magnitude=row.discrimination_magnitude,
        )
        effective_discrimination = float(
            row.discrimination_magnitude * row.discrimination_sign
        )
        diff = float(row.difficulty)
        ax.plot(sigmoid(theta), probs, label=f"{row.item} (a={effective_discrimination:.2f}, diff={diff:.2f})")

    ax.set_title("Item characteristic curves under beta4-IRT")
    ax.set_xlabel("Latent ability")
    ax.set_ylabel("Response")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax


def plot_beta4_family(
    theta: np.ndarray | None = None,
    parameter_pairs: list[tuple[float, float]] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot a family of beta4-IRT ICCs for discussion."""
    if theta is None:
        theta = np.linspace(-4, 4, 300)
    if parameter_pairs is None:
        parameter_pairs = [(1.5, 0.2), (1.5, 1.0), (-1.5, 1.0)]
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))

    for discrimination_sign, discrimination_magnitude in parameter_pairs:
        probs = beta4_expected_response(
            theta_logit=theta,
            difficulty_logit=0.0,
            discrimination_sign=discrimination_sign,
            discrimination_magnitude=discrimination_magnitude,
        )
        effective_discrimination = float(
            softplus(discrimination_magnitude) * np.tanh(discrimination_sign)
        )
        ax.plot(
            theta,
            probs,
            label=(
                "sign="
                f"{discrimination_sign}, mag={discrimination_magnitude}, a={effective_discrimination:.2f}"
            ),
        )

    ax.set_title("beta4-IRT response curves")
    ax.set_xlabel("Latent ability logit")
    ax.set_ylabel("Probability of success")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax


def plot_latent_accuracy(summary: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Axes:
    """Plot observed performance against latent ability."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4))

    ax.plot(summary["ability"], summary["observed_accuracy"], marker="o", label="Observed accuracy")
    ax.plot(summary["ability"], summary["mean_probability"], marker="s", label="Expected success")
    ax.set_title("Performance by latent ability")
    ax.set_xlabel("Latent ability")
    ax.set_ylabel("Proportion correct")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax
