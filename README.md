<p>
  <img src="docs/assets/logo_bristol.png" alt="University of Bristol" height="60" style="vertical-align: bottom;" />
    <img align="right" src="docs/assets/logo_cin.png" alt="CIn" height="42" style="vertical-align: bottom;" />
  <img align="right" src="docs/assets/logo_kunumi.png" alt="Kunumi" height="72" style="vertical-align: bottom;" />
  <img align="right" src="docs/assets/logo_ufpe.png" alt="UFPE" height="60" style="vertical-align: bottom;" />
</p>

--- 
# Latent Ability ML

This repository contains the current material for a hands-on workshop on latent-ability-aware evaluation in machine learning.
The workshop is organized as a progression from unsupervised evaluation to binary IRT, and then to Beta4-IRT and CLAIRE.

The main message of the handson is:

- aggregate metrics are useful, but incomplete;
- they usually treat all instances as if they were equally difficult;
- latent-variable models help us separate model ability from item difficulty;
- this leads naturally to richer analyses such as Beta4-IRT and CLAIRE.

## Themes

The current workshop is divided into three connected parts:

1. Unsupervised evaluation and the limitation of weighting all instances equally.
2. Binary IRT, with emphasis on 1PL intuition, 2PL-IRT, and ICC interpretation.
3. Beta4-IRT and CLAIRE as a latent-ability-aware framework for model evaluation.

## Suggested Format

The intended classroom rhythm is:

- `15 minutes` of theory per section
- `15 minutes` of guided practical explanation per section
- `30 minutes` of participant activity per section

Total estimated duration: `3 hours`.

## Audience

The notebooks were designed for participants with mixed backgrounds.
Because of that, the material prioritizes:

- toy problems;
- visual interpretation;
- compact activities;
- code that can be adapted live during the session.

## Current Notebook Sequence

Use the notebooks in the following order during the handson.

### 0. Roadmap

- `notebooks/00_workshop_roadmap.ipynb`
  Workshop framing, timing, and general sequence.

### 1. Unsupervised Evaluation

- `notebooks/01_00_unsupervised_evaluation_toy_problems.ipynb`
  Guided notebook for Section 1.
  Introduces toy clustering datasets, compares clustering models, and motivates the idea that some instances are systematically harder than others.

- `notebooks/01_01_activities.ipynb`
  Activity notebook for Section 1.
  Participants create or adapt a clustering scenario and inspect how aggregate metrics can hide instance-level structure.

- `notebooks/01_99_answer.ipynb`
  Answer notebook for Section 1.
  Provides one possible worked solution for the activity.

### 2. Binary IRT and 2PL

- `notebooks/02_00_binary_irt_and_2pl.ipynb`
  Guided notebook for Section 2.
  Covers binary IRT, 1PL intuition, 2PL-IRT, and reading ICCs through toy item banks.

- `notebooks/02_01_activities.ipynb`
  Activity notebook for Section 2.
  Participants manipulate difficulty and discrimination values and interpret the resulting ICCs.

- `notebooks/02_99_answer.ipynb`
  Answer notebook for Section 2.
  Provides one possible worked solution for the activity.

### 3. Beta4-IRT and CLAIRE

- `notebooks/03_00_beta4_and_claire.ipynb`
  Guided notebook for Section 3.
  Connects the workshop to the research context: Beta4-IRT, CLAIRE, agreement-based response matrices, abilities, difficulties, and discriminations.

- `notebooks/03_01_extra_negative_disc.ipynb`
  Extra analysis notebook.
  This is not the main activity; it was created to investigate, in a more controlled way, how negative discrimination can emerge when the agreement structure is directly perturbed.

- `notebooks/03_02_activities.ipynb`
  Activity notebook for Section 3.
  Participants generate a synthetic dataset with medium to high variability, build the CLAIRE response matrix, train Beta4-IRT, inspect abilities and item parameters, and generate ICCs.

- `notebooks/03_99_answer.ipynb`
  Answer notebook for Section 3.
  Provides a worked version of the main activity.

## How To Use This Repository During The Handson

A practical way to run the session is:

1. Open `00_workshop_roadmap.ipynb` to frame the workshop.
2. Run the guided notebook for the section.
3. Transition immediately to the corresponding activity notebook.
4. Use the `*_99_answer.ipynb` notebooks when you want to consolidate or discuss the activity solutions.
5. Use `03_01_extra_negative_disc.ipynb` only as an extra analytical notebook, not as the default participant activity.

## Repository Structure

```text
.
├── README.md
├── pyproject.toml
├── notebooks/
│   ├── 00_workshop_roadmap.ipynb
│   ├── 01_00_unsupervised_evaluation_toy_problems.ipynb
│   ├── 01_01_activities.ipynb
│   ├── 01_99_answer.ipynb
│   ├── 02_00_binary_irt_and_2pl.ipynb
│   ├── 02_01_activities.ipynb
│   ├── 02_99_answer.ipynb
│   ├── 03_00_beta4_and_claire.ipynb
│   ├── 03_01_extra_negative_disc.ipynb
│   ├── 03_02_activities.ipynb
│   ├── 03_99_answer.ipynb
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

- toy clustering dataset generation;
- clustering evaluation helpers;
- agreement-based response matrix generation;
- summaries of difficult instances;
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

## Presenter Note

This README is meant to serve as the operational guide for the current version of the workshop.
If notebook names, numbering, or roles change again, this file should be updated first so the session flow remains clear.

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
