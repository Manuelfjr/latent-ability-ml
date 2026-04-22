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
  "micropipPackages": ["seaborn"],
  "pythonFiles": [
    {"url": "{{ '/assets/python/utils/transform.py' | relative_url }}", "path": "utils/transform.py"},
    {"url": "{{ '/assets/python/utils/handson.py' | relative_url }}", "path": "utils/handson.py"}
  ],
  "browserNote": "When a notebook backend is connected, imports such as `from birt import Beta4` are available. Without it, keep the pure-Python helpers and use Colab for the full Beta4 fitting pipeline.",
  "cells": [
    {"label": "Task 1", "lead": "Generate a synthetic dataset with medium to high variability.", "code": "# answer\n"},
    {"label": "Task 2", "lead": "Train a small pool of clustering models.", "code": "# answer\n"},
    {"label": "Task 3", "lead": "Generate the bounded response matrix `pij`.", "code": "# answer\n"},
    {"label": "Task 4", "lead": "Fit Beta4-IRT and inspect abilities, difficulties, and discriminations.", "code": "# answer\n"}
  ]
}
  </script>
</div>
