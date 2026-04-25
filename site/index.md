---
layout: default
title: Latent Ability
eyebrow: Bristol Workshop
lead: A browsable workshop site for the latent-ability-aware evaluation material, organized by section, activities, and supporting notes.
permalink: /
---

The workshop now progresses through five connected stages: supervised evaluation, binary IRT, Beta4-IRT, unsupervised evaluation, and finally CLAIRE. The site mirrors that sequence so participants can move from intuition to latent modeling and then to agreement-based evaluation without leaving the workshop environment.

## Workshop Structure

<div class="card-grid">
  <div class="card">
    <h3>Section 1</h3>
    <p>Supervised evaluation, compact metric tables, and example-level difficulty.</p>
    <div class="button-row">
      <a class="button" href="{{ '/section-1/' | relative_url }}">Open section</a>
    </div>
  </div>
  <div class="card">
    <h3>Section 2</h3>
    <p>Binary IRT, 1PL intuition, 2PL-IRT, and how to interpret ICCs.</p>
    <div class="button-row">
      <a class="button" href="{{ '/section-2/' | relative_url }}">Open section</a>
      <a class="button secondary" href="{{ '/section-2-activity/' | relative_url }}">Open activity</a>
    </div>
  </div>
  <div class="card">
    <h3>Section 3</h3>
    <p>Beta4-IRT for bounded responses, synthetic recovery, and latent quantities beyond the binary case.</p>
    <div class="button-row">
      <a class="button" href="{{ '/section-3/' | relative_url }}">Open section</a>
      <a class="button secondary" href="{{ '/section-3-activity/' | relative_url }}">Open activity</a>
    </div>
  </div>
  <div class="card">
    <h3>Section 4</h3>
    <p>Unsupervised evaluation and the limitation of treating all clustering instances as equally difficult.</p>
    <div class="button-row">
      <a class="button" href="{{ '/section-4/' | relative_url }}">Open section</a>
      <a class="button secondary" href="{{ '/section-4-activity/' | relative_url }}">Open activity</a>
    </div>
  </div>
  <div class="card">
    <h3>Section 5</h3>
    <p>CLAIRE, agreement-based response matrices, and latent evaluation of clustering models.</p>
    <div class="button-row">
      <a class="button" href="{{ '/section-5/' | relative_url }}">Open section</a>
      <a class="button secondary" href="{{ '/section-5-activity/' | relative_url }}">Open activity</a>
    </div>
  </div>
</div>

## Suggested Rhythm

A more realistic way to run this workshop in a `3-hour` slot is to group the material into three larger blocks:

1. `Section 1` on its own: supervised evaluation and example difficulty.
2. `Sections 2 and 3` together: binary IRT first, then Beta4-IRT as the bounded-response extension.
3. `Sections 4 and 5` together: unsupervised evaluation first, then CLAIRE as the agreement-based latent framework.

For each block, keep the same classroom cadence:

- `15 minutes` of theory
- `15 minutes` of guided hands-on explanation
- `30 minutes` of participant activity

That gives:

- `1 hour` for Section 1
- `1 hour` for Sections 2 and 3 together
- `1 hour` for Sections 4 and 5 together

Total estimated duration: `3 hours`.

## Repository

- Main repository: [latent-ability-ml]({{ site.repo_url }})
- Roadmap notebook: [00_workshop_roadmap.ipynb]({{ site.repo_url }}/blob/main/notebooks/00_workshop_roadmap.ipynb)
- Portuguese script: [99_script_portuguese.md]({{ site.repo_url }}/blob/main/docs/text/99_script_portuguese.md)
- English script: [99_script_english.md]({{ site.repo_url }}/blob/main/docs/text/99_script_english.md)

## Guide

The workshop guide is also available through the site navigation, so participants can access the repository overview without leaving the website.

<div class="button-row">
  <a class="button secondary" href="{{ '/readme/' | relative_url }}">Open guide page</a>
</div>
