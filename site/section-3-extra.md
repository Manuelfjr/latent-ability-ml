---
layout: default
title: Extra
eyebrow: Negative Discrimination
lead: A controlled companion analysis showing how negative discrimination can emerge when the agreement structure itself is perturbed.
permalink: /section-3-extra/
---

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/03_01_extra_negative_disc.ipynb">Open extra notebook</a>
  <a class="button secondary" href="{{ '/section-3/' | relative_url }}">Back to section</a>
</div>

## Why this notebook exists

This notebook is separate on purpose. In the main CLAIRE walkthrough, Beta4-IRT is fitted to an agreement-based response matrix obtained from a pool of clustering models. That is enough to introduce the framework, but it is not enough to isolate the exact conditions under which negative discrimination can appear.

The extra analysis exists to answer a narrower question: what happens when the agreement structure itself is perturbed in a controlled way? The point is not to create another participant activity. The point is to produce a clean analytical example that can be discussed in class without mixing too many moving parts.

<div class="notice">
  Changing the external labels is not enough to study negative discrimination in CLAIRE. The response matrix is built from agreements between model partitions, so the perturbation has to happen in the partitions themselves.
</div>

## Starting from a noisy geometry

The notebook begins with a noisy moons dataset. That geometry is useful because it already contains a natural ambiguous region near the center of the shape. Rather than perturbing the whole dataset, the analysis selects a subset of instances close to that center, where disagreement is already more plausible.

The next step is to fit a heterogeneous pool of models. That matters because negative discrimination is not meaningful unless the pool already contains competing structural assumptions. Once those partitions exist, the notebook identifies the strongest models in the pool and perturbs only their assignments in the ambiguous region.

This is what turns the notebook into a controlled experiment rather than a random stress test. The perturbation is targeted, local, and structurally interpretable.

## What the perturbation is meant to reveal

If the response matrix were perfectly well behaved, the most informative items would all reinforce the same ranking logic: stronger models would tend to agree more on the right instances, and weaker models would tend to disagree. Negative discrimination appears when this ordering starts to invert for a subset of items.

In other words, the item stops helping to separate stronger and weaker models in the expected direction. It begins to behave like a misleading signal.

## The spatial view of the perturbed case

The notebook makes this visible by coloring instances by estimated difficulty, sizing them by the absolute magnitude of discrimination, and then explicitly marking the items whose estimated discrimination is negative.

<figure>
  <img src="{{ '/assets/section-3-negative-discrimination.svg' | relative_url }}" alt="Negative discrimination after direct partition perturbation." />
  <figcaption>The gold-outlined region marks the perturbed instances; black outlines identify items whose estimated discrimination becomes negative.</figcaption>
</figure>

This figure is useful because it prevents the discussion from becoming too abstract. Negative discrimination is not floating in parameter space by itself. It is attached to a region of the dataset and to a very specific deformation of the agreement structure.

## Comparing the ICCs of the most negative and most positive items

The final step in the notebook compares the item characteristic curves of the most negative and most positive items after the perturbation. This is the cleanest way to see how the ordering logic changes.

<figure>
  <img src="{{ '/assets/section-3-negative-icc.svg' | relative_url }}" alt="Comparison between the most negative and most positive item characteristic curves." />
  <figcaption>The controlled perturbation produces one item whose curve runs against the expected ranking direction while another still behaves as a strongly positive item.</figcaption>
</figure>

This comparison closes the loop with the previous section. In binary IRT, negative discrimination is already conceptually important. In Beta4-IRT and CLAIRE, it becomes even more informative because it can emerge from the agreement structure itself rather than from a simple binary response pattern.

## Why this companion analysis matters

The value of this notebook is that it isolates a phenomenon that is easy to mention and much harder to interpret. Negative discrimination is often treated as a strange parameter estimate, but here it is tied to a concrete perturbation of the agreement structure, a visible region of the dataset, and a corresponding inversion in ICC behavior.

That makes the companion analysis an important research bridge for the section. It shows that negative discrimination is not merely a numerical anomaly. It can be read as the local signature of a response structure that has turned against the ranking logic implied by the rest of the pool.
