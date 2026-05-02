<p>
  <img src="docs/assets/logo_bristol.png" alt="University of Bristol" height="60" style="vertical-align: bottom;" />

  <img align="right" src="docs/assets/logo_kunumi.png" alt="Kunumi" height="72" style="vertical-align: bottom;" />
  <img align="right" src="docs/assets/logo_ufpe.png" alt="UFPE" height="60" style="vertical-align: bottom;" />
</p>

---
# Latent Ability

This repository contains the current material for a `3-hour` hands-on workshop on latent-ability-aware evaluation in machine learning. The workshop begins by using classical supervised evaluation as the motivation for item response theory, then moves to bounded-response latent models, and finally to clustering scenarios where agreement replaces correctness as the central signal.

The guiding idea of the workshop is simple: aggregate metrics are useful, but they do not tell the whole story. Across supervised and unsupervised settings, some examples are structurally easier than others, some are much more informative than others, and a good evaluation framework should be able to separate model ability from item difficulty and, when relevant, item discrimination.

This repository is meant to be useful in two ways:

- for participants, as the workshop material itself;
- for the instructor, as a structured sequence of notebooks, activities, and scripts that support a coherent live delivery.

## Deployment Layout

- `main` is the branch used for the GitHub Pages site and the public workshop material.
- `hf-backend` is the backend-focused branch used for the Hugging Face runtime deployment.
- The Jekyll site source lives in `site/`, while the Python execution API used by the browser notebooks lives in `backend/`.
- In production, the GitHub Pages site points its notebook runtime to the Hugging Face backend space.

## Workshop Arc

The workshop is divided into four connected sections:

1. `Supervised Evaluation + Binary IRT and 2PL`
   We begin with familiar supervised evaluation to show that aggregate scores can hide meaningful variation across examples. Once local variation is visible, binary IRT provides a language for describing it more explicitly. We introduce ability, difficulty, and discrimination, and use ICCs to make those concepts concrete.
2. `Beta4-IRT`
   The third section asks what changes when responses are not binary. Beta4-IRT keeps the latent perspective but adapts it to bounded responses, allowing richer summaries and recovery experiments.
3. `Unsupervised Evaluation`
   We then leave supervised labels behind and ask how evaluation works when clustering models disagree. The main point is that instance-level difficulty does not disappear simply because the setting is unsupervised.
4. `CLAIRE`
   The final section reframes the problem around agreement-based response matrices. CLAIRE uses model agreement across instances to recover latent structure in a setting where correctness is not directly observed.

## Suggested Rhythm

For a `3-hour` workshop, the material works best when it is delivered in three larger blocks:

1. supervised evaluation plus `Binary IRT and 2PL`
2. `Beta4-IRT`
3. `Unsupervised Evaluation` plus `CLAIRE`

For each block, keep the same cadence:

- `15 minutes` of theory
- `15 minutes` of guided hands-on explanation
- `30 minutes` of participant activity

This gives:

- `1 hour` for supervised evaluation plus Binary IRT and 2PL
- `1 hour` for Beta4-IRT
- `1 hour` for unsupervised evaluation plus CLAIRE

Total estimated duration: `3 hours`.

## Notebook Sequence

### 0. Roadmap

- `notebooks/00_workshop_roadmap.ipynb`
  A short framing notebook that introduces the logic of the workshop, the timing, and the path from classical metrics to latent evaluation.

### 1. Supervised Evaluation + Binary IRT and 2PL

- `notebooks/01_00_supervised_evaluation_toy_problems.ipynb`
- `notebooks/02_00_binary_irt_and_2pl.ipynb`
- `notebooks/02_01_activities.ipynb`
- `notebooks/02_02_answer.ipynb`

The supervised notebook is no longer a separate public activity block. It is the guided motivation inside the first section: use it to show why aggregate metrics hide example-level difficulty, then move directly into the Binary IRT and 2PL notebook. The first participant activity is `02_01_activities.ipynb`.

### 2. Beta4-IRT

- `notebooks/03_00_beta4_irt.ipynb`
- `notebooks/03_01_activities.ipynb`
- `notebooks/03_02_answer.ipynb`

### 3. Unsupervised Evaluation

- `notebooks/04_00_unsupervised_evaluation_toy_problems.ipynb`
- `notebooks/04_01_activities.ipynb`
- `notebooks/04_02_answer.ipynb`

### 4. CLAIRE

- `notebooks/05_00_claire.ipynb`
- `notebooks/05_01_extra_negative_disc.ipynb`
- `notebooks/05_02_activities.ipynb`
- `notebooks/05_03_answer.ipynb`

## How To Use This Repository

### If you are attending the workshop

The simplest reading path is:

1. open the roadmap notebook;
2. follow the overview page or main notebook of the current section;
3. move to the corresponding activity notebook, starting with `02_01_activities.ipynb`;
4. compare your work with the answer notebook only after discussion or consolidation.

The activity notebooks are designed as working spaces after the guided exposition. They are intentionally lighter on text so that the conceptual narrative stays in the overview material and the main section notebooks.

The guided notebooks, activities, and answers can be opened in three complementary ways:

- through the workshop site;
- directly on GitHub;
- in Google Colab.

The overview pages on the site expose both GitHub and Colab links for the guided notebooks. The activity and answer pages do the same for their corresponding notebooks.

When you open one of the workshop notebooks in Colab, run the first setup cell before the rest of the notebook. That cell clones this repository into `/content/latent-ability-ml`, installs the core Python dependencies, and adds `notebooks/`, `utils/`, and `src/` to `sys.path` so the shared workshop helpers can be imported normally.

### If you are delivering the workshop

The scripts that support the live delivery are stored locally in:

- `data/99_script_portuguese.md`
- `data/99_script_english.md`

These files are not part of the public site flow. They are instructor-oriented notes that summarize the intended path through the material, the conceptual transitions between sections, and the discussion points worth emphasizing during the live session.

## Repository Structure

```text
.
├── README.md
├── _config.yml
├── backend/
│   ├── README.md
│   ├── app.py
│   ├── executor.py
│   ├── run_huggingface.sh
│   └── run_local.sh
├── data/
│   ├── 99_script_portuguese.md
│   └── 99_script_english.md
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
├── pyproject.toml
├── site/
│   ├── _config.yml
│   ├── _layouts/
│   ├── _data/
│   ├── assets/
│   └── *.md
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

To serve the workshop site locally from the repository root:

```bash
jekyll serve --config _config.yml --host 127.0.0.1 --port 4000
```

If you also want the local Python backend for `birt-gd` and the browser notebooks:

```bash
./backend/run_local.sh
jekyll serve --source site --config site/_config.yml,site/_config.local.yml --host 127.0.0.1 --port 4000
```

The Hugging Face deployment entrypoint is `backend/run_huggingface.sh`, and the container build used for that branch is defined in `Dockerfile`.

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
