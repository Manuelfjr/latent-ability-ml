"""Demonstração do CLAIRE usada no fim da Parte 2 do tutorial no ITA (só leitura, sem exercício).

Agrupa três grupos de dispersões diferentes com vários algoritmos, transforma a concordância entre as
partições numa matriz de respostas e ajusta o β4-IRT, sem usar rótulo nenhum. Gera a figura
e a tabela exibidas no site. Rode a partir da raiz do repositório (precisa do birt-gd):

    python notebooks/ita/claire_demo.py
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from sklearn.cluster import (  # noqa: E402
    DBSCAN,
    AgglomerativeClustering,
    KMeans,
    SpectralClustering,
)
from sklearn.datasets import make_blobs  # noqa: E402
from sklearn.metrics import adjusted_rand_score, silhouette_score  # noqa: E402
from sklearn.mixture import GaussianMixture  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).parent))

from tasks import THEME  # noqa: E402

from utils.transform import TransformPairwise  # noqa: E402

FIGURE = REPO / "site" / "assets" / "ita" / "claire-blobs.png"
DATA = REPO / "site" / "_data" / "ita" / "claire.json"


def model_pool() -> dict[str, object]:
    return {
        "k-médias (k=2)": KMeans(n_clusters=2, n_init=10, random_state=1),
        "k-médias (k=3)": KMeans(n_clusters=3, n_init=10, random_state=1),
        "k-médias (k=5)": KMeans(n_clusters=5, n_init=10, random_state=1),
        "mistura gaussiana (k=3)": GaussianMixture(n_components=3, random_state=1),
        "aglomerativo ward (k=3)": AgglomerativeClustering(n_clusters=3, linkage="ward"),
        "aglomerativo single (k=3)": AgglomerativeClustering(n_clusters=3, linkage="single"),
        "espectral (k=3)": SpectralClustering(n_clusters=3, affinity="nearest_neighbors", n_neighbors=15, random_state=1),
        "DBSCAN (eps=0,5)": DBSCAN(eps=0.5, min_samples=5),
        "DBSCAN (eps=1,0)": DBSCAN(eps=1.0, min_samples=5),
    }


def main() -> None:
    from birt import Beta4

    X, y = make_blobs(n_samples=300, cluster_std=[1.0, 2.5, 0.5], random_state=170)

    partitions = pd.DataFrame({name: model.fit_predict(X) for name, model in model_pool().items()})
    # Linhas = instâncias, colunas = algoritmos; cada célula é a concordância do algoritmo
    # com os demais sobre com quem a instância foi agrupada.
    pij = TransformPairwise(works=1).generate_pij_matrix(partitions)

    beta4 = Beta4(
        learning_rate=1,
        epochs=5000,
        n_respondents=pij.shape[1],
        n_items=pij.shape[0],
        n_inits=200,
        n_workers=1,
        random_seed=1,
        tol=1e-8,
        set_priors=True,
    )
    beta4.fit(pij.values)

    def silhouette(labels):
        return float(silhouette_score(X, labels)) if len(set(labels)) > 1 else float("nan")

    table = pd.DataFrame(
        {
            "algoritmo": partitions.columns,
            "habilidade": beta4.abilities,
            "ari": [adjusted_rand_score(y, partitions[c]) for c in partitions.columns],
            "silhueta": [silhouette(partitions[c]) for c in partitions.columns],
        }
    ).sort_values("habilidade", ascending=False)
    difficulty = np.asarray(beta4.difficulties)

    exec(THEME, {})
    ramp = LinearSegmentedColormap.from_list("kunumi_blue", ["#B9D2EA", "#4392D2", "#14304F"])
    fig, ax = plt.subplots(figsize=(7, 4.2))
    order = np.argsort(difficulty)
    points = ax.scatter(X[order, 0], X[order, 1], c=difficulty[order], cmap=ramp, s=26, edgecolor="#5E5E5E", linewidth=0.3)
    fig.colorbar(points, ax=ax, label="dificuldade CLAIRE", shrink=0.85)
    ax.set_title("Dificuldade de cada ponto, estimada sem rótulos")
    ax.set_xlabel("x₁")
    ax.set_ylabel("x₂")
    ax.set_aspect("equal", adjustable="datalim")
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE, dpi=200, bbox_inches="tight")

    def br(value: float, digits: int = 3) -> str:
        return "—" if np.isnan(value) else f"{value:.{digits}f}".replace(".", ",")

    rho_ari = table.habilidade.corr(table.ari, method="spearman")
    rho_silhouette = table.habilidade.corr(table.silhueta, method="spearman")
    # Valores já formatados em pt-BR para o site.
    payload = {
        "n_points": int(len(X)),
        "n_models": int(partitions.shape[1]),
        "spearman_ari": br(rho_ari, 2),
        "spearman_silhouette": br(rho_silhouette, 2),
        "models": [
            {"name": row.algoritmo, "ability": br(row.habilidade), "ari": br(row.ari), "silhouette": br(row.silhueta)}
            for row in table.itertuples()
        ],
    }
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(table.round(3).to_string(index=False))
    print({k: v for k, v in payload.items() if k != "models"})


if __name__ == "__main__":
    main()
