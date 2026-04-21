---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants manipulate difficulty and discrimination values and then interpret the resulting ICCs.
permalink: /section-2-activity/
---

## Browser Lab

This page now includes executable Python cells directly in the site. Students can adjust item parameters, rerun cells, add scratch cells, and compare curves without leaving the workshop page.

## Notebook

- Activity notebook: `02_01_activities.ipynb`
- Goal: connect item parameters to the geometry of the curves

## What Participants Should Do

- change item difficulty;
- change item discrimination;
- compare ICC shapes and discuss what they mean.

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/02_01_activities.ipynb">Open activity notebook</a>
  <a class="button secondary" href="https://colab.research.google.com/github/manuelfjr/latent-ability-ml/blob/main/notebooks/02_01_activities.ipynb" target="_blank" rel="noreferrer">Open in Colab</a>
  <a class="button secondary" href="{{ '/section-2/' | relative_url }}">Back to section</a>
</div>

<div class="browser-notebook" data-notebook-id="section-2-activity">
  <script type="application/json" class="browser-notebook__seed">
{
  "title": "Section 2 browser notebook",
  "lead": "Manipulate item parameters directly in the page and inspect how the ICC geometry changes.",
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
  "browserNote": "Available imports include numpy, pandas, matplotlib, scipy, scikit-learn, seaborn, utils.handson, and utils.transform.",
  "cells": [
    {
      "label": "Task 1",
      "lead": "Build a small item bank and plot the ICCs.",
      "code": "# answer\n"
    },
    {
      "label": "Task 2",
      "lead": "Change difficulty and see how the location of the curve moves.",
      "code": "# answer\n"
    },
    {
      "label": "Task 3",
      "lead": "Change discrimination and compare sharper and flatter ICCs.",
      "code": "# answer\n"
    }
  ]
}
  </script>
</div>
