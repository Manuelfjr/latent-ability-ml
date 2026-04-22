---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants create a toy supervised dataset, compare a small model pool, and inspect which examples remain difficult.
permalink: /section-1-activity/
---

## Browser Lab

This page includes executable Python cells directly in the site. Students can edit code, add new cells, delete cells, import the workshop helpers, and work through the activity without leaving the page.

## Notebook

- Activity notebook: `01_01_activities.ipynb`
- Goal: connect supervised metrics to local example difficulty

## What Participants Should Do

- create or adapt a toy classification dataset;
- compare several supervised models;
- inspect which examples stay ambiguous or disagreement-prone.

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/01_01_activities.ipynb">Open activity notebook</a>
  <a class="button secondary" href="https://colab.research.google.com/github/manuelfjr/latent-ability-ml/blob/main/notebooks/01_01_activities.ipynb" target="_blank" rel="noreferrer">Open in Colab</a>
  <a class="button secondary" href="{{ '/section-1/' | relative_url }}">Back to section</a>
</div>

<div class="browser-notebook" data-notebook-id="section-1-activity">
  <script type="application/json" class="browser-notebook__seed">
{
  "title": "Section 1 browser notebook",
  "lead": "Compare supervised models directly in the page, then inspect the examples that stay difficult.",
  "packages": ["numpy", "pandas", "matplotlib", "scipy", "scikit-learn", "micropip"],
  "micropipPackages": ["seaborn"],
  "pythonFiles": [
    {"url": "{{ '/assets/python/utils/transform.py' | relative_url }}", "path": "utils/transform.py"},
    {"url": "{{ '/assets/python/utils/handson.py' | relative_url }}", "path": "utils/handson.py"}
  ],
  "browserNote": "Available imports include numpy, pandas, matplotlib, scipy, scikit-learn, seaborn, utils.handson, and utils.transform.",
  "cells": [
    {"label": "Task 1", "lead": "Create or adapt a toy classification dataset.", "code": "# answer\n"},
    {"label": "Task 2", "lead": "Evaluate a small pool of supervised models on your dataset.", "code": "# answer\n"},
    {"label": "Task 3", "lead": "Inspect example-level difficulty or disagreement and discuss where the hard cases are.", "code": "# answer\n"}
  ]
}
  </script>
</div>
