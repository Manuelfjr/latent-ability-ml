---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants create or adapt a clustering scenario and inspect how aggregate metrics can mask hard instances.
permalink: /section-4-activity/
---

## Browser Lab

This page now includes executable Python cells directly in the site. Students can edit code, add new cells, delete cells, import the workshop helpers, and work through the activity without leaving the page.

## Shared Helpers You Can Use

This activity already has the shared workshop helpers available in the browser runtime, and the same imports work in the local notebook and in Colab.

```python
from utils.handson import (
    evaluate_clustering_models_on_dataset,
    get_default_clustering_models,
    make_toy_clustering_dataset,
    plot_clustering_dataset,
    plot_clustering_instance_difficulty,
    summarize_clustering_instance_difficulty,
    summarize_clustering_results,
)
```

- `make_toy_clustering_dataset` gives you ready-made geometric scenarios that you can keep or adapt.
- `get_default_clustering_models` and `evaluate_clustering_models_on_dataset` provide a fast way to compare a small heterogeneous model pool.
- `summarize_clustering_results` builds the aggregate metrics table for the same assignments.
- `summarize_clustering_instance_difficulty` and `plot_clustering_instance_difficulty` make the agreement-based hard-instance analysis explicit.

Inside the browser notebook editor, hovering one of these helper names now shows its docstring.

## Notebook

- Activity notebook: `04_01_activities.ipynb`
- Goal: analyze a synthetic clustering scenario with a more instance-aware perspective

## What Participants Should Do

- create or adapt a toy clustering dataset;
- compare clustering models;
- inspect hard instances rather than relying only on summary metrics.

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/04_01_activities.ipynb">Open activity notebook</a>
  <a class="button secondary" href="https://colab.research.google.com/github/manuelfjr/latent-ability-ml/blob/main/notebooks/04_01_activities.ipynb" target="_blank" rel="noreferrer">Open in Colab</a>
  <a class="button secondary" href="{{ '/section-4/' | relative_url }}">Back to section</a>
</div>

<div class="browser-notebook" data-notebook-id="section-4-activity">
  <script type="application/json" class="browser-notebook__seed">
{
  "title": "Section 4 browser notebook",
  "lead": "Run clustering experiments directly in the page, then compare model-level metrics with item-level difficulty.",
  "packages": ["numpy", "pandas", "matplotlib", "scipy", "scikit-learn", "micropip"],
  "micropipPackages": ["seaborn", "plotly", "statsmodels", "openpyxl"],
  "pythonFiles": [
    {"url": "{{ '/assets/python/utils/transform.py' | relative_url }}", "path": "utils/transform.py"},
    {"url": "{{ '/assets/python/utils/handson.py' | relative_url }}", "path": "utils/handson.py"}
  ],
  "browserNote": "Available imports include numpy, pandas, matplotlib, scipy, scikit-learn, seaborn, plotly, statsmodels, openpyxl, utils.handson, and utils.transform.",
  "libraryCatalog": [
    {"name": "numpy"},
    {"name": "pandas"},
    {"name": "matplotlib"},
    {"name": "scipy"},
    {"name": "scikit-learn"},
    {"name": "plotly"},
    {"name": "statsmodels"},
    {"name": "openpyxl"}
  ],
  "quickInserts": [
    {"id": "clustering-starter", "label": "Insert clustering starter", "description": "Quick clustering imports.", "code": "from utils.handson import make_toy_clustering_dataset, evaluate_clustering_models_on_dataset, summarize_clustering_instance_difficulty\nimport matplotlib.pyplot as plt\n"},
    {"id": "plotly-clusters", "label": "Insert Plotly clusters", "description": "Interactive scatter example.", "code": "import plotly.express as px\nfig = px.scatter(x=[-1, 0, 1], y=[0.2, 0.5, 0.9], color=['a', 'b', 'a'])\nfig\n"}
  ],
  "sliderDemos": [
    {
      "id": "clustering-noise-lab",
      "title": "Interactive clustering geometry lab",
      "lead": "Increase the moon noise level and see how quickly the geometry becomes harder to separate.",
      "buttonLabel": "Update dataset",
      "template": "import matplotlib.pyplot as plt\nfrom sklearn.datasets import make_moons\nX, y = make_moons(n_samples={% raw %}{{samples}}{% endraw %}, noise={% raw %}{{noise}}{% endraw %}, random_state=7)\nfig, ax = plt.subplots(figsize=(7, 4))\nax.scatter(X[:,0], X[:,1], c=y, cmap='coolwarm', s=28, alpha=0.85)\nax.set_title('Interactive clustering geometry')\nax.set_xlabel('feature_1')\nax.set_ylabel('feature_2')\nax.grid(alpha=0.2)\nprint(f'samples={% raw %}{{samples}}{% endraw %}, noise={% raw %}{{noise}}{% endraw %}')\nplt.show()\n",
      "controls": [
        {"name": "samples", "label": "Samples", "min": 120, "max": 500, "step": 20, "value": 240},
        {"name": "noise", "label": "Noise", "min": 0.02, "max": 0.35, "step": 0.01, "value": 0.12}
      ]
    }
  ],
  "cells": [
    {
      "label": "Task 1",
      "lead": "Create or adapt a toy clustering dataset.",
      "code": "# answer\n",
      "hints": [
        "You can begin with a simple geometric setting and then make it harder through noise, overlap, or curved structure.",
        "A two-dimensional dataset is usually enough for visual discussion."
      ]
    },
    {
      "label": "Task 2",
      "lead": "Compare clustering models on the dataset.",
      "code": "# answer\n",
      "hints": [
        "Pick models with different assumptions, such as centroid-based, connectivity-based, or spectral approaches.",
        "Keep the model outputs so you can compare both summary metrics and pairwise agreement."
      ]
    },
    {
      "label": "Task 3",
      "lead": "Inspect hard instances through agreement rather than only aggregate metrics.",
      "code": "# answer\n",
      "hints": [
        "The most interesting instances are usually those around ambiguous boundaries or local geometric irregularities.",
        "Try to identify points where model disagreement concentrates rather than being spread uniformly."
      ]
    }
  ]
}
  </script>
</div>
