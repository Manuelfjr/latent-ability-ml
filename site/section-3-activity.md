---
layout: default
title: Activity
eyebrow: Activity Notebook
lead: Participants generate a synthetic Beta4 `pij`, inspect ICCs for specific instances, train Beta4, and check parameter recovery.
permalink: /section-3-activity/
---

## Browser Lab

This page includes executable Python cells directly in the site. You can construct the synthetic `pij` matrix and inspect ICCs directly in the browser runtime. When a notebook backend is connected, `from birt import Beta4` is also available so the same page can train Beta4 and check parameter recovery.

## Shared Helpers You Can Use

The activity notebook, Colab, and the in-page runtime can all use the same shared helpers. This section is designed to keep the focus on Beta4 itself: latent parameter sampling, bounded-response construction, ICC interpretation, and recovery.

```python
from utils.handson import (
    beta4_expected_response,
    plot_beta4_family,
)
```

- `beta4_expected_response` lets you evaluate ICCs from specific Beta4 parameters.
- `plot_beta4_family` is useful when you want to compare several Beta4 parameter settings quickly.
- When the backend is connected, `from birt import Beta4` is available for the training and recovery steps.

Inside the browser notebook editor, hovering one of these helper names now shows its docstring.

## Notebook

- Activity notebook: `03_01_activities.ipynb`
- Goal: understand Beta4 as a bounded-response model before the workshop moves to agreement-based evaluation

## What Participants Should Do

- generate a synthetic bounded-response matrix `pij` from the parameter distributions shown in the section;
- generate ICCs for specific instances, such as the easiest and the hardest;
- train Beta4 on the synthetic `pij` and recover the latent parameters;
- compare the original and estimated parameters, especially through recovery plots such as `theta_i` versus `theta_i_hat`.

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/03_01_activities.ipynb">Open activity notebook</a>
  <a class="button secondary" href="https://colab.research.google.com/github/manuelfjr/latent-ability-ml/blob/main/notebooks/03_01_activities.ipynb" target="_blank" rel="noreferrer">Open in Colab</a>
  <a class="button secondary" href="{{ '/section-3/' | relative_url }}">Back to section</a>
</div>

<div class="browser-notebook" data-notebook-id="section-3-activity">
  <script type="application/json" class="browser-notebook__seed">
{
  "title": "Section 3 browser notebook",
  "lead": "Construct a synthetic Beta4 `pij`, inspect ICCs for specific instances, and train Beta4 when the backend is available.",
  "packages": ["numpy", "pandas", "matplotlib", "scipy", "scikit-learn", "micropip"],
  "micropipPackages": ["seaborn", "plotly", "statsmodels", "openpyxl"],
  "pythonFiles": [
    {"url": "{{ '/assets/python/utils/transform.py' | relative_url }}", "path": "utils/transform.py"},
    {"url": "{{ '/assets/python/utils/handson.py' | relative_url }}", "path": "utils/handson.py"}
  ],
  "browserNote": "You can construct the synthetic `pij` matrix and inspect ICCs directly in the browser runtime. When a notebook backend is connected, `from birt import Beta4` is available for the training and recovery steps. Without it, use Colab for the fitting stage.",
  "quickInserts": [
    {"id": "beta4-imports", "label": "Insert Beta4 starter", "description": "Starter imports for simulation and fitting.", "code": "import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\nfrom utils.handson import beta4_expected_response, plot_beta4_family\nfrom birt import Beta4\n"},
    {"id": "beta4-latent-sampler", "label": "Insert latent sampler", "description": "Sample theta, delta, and a from the section distributions.", "code": "rng = np.random.default_rng(7)\nn_models = 10\nn_items = 120\nsigma0 = 1.0\ntheta_true = rng.beta(1, 1, size=n_models)\ndelta_true = rng.beta(1, 1, size=n_items)\na_true = rng.normal(loc=1.0, scale=sigma0, size=n_items)\na_true = np.where(np.abs(a_true) < 0.05, np.sign(a_true) * 0.05 + (a_true == 0) * 0.05, a_true)\ntau_true = np.sign(a_true)\nomega_true = np.abs(a_true)\n"},
    {"id": "beta4-recovery-plot", "label": "Insert recovery plot", "description": "Scatter true versus estimated parameters.", "code": "fig, ax = plt.subplots(figsize=(5, 5))\nax.scatter(theta_true, theta_hat, alpha=0.8)\nax.plot([0, 1], [0, 1], linestyle='--', color='black')\nax.set_xlabel('theta_true')\nax.set_ylabel('theta_hat')\nax.set_title('Ability recovery')\nax.spines[['top', 'right']].set_visible(False)\nplt.show()\n"}
  ],
  "sliderDemos": [
    {
      "id": "beta4-curve-lab",
      "title": "Interactive Beta4 curve lab",
      "lead": "Change difficulty and the sign or magnitude of discrimination to see how bounded-response curves change.",
      "buttonLabel": "Update Beta4 curve",
      "template": "import numpy as np\nimport matplotlib.pyplot as plt\nfrom utils.handson import beta4_expected_response\n\ntheta = np.linspace(0.01, 0.99, 300)\nprob = beta4_expected_response(theta=theta, difficulty={% raw %}{{difficulty}}{% endraw %}, discrimination_sign={% raw %}{{discrimination_sign}}{% endraw %}, discrimination_magnitude={% raw %}{{discrimination_magnitude}}{% endraw %})\nfig, ax = plt.subplots(figsize=(7, 4))\nax.plot(theta, prob, linewidth=2.6, color='#35518e')\nax.set_title('Interactive Beta4 response curve')\nax.set_xlabel('latent ability')\nax.set_ylabel('expected bounded response')\nax.set_ylim(0, 1.05)\nax.grid(alpha=0.25)\nprint(f'difficulty={% raw %}{{difficulty}}{% endraw %}, sign={% raw %}{{discrimination_sign}}{% endraw %}, magnitude={% raw %}{{discrimination_magnitude}}{% endraw %}')\nplt.show()\n",
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
      "lead": "Generate a synthetic bounded-response matrix `pij` from the latent parameter distributions.",
      "code": "# answer\n",
      "hints": [
        "Use the distributions shown in the section: sample `theta_i` and `delta_j` from Beta laws and sample effective discrimination from a Normal law.",
        "After sampling the latent quantities, build `alpha_ij`, `beta_ij`, and the bounded-response matrix `pij`."
      ]
    },
    {
      "label": "Task 2",
      "lead": "Generate ICCs for specific instances, such as the easiest and the hardest.",
      "code": "# answer\n",
      "hints": [
        "Use the true item parameters to identify the easiest and hardest instances before plotting.",
        "A useful comparison is to plot both ICCs on the same latent ability grid and interpret the contrast."
      ]
    },
    {
      "label": "Task 3",
      "lead": "Train Beta4 on the synthetic `pij` and recover the latent parameters.",
      "code": "# answer\n",
      "hints": [
        "When the backend is connected, import `Beta4` from `birt` and fit it on the matrix you constructed.",
        "Keep the true parameters around so you can compare them with the fitted estimates afterward."
      ]
    },
    {
      "label": "Task 4",
      "lead": "Check whether the recovery succeeded and visualize true versus estimated parameters.",
      "code": "# answer\n",
      "hints": [
        "Start with a recovery plot such as `theta_i` versus `theta_i_hat` and add the diagonal as a reference line.",
        "If possible, repeat the same logic for difficulty and discrimination so you can judge recovery more broadly."
      ]
    }
  ]
}
  </script>
</div>
