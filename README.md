# Latent Ability ML Workshop

This repository contains the material for a hands-on session at the University of Bristol CDT.
The workshop connects three themes:

1. Evaluation of supervised methods with toy problems.
2. Item Response Theory (IRT), with emphasis on the Beta4 setting.
3. CLAIRE for latent-ability-aware evaluation.

## Audience

The material is designed for CDT students in Bristol who may come from different technical backgrounds.
The notebooks therefore aim to balance intuition, visual explanations, and reproducible experiments.

## Workshop Goals

By the end of the session, participants should be able to:

- understand why standard supervised metrics can hide important behavior;
- inspect how data difficulty and latent ability affect evaluation;
- interpret item characteristic curves (ICCs) in simple IRT examples;
- connect Beta4-style item behavior to supervised evaluation settings;
- understand where CLAIRE fits as a method for latent ability analysis.

## Repository Structure

- `notebooks/00_workshop_roadmap.ipynb`: session framing, learning goals, and narrative.
- `notebooks/01_supervised_evaluation_toy_problems.ipynb`: classification toy problems and standard metrics.
- `notebooks/02_irt_beta4_icc.ipynb`: IRT intuition, Beta4 discussion, and ICC plots.
- `notebooks/03_claire_latent_ability.ipynb`: CLAIRE motivation, workflow, and analysis prompts.
- `notebooks/workshop_utils.py`: helper functions for synthetic data, plotting, and IRT-style curves.

## Suggested Session Flow

### 1. Why evaluating supervised methods is hard

Start with simple classification examples and show that accuracy alone is not enough.
Use class imbalance, overlapping classes, and noisy labels to motivate richer evaluation.

### 2. From observed performance to latent ability

Introduce the idea that some examples are intrinsically harder than others.
Use this transition to motivate IRT as a framework that separates item difficulty from model ability.

### 3. IRT and Beta4

Explain the meaning of ability, difficulty, discrimination, and guessing.
Then position Beta4 as the specific model variant you want to discuss for this workshop.
Use ICCs to show how the probability of success changes with ability.

### 4. CLAIRE

Present CLAIRE as your proposed method for this setting.
Highlight what problem it solves, how it differs from plain supervised evaluation, and how it relates to IRT.

### 5. Discussion

Close with practical questions:

- When do standard metrics fail?
- What do latent-ability models reveal that confusion matrices do not?
- When should practitioners prefer a latent ability perspective?

## Notebook Development Priorities

If you want to build the workshop incrementally, this is a strong order:

1. Finish `01_supervised_evaluation_toy_problems.ipynb`.
2. Add the core IRT/Beta4 visual narrative in `02_irt_beta4_icc.ipynb`.
3. Turn `03_claire_latent_ability.ipynb` into the bridge from theory to your method.
4. Polish `00_workshop_roadmap.ipynb` last so it reflects the final story.

## Recommended Environment

The notebooks are expected to use:

- Python 3.10+
- NumPy
- Pandas
- Matplotlib
- SciPy
- scikit-learn
- Jupyter

## Next Content To Add

The current scaffold is intentionally lightweight.
The next development step is to replace each notebook placeholder section with:

- one motivating question;
- one minimal toy dataset or plot;
- one takeaway message;
- one transition to the next concept.
