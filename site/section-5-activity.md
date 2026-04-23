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
