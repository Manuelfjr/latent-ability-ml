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


def softplus(x: np.ndarray | float) -> np.ndarray | float:
    """Numerically stable softplus transform."""
    x = np.asarray(x, dtype=float)
    return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0)


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
    """Return a small model set for side-by-side comparisons."""
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
        scores = np.asarray(model.decision_function(X_test), dtype=float)
        return sigmoid(scores)

    predictions = np.asarray(model.predict(X_test), dtype=float)
    return predictions


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


def evaluate_logistic_workflow(
    df: pd.DataFrame,
    test_size: float = 0.30,
    random_state: int = 42,
) -> tuple[pd.DataFrame, LogisticRegression]:
    """Compatibility helper used by the initial notebook scaffold."""
    model = LogisticRegression(max_iter=500)
    results = evaluate_models_on_dataset(
        df=df,
        scenario="single_logistic_workflow",
        models={"logistic_regression": model},
        test_size=test_size,
        random_state=random_state,
    )
    return results.reset_index(drop=True), model


def summarize_classification_results(results: pd.DataFrame, scenario: str | None = None) -> pd.DataFrame:
    """Compute a compact metrics table from a prediction dataframe."""
    group_cols = ["scenario", "model"]
    if scenario is not None:
        results = results.loc[results["scenario"] == scenario].copy()

    summary = (
        results.groupby(group_cols, as_index=False)
        .apply(
            lambda frame: pd.Series(
                {
                    "accuracy": accuracy_score(frame["label"], frame["predicted_label"]),
                    "balanced_accuracy": balanced_accuracy_score(frame["label"], frame["predicted_label"]),
                    "f1": f1_score(frame["label"], frame["predicted_label"]),
                    "mean_difficulty_proxy": frame["difficulty_proxy"].mean(),
                }
            )
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


def beta4_expected_response(
    theta: np.ndarray | float,
    difficulty: np.ndarray | float,
    discrimination: float,
    discrimination_sign: np.ndarray | float,
    discrimination_magnitude: np.ndarray | float,
) -> np.ndarray:
    """Compute expected responses under a simple beta4-style parameterization."""
    if discrimination is None:
        discrimination = discrimination_sign * discrimination_magnitude

    theta_odds = theta / (1.0 - theta)
    difficulty_odds = difficulty / (1.0 - difficulty)
    denominator = 1.0 + (np.power(difficulty_odds, discrimination) * np.power(theta_odds, -discrimination))
    return 1.0 / denominator


# def effective_beta4_discrimination(
#     discrimination_sign: np.ndarray | float,
#     discrimination_magnitude: np.ndarray | float,
# ) -> np.ndarray:
#     """Map sign and magnitude into a single effective discrimination value."""
#     return softplus(discrimination_magnitude) * np.tanh(discrimination_sign)


def make_binary_item_bank() -> pd.DataFrame:
    """Return a tiny item bank for classical binary IRT demos."""
    return pd.DataFrame(
        [
            {"item": "easy_item", "difficulty": -1.2, "discrimination": 0.9},
            {"item": "medium_item", "difficulty": 0.0, "discrimination": 1.2},
            {"item": "hard_item", "difficulty": 1.1, "discrimination": 1.5},
        ]
    )


def make_item_bank(dict_values: list[dict[str, str | float]] | None = None) -> pd.DataFrame:
    """Return a small beta4 item bank for ICC demonstrations."""
    if dict_values is None:
        return pd.DataFrame(
            [
                {
                    "item": "supportive_case",
                    "difficulty": 0.1,
                    "discrimination_sign": 0.1,
                    "discrimination_magnitude": 0.5,
                },
                {
                    "item": "boundary_case",
                    "difficulty": 0.5,
                    "discrimination_sign": 0.5,
                    "discrimination_magnitude": 1.0,
                },
                {
                    "item": "strict_case",
                    "difficulty": 0.9,
                    "discrimination_sign": 0.9,
                    "discrimination_magnitude": 2,
                },
            ]
        )
    return pd.DataFrame(dict_values)


def make_model_ability_grid(n_models: int = 6, low: float = -2.0, high: float = 2.0) -> pd.DataFrame:
    """Create a simple ordered list of models and latent abilities."""
    abilities = np.linspace(low, high, n_models)
    return pd.DataFrame(
        {
            "model": [f"model_{index + 1}" for index in range(n_models)],
            "ability": abilities,
        }
    )


def simulate_binary_irt_responses(
    n_models: int = 6,
    item_bank: pd.DataFrame | None = None,
    random_state: int = 7,
) -> pd.DataFrame:
    """Simulate model-item responses using a classical binary IRT curve."""
    if item_bank is None:
        item_bank = make_binary_item_bank()

    rng = np.random.default_rng(random_state)
    abilities = make_model_ability_grid(n_models=n_models)
    rows: list[dict[str, float | int | str]] = []

    for ability_row in abilities.itertuples(index=False):
        for item_row in item_bank.itertuples(index=False):
            probability = float(
                binary_irt_probability(
                    theta=ability_row.ability,
                    difficulty=item_row.difficulty,
                    discrimination=item_row.discrimination,
                )
            )
            rows.append(
                {
                    "model": ability_row.model,
                    "ability": ability_row.ability,
                    "item": item_row.item,
                    "difficulty": item_row.difficulty,
                    "discrimination": item_row.discrimination,
                    "expected_probability": probability,
                    "observed_correct": int(rng.binomial(1, probability)),
                }
            )

    return pd.DataFrame(rows)


def simulate_latent_ability_dataset(
    n_models: int = 6,
    item_bank: pd.DataFrame | None = None,
    random_state: int = 7,
) -> pd.DataFrame:
    """Simulate responses under a beta4-style latent ability setting."""
    if item_bank is None:
        item_bank = make_item_bank()

    rng = np.random.default_rng(random_state)
    abilities = make_model_ability_grid(n_models=n_models)
    rows: list[dict[str, float | int | str]] = []

    for ability_row in abilities.itertuples(index=False):
        for item_row in item_bank.itertuples(index=False):
            probability = float(
                beta4_expected_response(
                    theta=ability_row.ability,
                    difficulty=item_row.difficulty_logit,
                    discrimination_sign=item_row.discrimination_sign,
                    discrimination_magnitude=item_row.discrimination_magnitude,
                )
            )
            rows.append(
                {
                    "model": ability_row.model,
                    "ability": ability_row.ability,
                    "item": item_row.item,
                    "difficulty_logit": item_row.difficulty_logit,
                    "difficulty_probability": float(sigmoid(item_row.difficulty_logit)),
                    "discrimination_sign": item_row.discrimination_sign,
                    "discrimination_magnitude": item_row.discrimination_magnitude,
                    "effective_discrimination": item_row.discrimination_sign * item_row.discrimination_magnitude,
                    "expected_probability": probability,
                    "observed_correct": int(rng.binomial(1, probability)),
                }
            )

    return pd.DataFrame(rows)


def summarize_latent_results(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate latent ability simulation results at model level."""
    summary = (
        df.groupby(["model", "ability"], as_index=False)
        .agg(
            mean_expected_probability=("expected_probability", "mean"),
            observed_accuracy=("observed_correct", "mean"),
        )
        .sort_values("ability")
    )
    return summary


def make_response_matrix(df: pd.DataFrame, value_column: str = "observed_correct") -> pd.DataFrame:
    """Convert long responses into a model-item matrix."""
    return df.pivot(index="model", columns="item", values=value_column).sort_index()


def plot_binary_iccs(
    item_bank: pd.DataFrame,
    theta: np.ndarray | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot classical binary IRT ICCs."""
    if theta is None:
        theta = np.linspace(-3.0, 3.0, 300)
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))

    for row in item_bank.itertuples(index=False):
        probs = binary_irt_probability(theta, difficulty=row.difficulty, discrimination=row.discrimination)
        ax.plot(
            theta,
            probs,
            label=f"{row.item} (a={row.discrimination:.1f}, b={row.difficulty:.1f})",
        )

    ax.set_title("Binary IRT item characteristic curves")
    ax.set_xlabel("Latent ability")
    ax.set_ylabel("Probability of a correct response")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax


def plot_iccs(
    item_bank: pd.DataFrame,
    theta: np.ndarray | None = None,
    aj: float | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot beta4-style ICCs for a small item bank."""
    if theta is None:
        theta = np.linspace(-3.0, 3.0, 300)
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
            discrimination=aj,
            discrimination_sign=sign,
            discrimination_magnitude=magn,
        )
        ax.plot(
            theta,
            probs,
            label=(
                f"{row.item} (" + f"aj={aj if aj is not None else sign * magn:.2f}, " +
                f"d={row.difficulty:.1f})"
            ),
        )

    ax.set_title("Beta4-style item characteristic curves")
    ax.set_xlabel("Ability")
    ax.set_ylabel("Pij")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax


def plot_beta4_family(
    theta: np.ndarray | None = None,
    # difficulty: float = 0.5,
    # discrimination: float | None = None,
    parameter_pairs: list[tuple[float, float]] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot a family of beta4-style ICCs for discussion."""
    if theta is None:
        theta = np.linspace(-3.0, 3.0, 300)
    if parameter_pairs is None:
        parameter_pairs = [(0.1, -0.5, 2.0), (0.5, 0.1, 2.0), (0.9, 0.5, 2.0)]
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))

    for difficulty, discrimination_sign, discrimination_magnitude in parameter_pairs:
        probs = beta4_expected_response(
            theta=theta,
            difficulty=difficulty,
            discrimination=None,
            discrimination_sign=discrimination_sign,
            discrimination_magnitude=discrimination_magnitude,
        )
        effective_discrimination = float(
            discrimination_sign * discrimination_magnitude
        )
        ax.plot(
            theta,
            probs,
            label=(
                f"diffs={difficulty:.2f}, "
                f"sign={discrimination_sign:.1f}, "
                f"mag={discrimination_magnitude:.1f}, "
                f"aj={effective_discrimination:.2f}"
            ),
        )

    ax.set_title("Beta4 family with varying discrimination")
    ax.set_xlabel("Latent ability logit")
    ax.set_ylabel("Probability of a correct response")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax


def plot_latent_accuracy(summary: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Axes:
    """Plot observed performance against latent ability."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4))

    expected_col = "mean_expected_probability"
    ax.plot(summary["ability"], summary["observed_accuracy"], marker="o", label="Observed accuracy")
    ax.plot(summary["ability"], summary[expected_col], marker="s", label="Expected probability")
    ax.set_title("Performance by latent ability")
    ax.set_xlabel("Latent ability")
    ax.set_ylabel("Proportion correct")
    ax.set_ylim(0, 1.05)
    ax.legend()
    return ax
