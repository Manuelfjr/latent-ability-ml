---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants create or adapt a clustering scenario and inspect how aggregate metrics can mask hard instances.
permalink: /section-4-activity/
---

## Browser Lab

This page now includes executable Python cells directly in the site. Students can edit code, add new cells, delete cells, import the workshop helpers, and work through the activity without leaving the page.

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
