---
layout: default
title: Extra
eyebrow: Negative Discrimination
lead: A controlled companion analysis showing how negative discrimination can emerge when the agreement structure itself is perturbed.
permalink: /section-5-extra/
---

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/05_01_extra_negative_disc.ipynb">Open extra notebook</a>
  <a class="button secondary" href="{{ '/section-5/' | relative_url }}">Back to section</a>
</div>

## Why this notebook exists

This notebook is separate on purpose. In the main CLAIRE walkthrough, Beta4-IRT is fitted on the agreement-based response matrix obtained from a pool of clustering models. That is enough to introduce the framework, but it is not enough to isolate the exact conditions under which negative discrimination can appear.

The extra analysis exists to answer a narrower question: what happens when the agreement structure itself is perturbed in a controlled way? The point is not to create another participant task. The point is to slow the story down and inspect a phenomenon that is easy to mention but hard to interpret if it only appears as a surprising parameter estimate.

<div class="notice">
  Changing the external labels is not enough to study negative discrimination in CLAIRE. The response matrix is built from agreements between model partitions, so the perturbation has to happen in the partitions themselves.
</div>

## Starting from a geometry that already admits ambiguity

The notebook begins with a noisy moons dataset. That choice is important because the geometry already contains a naturally ambiguous region near the center of the shape. In other words, the experiment does not inject complexity into an otherwise trivial problem. It starts from a structure where disagreement is already plausible.

The next step is to fit a heterogeneous pool of models. That also matters. Negative discrimination would not mean very much if every model in the pool behaved almost identically. The pool needs enough diversity that agreement and disagreement can take on a meaningful structure.

## Perturbing the partitions, not the labels

This is one of the most conceptually important points in the notebook. If the response matrix were built from supervised labels, then label perturbation might be the obvious way to create a pathological case. But CLAIRE does not work that way. Its response matrix is built from model partitions and pairwise agreement. So the perturbation has to happen in the partitions themselves.

That is what makes the notebook analytically useful. It perturbs a specific region and a specific subset of model outputs, so the resulting negative discrimination can be read as a structural consequence of altered agreement rather than as a mysterious numerical accident.

## The spatial view of the perturbed case

The notebook makes this visible by coloring instances by estimated difficulty, sizing them by the absolute magnitude of discrimination, and then explicitly marking the items whose estimated discrimination is negative.

<figure>
  <img src="{{ '/assets/section-3-negative-discrimination.svg' | relative_url }}" alt="Negative discrimination after direct partition perturbation." />
  <figcaption>The gold-outlined region marks the perturbed instances; black outlines identify items whose estimated discrimination becomes negative.</figcaption>
</figure>

This figure is useful because it keeps the discussion grounded in the dataset. Negative discrimination is not floating in parameter space by itself. It belongs to a local region of the geometry and to a specific deformation of the agreement structure. That is exactly the kind of interpretation the workshop wants to cultivate: parameters should be read back onto the data whenever possible.

## Comparing the ICCs of the most negative and most positive items

The final step in the notebook compares the item characteristic curves of the most negative and most positive items after the perturbation. This is the cleanest way to see how the ranking logic changes.

<figure>
  <img src="{{ '/assets/section-3-negative-icc.svg' | relative_url }}" alt="Comparison between the most negative and most positive item characteristic curves." />
  <figcaption>The controlled perturbation produces one item whose curve runs against the expected ranking direction while another still behaves as a strongly positive item.</figcaption>
</figure>

Once the ICCs are placed side by side, the meaning of negative discrimination becomes much easier to explain. The item is no longer helping to order stronger and weaker models in the expected direction. Instead, its response pattern has turned against the dominant ranking logic of the rest of the pool.

## Why this companion analysis matters

The value of this notebook is that it isolates a phenomenon that is often discussed too quickly. Negative discrimination is easy to mention and much harder to interpret. Here it is tied to a concrete perturbation of the agreement structure, a visible region of the dataset, and an inversion in ICC behavior.

That makes the companion analysis an important research bridge for the section. It shows that negative discrimination is not merely a strange coefficient that happened to come out of a fitted model. It can be read as the local signature of a response structure that has stopped supporting the ranking logic implied by the rest of the agreement matrix.
