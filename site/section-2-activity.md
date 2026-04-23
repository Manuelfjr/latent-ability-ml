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
  "sliderDemos": [
    {
      "id": "irt-curve-lab",
      "title": "Interactive IRT curve lab",
      "lead": "Move difficulty and discrimination to see how the binary ICC changes before writing your own code.",
      "buttonLabel": "Update curve",
      "template": "import numpy as np\nimport matplotlib.pyplot as plt\nfrom utils.handson import binary_irt_probability\n\ntheta = np.linspace(0.01, 0.99, 300)\nprob = binary_irt_probability(theta, difficulty={{difficulty}}, discrimination={{discrimination}})\nfig, ax = plt.subplots(figsize=(7, 4))\nax.plot(theta, prob, linewidth=2.6, color='#ab2330')\nax.set_title('Interactive binary ICC')\nax.set_xlabel('latent ability')\nax.set_ylabel('probability of a correct response')\nax.set_ylim(0, 1.05)\nax.grid(alpha=0.25)\nprint(f'difficulty={{difficulty}}, discrimination={{discrimination}}')\nplt.show()\n",
      "controls": [
        {"name": "difficulty", "label": "Difficulty", "min": 0.05, "max": 0.95, "step": 0.05, "value": 0.5},
        {"name": "discrimination", "label": "Discrimination", "min": 0.2, "max": 3.0, "step": 0.1, "value": 1.2}
      ]
    }
  ],
  "cells": [
    {
      "label": "Task 1",
      "lead": "Build a small item bank and plot the ICCs.",
      "code": "# answer\n",
      "hints": [
        "The helpers `make_binary_item_bank` and `plot_binary_iccs` give you a clean starting point.",
        "Use three items with different parameter values so the curves are easy to compare visually."
      ]
    },
    {
      "label": "Task 2",
      "lead": "Change difficulty and see how the location of the curve moves.",
      "code": "# answer\n",
      "hints": [
        "Difficulty mainly shifts the curve left or right along the ability axis.",
        "Keep discrimination fixed while changing difficulty if you want to isolate the effect."
      ]
    },
    {
      "label": "Task 3",
      "lead": "Change discrimination and compare sharper and flatter ICCs.",
      "code": "# answer\n",
      "hints": [
        "Discrimination changes the steepness of the transition region more than the general location.",
        "Compare a low-discrimination item and a high-discrimination item at similar difficulty."
      ]
    }
  ]
}
  </script>
</div>
