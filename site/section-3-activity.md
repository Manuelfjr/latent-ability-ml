---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants generate a synthetic dataset, build the response matrix, inspect Beta4-style quantities, and connect the workflow back to CLAIRE.
permalink: /section-3-activity/
---

## Browser Lab

This page now includes executable Python cells directly in the site. The browser lab loads the pure-Python workshop helpers, including `TransformPairwise`, so students can build response matrices and explore Beta4-style quantities inside GitHub Pages itself. For the full `birt-gd` training pipeline, keep the Colab notebook as the companion environment.

## Notebook

- Activity notebook: `03_02_activities.ipynb`
- Goal: inspect the individual item and connect the practical workflow back to the theory

## What Participants Should Do

- generate a synthetic dataset;
- produce the response matrix;
- inspect ability, difficulty, discrimination, and ICCs.

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/03_02_activities.ipynb">Open activity notebook</a>
  <a class="button secondary" href="https://colab.research.google.com/github/manuelfjr/latent-ability-ml/blob/main/notebooks/03_02_activities.ipynb" target="_blank" rel="noreferrer">Open in Colab</a>
  <a class="button secondary" href="{{ '/section-3/' | relative_url }}">Back to section</a>
</div>

<div class="browser-notebook" data-notebook-id="section-3-activity">
  <script type="application/json" class="browser-notebook__seed">
{
  "title": "Section 3 browser notebook",
  "lead": "Work through the full CLAIRE activity sequence in the page: synthetic data, model pool, response matrix, Beta4-style summaries, and item-level inspection.",
  "packages": [
    "numpy",
    "pandas",
    "matplotlib",
    "scipy",
    "scikit-learn",
    "micropip"
  ],
  "micropipPackages": [
    "seaborn"
  ],
  "runtimeApiUrls": [
    "http://127.0.0.1:8765",
    "http://localhost:8765"
  ],
  "pythonFiles": [
    {
      "url": "{{ '/assets/python/utils/transform.py' | relative_url }}",
      "path": "utils/transform.py"
    },
    {
      "url": "{{ '/assets/python/utils/handson.py' | relative_url }}",
      "path": "utils/handson.py"
    }
  ],
  "browserNote": "The browser notebook supports the pure-Python workshop helpers, including TransformPairwise and the CLAIRE-style response-matrix utilities. The full birt-gd package is not available here because it imports TensorFlow at module import time. Use the Colab notebook for the complete Beta4 training pipeline.",
  "cells": [
    {
      "label": "Task 1",
      "lead": "Generate a synthetic dataset with medium to high variability.",
      "code": "# answer\n"
    },
    {
      "label": "Task 2",
      "lead": "Train a pool of clustering models with different inductive biases.",
      "code": "# answer\n"
    },
    {
      "label": "Task 3",
      "lead": "Generate the CLAIRE response matrix from agreement.",
      "code": "# answer\n"
    },
    {
      "label": "Task 4",
      "lead": "Prepare the Beta4-IRT training step and inspect what will be fitted.",
      "code": "# answer\n"
    },
    {
      "label": "Task 5",
      "lead": "Compare latent-aware summaries with standard clustering metrics.",
      "code": "# answer\n"
    },
    {
      "label": "Task 6",
      "lead": "Inspect item difficulties and locate the hardest instances.",
      "code": "# answer\n"
    },
    {
      "label": "Task 7",
      "lead": "Select representative items and compare their agreement profiles.",
      "code": "# answer\n"
    },
    {
      "label": "Task 8",
      "lead": "Inspect one representative item in more detail inside the feature space.",
      "code": "# answer\n"
    }
  ]
}
  </script>
</div>
