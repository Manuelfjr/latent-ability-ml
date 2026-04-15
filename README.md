# Latent Ability ML Workshop

This repository contains the current material for a hands-on workshop built around latent-ability-aware evaluation in machine learning.
The workshop is organized for a University of Bristol context and is structured as a progression from standard unsupervised evaluation to IRT, Beta4-IRT, and CLAIRE.

The central message of the handson is simple:

- standard aggregate metrics are useful, but incomplete;
- they usually treat all instances as if they were equally difficult;
- latent-variable models help us separate model ability from item difficulty;
- this opens the door to richer analyses such as Beta4-IRT and CLAIRE.

## Workshop Themes

The material is divided into three connected parts:

1. Evaluation of unsupervised methods and the limitation of weighting all instances equally.
2. Binary IRT, with emphasis on 1PL intuition, 2PL-IRT, and ICC interpretation.
3. Beta4-IRT and CLAIRE as a latent-ability-aware framework for model evaluation.

## Suggested Format

The intended classroom rhythm is:

- `15 minutes` of theory per section
- `15 minutes` of guided practical explanation per section
- `30 minutes` of participant activity per section

Total estimated duration: `3 hours`.

## Audience

The notebooks are designed for participants with mixed backgrounds.
Because of that, the material prioritizes:

- toy problems;
- short interpretation steps;
- visual explanations;
- lightweight code that can be modified live during the session.

## Current Notebook Sequence

Use the notebooks in the following order during the handson.

### 0. Roadmap

- `notebooks/00_workshop_roadmap.ipynb`
  Workshop framing, session arc, and high-level organization.

### 1. Unsupervised Evaluation

- `notebooks/01_00_unsupervised_evaluation_toy_problems.ipynb`
  Guided notebook for Section 1.
  Introduces toy clustering datasets, compares clustering models, and motivates the idea that some instances are systematically harder than others.

- `notebooks/01_01_activities.ipynb`
  Participant activity notebook for Section 1.
  Students create or modify clustering scenarios and inspect how aggregate metric summaries can hide important structure.

### 2. Binary IRT and 2PL

- `notebooks/02_00_binary_irt_and_2pl.ipynb`
  Guided notebook for Section 2.
  Covers binary IRT, 1PL intuition, 2PL-IRT, and reading ICCs through toy item banks.

- `notebooks/02_01_activities.ipynb`
  Participant activity notebook for Section 2.
  Students manipulate difficulty and discrimination values and interpret the resulting curves.

### 3. Beta4-IRT and CLAIRE


## How To Use This Repository During The Handson

A practical way to run the session is:

1. Open `00_workshop_roadmap.ipynb` to frame the workshop.
2. Run the guided notebook of the section.
3. Transition immediately to the corresponding activity notebook.

## Repository Structure

```text
.
├── README.md
├── pyproject.toml
├── notebooks/
│   ├── 00_workshop_roadmap.ipynb
│   ├── 01_00_unsupervised_evaluation_toy_problems.ipynb
│   ├── 01_01_activities.ipynb
│   ├── 02_00_binary_irt_and_2pl.ipynb
│   ├── 02_01_activities.ipynb
│   └── nb_utils.py
└── utils/
    ├── __init__.py
    └── handson.py
```

## Shared Utilities

The shared helper code lives mainly in:

- `utils/handson.py`
- `notebooks/nb_utils.py`

These utilities support the current notebooks with:

- toy clustering dataset generation;
- clustering evaluation helpers;
- agreement-based summaries of difficult instances;
- binary IRT and 2PL ICC plotting;
- Beta4-style response visualization;
- toy CLAIRE-style agreement computations.

## Environment

The project uses Poetry for dependency management.

Typical commands:

```bash
poetry install
poetry run jupyter notebook
```

## Presenter Note

This README is meant to serve as the operational guide for the current handson version of the repository.
If notebook names, prefixes, or roles change again, this file should be updated first so the workshop flow remains easy to follow.
