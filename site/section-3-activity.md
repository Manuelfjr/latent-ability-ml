---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants simulate a synthetic setting, build a bounded response matrix, fit Beta4-IRT, and interpret the resulting latent quantities.
permalink: /section-3-activity/
---

## Browser Lab

This page includes executable Python cells directly in the site. When a notebook backend is available, `birt` can be imported here; otherwise the page falls back to the pure-Python workshop helpers and the Colab notebook remains the companion environment.

## Notebook

- Activity notebook: `03_01_activities.ipynb`
- Goal: inspect Beta4-IRT before moving to agreement-based evaluation

## What Participants Should Do

- generate a synthetic dataset with medium to high variability;
- train a small pool of clustering models;
- build the bounded response matrix `pij`;
- fit Beta4-IRT and inspect the resulting latent quantities.

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/03_01_activities.ipynb">Open activity notebook</a>
  <a class="button secondary" href="https://colab.research.google.com/github/manuelfjr/latent-ability-ml/blob/main/notebooks/03_01_activities.ipynb" target="_blank" rel="noreferrer">Open in Colab</a>
  <a class="button secondary" href="{{ '/section-3/' | relative_url }}">Back to section</a>
</div>

<div class="browser-notebook" data-notebook-id="section-3-activity">
  <script type="application/json" class="browser-notebook__seed">
{
  "title": "Section 3 browser notebook",
  "lead": "Simulate bounded responses in the page, then inspect the Beta4 latent quantities.",
  "packages": ["numpy", "pandas", "matplotlib", "scipy", "scikit-learn", "micropip"],
  "micropipPackages": ["seaborn", "plotly", "statsmodels", "openpyxl"],
  "pythonFiles": [
    {"url": "{{ '/assets/python/utils/transform.py' | relative_url }}", "path": "utils/transform.py"},
    {"url": "{{ '/assets/python/utils/handson.py' | relative_url }}", "path": "utils/handson.py"}
  ],
  "browserNote": "When a notebook backend is connected, imports such as `from birt import Beta4` are available. In both modes, students can also use numpy, pandas, matplotlib, seaborn, plotly, statsmodels, openpyxl, and the workshop helpers. Without the backend, keep the pure-Python helpers and use Colab for the full Beta4 fitting pipeline.",
  "sliderDemos": [
    {
      "id": "beta4-curve-lab",
      "title": "Interactive Beta4 curve lab",
      "lead": "Change difficulty and the sign or magnitude of discrimination to see how bounded-response curves change.",
      "buttonLabel": "Update Beta4 curve",
      "template": "import numpy as np\nimport matplotlib.pyplot as plt\nfrom utils.handson import beta4_expected_response\n\ntheta = np.linspace(0.01, 0.99, 300)\nprob = beta4_expected_response(theta=theta, difficulty={{difficulty}}, discrimination_sign={{discrimination_sign}}, discrimination_magnitude={{discrimination_magnitude}})\nfig, ax = plt.subplots(figsize=(7, 4))\nax.plot(theta, prob, linewidth=2.6, color='#35518e')\nax.set_title('Interactive Beta4 response curve')\nax.set_xlabel('latent ability')\nax.set_ylabel('expected bounded response')\nax.set_ylim(0, 1.05)\nax.grid(alpha=0.25)\nprint(f'difficulty={{difficulty}}, sign={{discrimination_sign}}, magnitude={{discrimination_magnitude}}')\nplt.show()\n",
      "controls": [
        {"name": "difficulty", "label": "Difficulty", "min": 0.05, "max": 0.95, "step": 0.05, "value": 0.5},
        {"name": "discrimination_sign", "label": "Discrimination sign", "min": -1.0, "max": 1.0, "step": 0.1, "value": 0.8},
        {"name": "discrimination_magnitude", "label": "Discrimination magnitude", "min": 0.2, "max": 2.0, "step": 0.1, "value": 1.2}
      ]
    }
  ],
  "cells": [
    {
      "label": "Task 1",
      "lead": "Generate a synthetic dataset with medium to high variability.",
      "code": "# answer\n",
      "hints": [
        "Keep the geometry simple enough to visualize, but add enough overlap or variability to make the latent structure interesting.",
        "A medium-to-high variability setting is more informative if different models do not all behave identically."
      ]
    },
    {
      "label": "Task 2",
      "lead": "Train a small pool of clustering models.",
      "code": "# answer\n",
      "hints": [
        "The pool should contain models with different inductive biases so disagreement becomes meaningful.",
        "Store each partition in a form that you can later turn into a model-by-instance response matrix."
      ]
    },
    {
      "label": "Task 3",
      "lead": "Generate the bounded response matrix `pij`.",
      "code": "# answer\n",
      "hints": [
        "The matrix should contain values in (0, 1), not just binary outcomes.",
        "Think of each row as a model and each column as an item before fitting Beta4."
      ]
    },
    {
      "label": "Task 4",
      "lead": "Fit Beta4-IRT and inspect abilities, difficulties, and discriminations.",
      "code": "# answer\n",
      "hints": [
        "If the backend is connected, you can import `Beta4` directly from `birt`.",
        "After fitting, compare the resulting latent quantities with what you expected from the synthetic construction."
      ]
    }
  ]
}
  </script>
</div>
