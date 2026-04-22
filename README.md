<p>
  <img src="docs/assets/logo_bristol.png" alt="University of Bristol" height="60" style="vertical-align: bottom;" />

  <img align="right" src="docs/assets/logo_kunumi.png" alt="Kunumi" height="72" style="vertical-align: bottom;" />
  <img align="right" src="docs/assets/logo_ufpe.png" alt="UFPE" height="60" style="vertical-align: bottom;" />
</p>

---
# Latent Ability

This repository contains the current material for a hands-on workshop on latent-ability-aware evaluation in machine learning.
The workshop is now organized as a progression through supervised evaluation, binary IRT, Beta4-IRT, unsupervised evaluation, and CLAIRE.

The main message of the handson is:

- aggregate metrics are useful, but incomplete;
- local example or instance difficulty matters before we ever fit a latent model;
- latent-variable models help us separate model ability from item difficulty and discrimination;
- this leads naturally to richer analyses such as Beta4-IRT and CLAIRE.

## Themes

The current workshop is divided into five connected parts:

1. Supervised evaluation and example-level difficulty.
2. Binary IRT, with emphasis on 1PL intuition, 2PL-IRT, and ICC interpretation.
3. Beta4-IRT for bounded responses and synthetic recovery checks.
4. Unsupervised evaluation and the limitation of weighting clustering instances equally.
5. CLAIRE as an agreement-based latent-evaluation framework for clustering.

## Suggested Format

For a `3-hour` workshop, the material works best when it is delivered in three combined blocks rather than five isolated mini-sessions:

1. `Section 1` on its own, introducing supervised evaluation and local example difficulty.
2. `Sections 2 and 3` together, moving from binary IRT to Beta4-IRT.
3. `Sections 4 and 5` together, moving from unsupervised evaluation to CLAIRE.

For each block, keep the same cadence:

- `15 minutes` of theory
- `15 minutes` of guided practical explanation
- `30 minutes` of participant activity

That gives:

- `1 hour` for Section 1
- `1 hour` for Sections 2 and 3 together
- `1 hour` for Sections 4 and 5 together

Total estimated duration: `3 hours`.

## Current Notebook Sequence

### 0. Roadmap

- `notebooks/00_workshop_roadmap.ipynb`
  Workshop framing, timing, and general sequence.

### 1. Supervised Evaluation

- `notebooks/01_00_supervised_evaluation_toy_problems.ipynb`
- `notebooks/01_01_activities.ipynb`
- `notebooks/01_02_answer.ipynb`

### 2. Binary IRT and 2PL

- `notebooks/02_00_binary_irt_and_2pl.ipynb`
- `notebooks/02_01_activities.ipynb`
- `notebooks/02_02_answer.ipynb`

### 3. Beta4-IRT

- `notebooks/03_00_beta4_irt.ipynb`
- `notebooks/03_01_activities.ipynb`
- `notebooks/03_02_answer.ipynb`

### 4. Unsupervised Evaluation

- `notebooks/04_00_unsupervised_evaluation_toy_problems.ipynb`
- `notebooks/04_01_activities.ipynb`
- `notebooks/04_02_answer.ipynb`

### 5. CLAIRE

- `notebooks/05_00_claire.ipynb`
- `notebooks/05_01_extra_negative_disc.ipynb`
- `notebooks/05_02_activities.ipynb`
- `notebooks/05_03_answer.ipynb`

## How To Use This Repository During The Handson

1. Open `00_workshop_roadmap.ipynb` to frame the workshop.
2. Run the guided notebook for the section.
3. Transition immediately to the corresponding activity notebook.
4. Use the answer notebook after discussion or consolidation.
5. Use `05_01_extra_negative_disc.ipynb` as an extra analytical notebook, not as the default participant activity.

## Repository Structure

```text
.
├── README.md
├── pyproject.toml
├── notebooks/
│   ├── 00_workshop_roadmap.ipynb
│   ├── 01_00_supervised_evaluation_toy_problems.ipynb
│   ├── 01_01_activities.ipynb
│   ├── 01_02_answer.ipynb
│   ├── 02_00_binary_irt_and_2pl.ipynb
│   ├── 02_01_activities.ipynb
│   ├── 02_02_answer.ipynb
│   ├── 03_00_beta4_irt.ipynb
│   ├── 03_01_activities.ipynb
│   ├── 03_02_answer.ipynb
│   ├── 04_00_unsupervised_evaluation_toy_problems.ipynb
│   ├── 04_01_activities.ipynb
│   ├── 04_02_answer.ipynb
│   ├── 05_00_claire.ipynb
│   ├── 05_01_extra_negative_disc.ipynb
│   ├── 05_02_activities.ipynb
│   ├── 05_03_answer.ipynb
│   └── nb_utils.py
├── docs/
│   ├── 99_script_portuguese.md
│   └── 99_script_english.md
└── utils/
    ├── __init__.py
    ├── handson.py
    └── transform.py
```

## Shared Utilities

The shared helper code lives mainly in:

- `utils/handson.py`
- `utils/transform.py`
- `notebooks/nb_utils.py`

These utilities currently support:

- toy supervised dataset generation and evaluation;
- clustering evaluation helpers;
- agreement-based response matrix generation;
- binary IRT and 2PL ICC plotting;
- Beta4-style response visualization;
- CLAIRE-style agreement analysis.

## Environment

The project uses Poetry for dependency management.

Typical commands:

```bash
poetry install
poetry run jupyter notebook
```

---

# Authors

<table align="center">
  <tr>
    <td align="center" width="280">
      <img src="docs/assets/author_rbcp.png" alt="Ricardo Prudêncio" width="140" height="140" style="border-radius: 50%;" />
    </td>
    <td align="center" width="280">
      <img src="docs/assets/author_mfjr.png" alt="Manuel Ferreira Junior" width="140" height="140" style="border-radius: 50%;" />
    </td>
  </tr>
  <tr>
    <td align="center" width="280" height="40" valign="top">
      <strong>Ricardo Prudêncio</strong>
    </td>
    <td align="center" width="280" height="40" valign="top">
      <strong>Manuel Ferreira Junior</strong>
    </td>
  </tr>
  <tr>
    <td align="center" width="280" height="72" valign="top">
      Professor at UFPE
      <br />
      Centro de Informática (CIn)
    </td>
    <td align="center" width="280" height="72" valign="top">
      Data Scientist at Instituto Kunumi
      <br />
      M.Sc. Student at CIn, UFPE
    </td>
  </tr>
</table>

<p align="center">
  <em>Latent-Ability Evaluation in Machine Learning</em>
</p>
