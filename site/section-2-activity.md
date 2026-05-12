---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants move from the supervised-evaluation motivation into hands-on 2PL ICCs, manipulating difficulty and discrimination values directly.
permalink: /section-2-activity/
---

## Browser Lab

This page now includes executable Python cells directly in the site. Students can adjust 2PL item parameters, rerun cells, add scratch cells, and compare curves without leaving the workshop page.

In this section, the 2PL ability parameter `theta` is real-valued. The interactive lab plots the ICC over `theta` in `[-3, 3]`, which is a common practical window for visualizing the central part of a latent ability scale. Item difficulty is also real-valued and acts as the location of the curve on that axis. Discrimination is a slope parameter; the standard case is positive discrimination, although the input fields allow custom numeric values for exploration.

## Shared Helpers You Can Use

The browser notebook, the local notebook, and Colab can all import the same workshop helpers directly. You do not need to rewrite these utilities during the activity.

```python
from utils.handson import (
    binary_irt_probability,
    make_binary_item_bank,
    plot_binary_iccs,
)
```

- `binary_irt_probability` computes the 2PL probability curve for chosen ability, difficulty, and discrimination values.
- `make_binary_item_bank` creates a small starter item bank that is ready to plot and edit.
- `plot_binary_iccs` plots several ICCs at once so you can compare items quickly in the activity notebook or locally.

Inside the browser notebook editor, hovering one of these helper names now shows its docstring.

## Notebook

- Activity notebook: `02_01_activities.ipynb`
- Goal: connect 2PL item parameters to the geometry of the curves

## What Participants Should Do

- change item difficulty;
- change item discrimination;
- compare 2PL ICC shapes and discuss what they mean.

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/02_01_activities.ipynb">Open activity notebook</a>
  <a class="button secondary" href="https://colab.research.google.com/github/manuelfjr/latent-ability-ml/blob/main/notebooks/02_01_activities.ipynb" target="_blank" rel="noreferrer">Open in Colab</a>
  <a class="button secondary" href="{{ '/section-2/' | relative_url }}">Back to section</a>
</div>

<div class="browser-notebook" data-notebook-id="section-2-activity">
  <script type="application/json" class="browser-notebook__seed">
{
  "title": "Section 2 browser notebook",
  "lead": "Use the supervised-evaluation motivation as context, then manipulate 2PL item parameters directly in the page and inspect how the ICC geometry changes.",
  "packages": [
    "numpy",
    "pandas",
    "matplotlib",
    "scipy",
    "scikit-learn",
    "micropip"
  ],
  "micropipPackages": [
    "seaborn",
    "plotly",
    "statsmodels",
    "openpyxl"
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
    {"id": "irt-imports", "label": "Insert 2PL starter", "description": "Start with the 2PL helpers.", "code": "from utils.handson import make_binary_item_bank, plot_binary_iccs\nimport matplotlib.pyplot as plt\n"},
    {"id": "plotly-scatter", "label": "Insert Plotly starter", "description": "Quick interactive chart.", "code": "import plotly.express as px\nfig = px.scatter(x=[1, 2, 3], y=[2, 1, 4])\nfig\n"}
  ],
  "sliderDemos": [
    {
      "id": "irt-curve-lab",
      "title": "Interactive 2PL curve lab",
      "lead": "Move difficulty and discrimination to see how the 2PL ICC changes before writing your own code.",
      "buttonLabel": "Update curve",
      "template": "import numpy as np\nimport matplotlib.pyplot as plt\nfrom utils.handson import binary_irt_probability\n\ntheta = np.linspace(-3.0, 3.0, 300)\nprob = binary_irt_probability(theta, difficulty=[[difficulty]], discrimination=[[discrimination]])\nfig, ax = plt.subplots(figsize=(7, 4))\nax.plot(theta, prob, linewidth=2.6, color='#ab2330')\nax.set_title('Interactive 2PL ICC')\nax.set_xlabel('latent ability')\nax.set_ylabel('probability of a correct response')\nax.set_ylim(0, 1.05)\nax.grid(alpha=0.25)\nprint(f'difficulty=[[difficulty]], discrimination=[[discrimination]]')\nplt.show()\n",
      "controls": [
        {"name": "difficulty", "label": "Difficulty", "min": -2.0, "max": 2.0, "step": 0.1, "value": 0.0},
        {"name": "discrimination", "label": "Discrimination", "min": 0.2, "max": 3.0, "step": 0.1, "value": 1.2}
      ]
    }
  ],
  "cells": [
    {
      "label": "Task 1",
      "lead": "Build a small item bank and plot the 2PL ICCs.",
      "code": "# answer\n",
      "hints": [
        "The helpers `make_binary_item_bank` and `plot_binary_iccs` give you a clean starting point.",
        "Use three items with different parameter values so the curves are easy to compare visually."
      ]
    },
    {
      "label": "Task 2",
      "lead": "Select instances with different difficulties and see how the location of the curve moves.",
      "code": "# answer\n",
      "hints": [
        "Difficulty mainly shifts the curve left or right along the ability axis.",
        "Keep discrimination fixed while changing difficulty if you want to isolate the effect."
      ]
    },
    {
      "label": "Task 3",
      "lead": "The same from the task 2, but consider the discrimination and compare the ICCs.",
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
