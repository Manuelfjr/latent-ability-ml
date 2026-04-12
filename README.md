# Latent Ability ML Workshop

This repository contains the material for a hands-on session for the University of Bristol CDT.
The workshop is organized around three connected themes:

1. evaluation of supervised methods with toy problems;
2. classical binary IRT for model evaluation;
3. Beta4-IRT and CLAIRE for latent-ability-aware analysis.

## Audience

The material is designed for CDT students with mixed backgrounds.
The notebooks therefore prioritize clear visuals, simple toy problems, and short interpretation exercises.

## Workshop Narrative

The core message of the session is that standard supervised metrics are useful, but incomplete.
They usually treat all instances as if they were equally difficult.
The notebooks use that limitation to motivate IRT, Beta4, and finally CLAIRE.

## Notebook Structure

- `notebooks/00_workshop_roadmap.ipynb`: workshop framing, timing, and presenter checklist.
- `notebooks/01_supervised_evaluation_toy_problems.ipynb`: multiple-model comparison on easy and hard classification tasks.
- `notebooks/02_irt_beta4_icc.ipynb`: classical binary IRT, item characteristic curves, and the bridge to model evaluation.
- `notebooks/03_claire_latent_ability.ipynb`: Beta4-style ICCs, latent-ability simulations, and CLAIRE positioning.

## Teaching Format

Each notebook is designed around the same structure:

- 15 minutes of theory;
- 15 minutes of guided practical explanation;
- 30 minutes of student activity.

Each section ends with a small activity so students can interpret the toy results rather than only watch the walkthrough.

## Development Priorities

The repository is now structured so that you can keep iterating in this order:

1. polish the examples and plots in notebook `01`;
2. refine the classical binary IRT explanations in notebook `02`;
3. replace the toy CLAIRE bridge with the final wording and examples you want in notebook `03`;
4. adjust notebook `00` last so the roadmap matches the final workshop script.

## Utilities

The shared helper functions live in `utils/handson.py`.
They cover:

- toy classification dataset generation;
- multi-model supervised evaluation;
- instance difficulty summaries;
- classical binary IRT ICCs;
- Beta4-style ICCs;
- latent-ability simulations for the CLAIRE notebook.
