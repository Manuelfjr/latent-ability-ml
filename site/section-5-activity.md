---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants generate a synthetic dataset, build the response matrix, inspect CLAIRE quantities, and connect the workflow back to the theory.
permalink: /section-5-activity/
---

## Browser Lab

This page includes executable Python cells directly in the site. When a notebook backend is connected, `birt` is available and the full CLAIRE workflow can run here; otherwise the page falls back to the pure-Python workshop helpers.

## Shared Helpers You Can Use

The CLAIRE activity can use the same helpers in the browser notebook, in the local notebook, and in Colab. The point is to let you focus on the latent analysis rather than rewriting support code.

```python
from utils.handson import (
    beta4_expected_response,
    build_claire_response_matrix,
    compute_claire_like_scores,
    estimate_case_statistics,
    make_toy_clustering_partitions,
)
from utils.transform import TransformPairwise
```

- `make_toy_clustering_partitions` gives you a compact starter set of partitions for a CLAIRE-style demo.
- `build_claire_response_matrix` and `TransformPairwise` both make the agreement-to-response-matrix step explicit.
- `estimate_case_statistics` and `compute_claire_like_scores` provide simple summaries that help inspect the response matrix before or after fitting.
- `beta4_expected_response` is available when you want to interpret representative items back through a bounded-response curve.

Inside the browser notebook editor, hovering one of these helper names now shows its docstring.

## Notebook

- Activity notebook: `05_02_activities.ipynb`
- Goal: inspect individual items and connect the practical workflow back to the CLAIRE theory

## What Participants Should Do

- generate a synthetic dataset;
- produce the response matrix;
- inspect ability, difficulty, discrimination, and ICCs.

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/05_02_activities.ipynb">Open activity notebook</a>
  <a class="button secondary" href="https://colab.research.google.com/github/manuelfjr/latent-ability-ml/blob/main/notebooks/05_02_activities.ipynb" target="_blank" rel="noreferrer">Open in Colab</a>
  <a class="button secondary" href="{{ '/section-5/' | relative_url }}">Back to section</a>
</div>

<div class="browser-notebook" data-notebook-id="section-5-activity">
  <script type="application/json" class="browser-notebook__seed">
{
  "title": "Section 5 browser notebook",
  "lead": "Work through the full CLAIRE activity sequence in the page: synthetic data, model pool, response matrix, latent summaries, and item-level inspection.",
  "packages": ["numpy", "pandas", "matplotlib", "scipy", "scikit-learn", "micropip"],
  "micropipPackages": ["seaborn", "plotly", "statsmodels", "openpyxl"],
  "pythonFiles": [
    {"url": "{{ '/assets/python/utils/transform.py' | relative_url }}", "path": "utils/transform.py"},
    {"url": "{{ '/assets/python/utils/handson.py' | relative_url }}", "path": "utils/handson.py"}
  ],
  "browserNote": "When a notebook backend is connected, imports such as `from birt import Beta4` are available. In both modes, students can also use numpy, pandas, matplotlib, seaborn, plotly, statsmodels, openpyxl, and the workshop helpers. Without it, keep the pure-Python helpers and use Colab for the full CLAIRE fitting pipeline.",
  "libraryCatalog": [
    {"name": "numpy"},
    {"name": "pandas"},
    {"name": "matplotlib"},
    {"name": "scipy"},
    {"name": "scikit-learn"},
    {"name": "plotly"},
    {"name": "statsmodels"},
    {"name": "openpyxl"},
    {"name": "birt", "label": "birt-gd / Beta4", "url": "https://pypi.org/project/birt-gd/", "mode": "backend"}
  ],
  "quickInserts": [
    {"id": "claire-transform", "label": "Insert CLAIRE starter", "description": "Start from TransformPairwise.", "code": "from utils.transform import TransformPairwise\nfrom utils.handson import make_toy_clustering_partitions\n"},
    {"id": "beta4-backend", "label": "Insert Beta4 starter", "description": "Use Beta4 when the backend is connected.", "code": "from birt import Beta4\n"},
    {"id": "plotly-starter", "label": "Insert Plotly starter", "description": "Quick interactive chart.", "code": "import plotly.express as px\nfig = px.scatter(x=[1, 2, 3], y=[2, 1, 4])\nfig\n"}
  ],
  "sliderDemos": [
    {
      "id": "claire-icc-lab",
      "title": "Interactive CLAIRE / Beta4 ICC lab",
      "lead": "Move the latent quantities to see how a representative CLAIRE item would change its response curve.",
      "buttonLabel": "Update CLAIRE curve",
      "template": "import numpy as np\nimport matplotlib.pyplot as plt\nfrom utils.handson import beta4_expected_response\ntheta = np.linspace(0.01, 0.99, 300)\nprob = beta4_expected_response(theta=theta, difficulty={% raw %}{{difficulty}}{% endraw %}, discrimination_sign={% raw %}{{discrimination_sign}}{% endraw %}, discrimination_magnitude={% raw %}{{discrimination_magnitude}}{% endraw %})\nfig, ax = plt.subplots(figsize=(7, 4))\nax.plot(theta, prob, linewidth=2.6, color='#35518e')\nax.set_title('Interactive CLAIRE / Beta4 ICC')\nax.set_xlabel('latent ability')\nax.set_ylabel('expected bounded response')\nax.set_ylim(0, 1.05)\nax.grid(alpha=0.25)\nprint(f'difficulty={% raw %}{{difficulty}}{% endraw %}, sign={% raw %}{{discrimination_sign}}{% endraw %}, magnitude={% raw %}{{discrimination_magnitude}}{% endraw %}')\nplt.show()\n",
      "controls": [
        {"name": "difficulty", "label": "Difficulty", "min": 0.05, "max": 0.95, "step": 0.05, "value": 0.45},
        {"name": "discrimination_sign", "label": "Discrimination sign", "min": -1.0, "max": 1.0, "step": 0.1, "value": 0.8},
        {"name": "discrimination_magnitude", "label": "Discrimination magnitude", "min": 0.2, "max": 2.0, "step": 0.1, "value": 1.1}
      ]
    }
  ],
  "cells": [
    {
      "label": "Task 1",
      "lead": "Generate a synthetic dataset with medium to high variability.",
      "code": "# answer\n",
      "hints": [
        "A useful CLAIRE demo starts with geometry that is easy to visualize but rich enough to produce model disagreement.",
        "Three clusters are often a good compromise between interpretability and nontrivial structure."
      ]
    },
    {
      "label": "Task 2",
      "lead": "Train a pool of clustering models with different inductive biases.",
      "code": "# answer\n",
      "hints": [
        "CLAIRE becomes interesting when the pool is heterogeneous, not when all models are near duplicates.",
        "Keep the partitions in a table-like structure so they can be transformed into pairwise agreement."
      ]
    },
    {
      "label": "Task 3",
      "lead": "Generate the CLAIRE response matrix from agreement.",
      "code": "# answer\n",
      "hints": [
        "Use `TransformPairwise` to turn model partitions into the agreement-based matrix used by CLAIRE.",
        "The response matrix should summarize normalized agreement per model and per instance."
      ]
    },
    {
      "label": "Task 4",
      "lead": "Train Beta4-IRT on the agreement matrix.",
      "code": "# answer\n",
      "hints": [
        "When the backend is connected, `from birt import Beta4` should work directly in the page.",
        "Fit Beta4 on the response matrix and keep the fitted object for the next tasks."
      ]
    },
    {
      "label": "Task 5",
      "lead": "Compare latent-aware summaries with standard clustering metrics.",
      "code": "# answer\n",
      "hints": [
        "This comparison is useful because CLAIRE ability should be related to familiar metrics without collapsing into them.",
        "Think in terms of continuity with classical summaries, not redundancy."
      ]
    },
    {
      "label": "Task 6",
      "lead": "Inspect item difficulties and discriminations.",
      "code": "# answer\n",
      "hints": [
        "Look for instances with high difficulty and ask whether they coincide with visually ambiguous regions.",
        "Discrimination tells you whether an instance separates stronger and weaker models clearly."
      ]
    },
    {
      "label": "Task 7",
      "lead": "Generate ICCs for representative items.",
      "code": "# answer\n",
      "hints": [
        "Pick one easy item and one difficult item if you want a clear contrast in the curves.",
        "The goal is not only to plot the ICCs, but to interpret what they say about agreement structure."
      ]
    },
    {
      "label": "Task 8",
      "lead": "Inspect one representative item in more detail inside the feature space.",
      "code": "# answer\n",
      "hints": [
        "Choose an instance whose latent quantities make it interesting, not just visually central.",
        "Bring the latent reading back to the geometry of the original clustering problem."
      ]
    }
  ]
}
  </script>
</div>
