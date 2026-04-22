---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants generate a synthetic dataset, build the response matrix, inspect CLAIRE quantities, and connect the workflow back to the theory.
permalink: /section-5-activity/
---

## Browser Lab

This page includes executable Python cells directly in the site. When a notebook backend is connected, `birt` is available and the full CLAIRE workflow can run here; otherwise the page falls back to the pure-Python workshop helpers.

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
  "micropipPackages": ["seaborn"],
  "pythonFiles": [
    {"url": "{{ '/assets/python/utils/transform.py' | relative_url }}", "path": "utils/transform.py"},
    {"url": "{{ '/assets/python/utils/handson.py' | relative_url }}", "path": "utils/handson.py"}
  ],
  "browserNote": "When a notebook backend is connected, imports such as `from birt import Beta4` are available. Without it, keep the pure-Python helpers and use Colab for the full CLAIRE fitting pipeline.",
  "cells": [
    {"label": "Task 1", "lead": "Generate a synthetic dataset with medium to high variability.", "code": "# answer\n"},
    {"label": "Task 2", "lead": "Train a pool of clustering models with different inductive biases.", "code": "# answer\n"},
    {"label": "Task 3", "lead": "Generate the CLAIRE response matrix from agreement.", "code": "# answer\n"},
    {"label": "Task 4", "lead": "Train Beta4-IRT on the agreement matrix.", "code": "# answer\n"},
    {"label": "Task 5", "lead": "Compare latent-aware summaries with standard clustering metrics.", "code": "# answer\n"},
    {"label": "Task 6", "lead": "Inspect item difficulties and discriminations.", "code": "# answer\n"},
    {"label": "Task 7", "lead": "Generate ICCs for representative items.", "code": "# answer\n"},
    {"label": "Task 8", "lead": "Inspect one representative item in more detail inside the feature space.", "code": "# answer\n"}
  ]
}
  </script>
</div>
