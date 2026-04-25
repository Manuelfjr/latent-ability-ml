<p>
  <img src="docs/assets/logo_bristol.png" alt="University of Bristol" height="60" style="vertical-align: bottom;" />

  <img align="right" src="docs/assets/logo_kunumi.png" alt="Kunumi" height="72" style="vertical-align: bottom;" />
  <img align="right" src="docs/assets/logo_ufpe.png" alt="UFPE" height="60" style="vertical-align: bottom;" />
</p>

---
# Latent Ability

This repository contains the current material for a `3-hour` hands-on workshop on latent-ability-aware evaluation in machine learning. The workshop is organized as a progression from classical supervised evaluation to item response theory, then to bounded-response latent models, and finally to clustering scenarios where agreement replaces correctness as the central signal.

The guiding idea of the workshop is simple: aggregate metrics are useful, but they do not tell the whole story. Across supervised and unsupervised settings, some examples are structurally easier than others, some are much more informative than others, and a good evaluation framework should be able to separate model ability from item difficulty and, when relevant, item discrimination.

This repository is meant to be useful in two ways:

- for participants, as the workshop material itself;
- for the instructor, as a structured sequence of notebooks, activities, and scripts that support a coherent live delivery.

## Workshop Arc

The workshop is divided into five connected sections:

1. `Supervised Evaluation`
   We begin with familiar territory: compact performance summaries and toy classification settings. The key move here is to show that even in a supervised problem, aggregate scores can hide meaningful variation across examples.
2. `Binary IRT and 2PL`
   Once local variation is visible, binary IRT provides a language for describing it more explicitly. We introduce ability, difficulty, and discrimination, and use ICCs to make those concepts concrete.
3. `Beta4-IRT`
   The third section asks what changes when responses are not binary. Beta4-IRT keeps the latent perspective but adapts it to bounded responses, allowing richer summaries and recovery experiments.
4. `Unsupervised Evaluation`
   We then leave supervised labels behind and ask how evaluation works when clustering models disagree. The main point is that instance-level difficulty does not disappear simply because the setting is unsupervised.
5. `CLAIRE`
   The final section reframes the problem around agreement-based response matrices. CLAIRE uses model agreement across instances to recover latent structure in a setting where correctness is not directly observed.

## Suggested Rhythm

For a `3-hour` workshop, the material works best when it is delivered in three larger blocks:

1. `Section 1` on its own
2. `Sections 2 and 3` together
3. `Sections 4 and 5` together

For each block, keep the same cadence:

- `15 minutes` of theory
- `15 minutes` of guided hands-on explanation
- `30 minutes` of participant activity

This gives:

- `1 hour` for Section 1
- `1 hour` for Sections 2 and 3 together
- `1 hour` for Sections 4 and 5 together

Total estimated duration: `3 hours`.

## Notebook Sequence

### 0. Roadmap

- `notebooks/00_workshop_roadmap.ipynb`
  A short framing notebook that introduces the logic of the workshop, the timing, and the path from classical metrics to latent evaluation.

### 1. Supervised Evaluation

- `notebooks/01_00_supervised_evaluation_toy_problems.ipynb`
  Guided exposition notebook.
  
This opening section is now treated as a guided conceptual block. It introduces the problem of example-level difficulty in a familiar supervised setting, but it no longer has a separate public activity or answer page in the site flow.

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

## How To Use This Repository

### If you are attending the workshop

The simplest reading path is:

1. open the roadmap notebook;
2. follow the overview page or main notebook of the current section;
3. from Section 2 onward, move to the corresponding activity notebook;
4. compare your work with the answer notebook only after discussion or consolidation.

The activity notebooks are designed as working spaces from Section 2 onward. They are intentionally lighter on exposition so that the conceptual narrative stays in the overview material and the guided section notebooks.

### If you are delivering the workshop

The scripts that support the live delivery are stored locally in:

- `data/99_script_portuguese.md`
- `data/99_script_english.md`

These files are not part of the public site flow. They are instructor-oriented notes that summarize the intended path through the material, the conceptual transitions between sections, and the discussion points worth emphasizing during the live session.

## Repository Structure

```text
.
├── README.md
├── pyproject.toml
├── notebooks/
│   ├── 00_workshop_roadmap.ipynb
│   ├── 01_00_supervised_evaluation_toy_problems.ipynb
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
├── data/
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

To run the workshop site locally:

```bash
jekyll serve --config _config.yml --host 127.0.0.1 --port 4000
```

If you also want the local backend for `birt-gd`:

```bash
./backend/run_local.sh
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
