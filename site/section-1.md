---
layout: default
title: Section 1
eyebrow: Unsupervised Evaluation
lead: Aggregate evaluation is useful, but it can hide that some instances are consistently harder than others.
permalink: /section-1/
---

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/01_00_unsupervised_evaluation_toy_problems.ipynb">Open guided notebook</a>
  <a class="button secondary" href="{{ '/section-1-activity/' | relative_url }}">Go to activity</a>
</div>

## Unsupervised evaluation and instance difficulty

Clustering is often evaluated through aggregate metrics. This is a useful starting point, but it is not the whole story. A single score can summarize the behavior of a model over the entire dataset while hiding that some regions are trivial and others are genuinely ambiguous.

That is the central idea of this opening section. We begin with a clean clustering problem, move to a harder geometric structure, compare the aggregate metrics, and then shift the attention to the instances where model agreement starts to break down.

<div class="notice">
  The goal of this section is to make one point very clear: evaluation should not stop at a dataset-level summary when the difficulty is not uniformly distributed across the instances.
</div>

## A first visual baseline

We start with an easy toy problem. The two groups are well separated, compact, and visually stable. In this situation, the intuitive notion of a good clustering and the numerical evaluation are aligned.

<figure>
  <svg viewBox="0 0 560 300" role="img" aria-label="Easy clustering baseline" style="width:100%; border:1px solid #e7dbc7; border-radius:20px; background:#fffdfa;">
    <rect x="0" y="0" width="560" height="300" rx="20" fill="#fffdfa"></rect>
    <line x1="55" y1="250" x2="510" y2="250" stroke="#d7cebf" />
    <line x1="55" y1="40" x2="55" y2="250" stroke="#d7cebf" />
    <g fill="#ab2330" fill-opacity="0.88">
      <circle cx="132" cy="192" r="5"></circle>
      <circle cx="148" cy="205" r="5"></circle>
      <circle cx="163" cy="180" r="5"></circle>
      <circle cx="175" cy="196" r="5"></circle>
      <circle cx="154" cy="170" r="5"></circle>
      <circle cx="190" cy="187" r="5"></circle>
      <circle cx="177" cy="163" r="5"></circle>
      <circle cx="145" cy="222" r="5"></circle>
      <circle cx="167" cy="214" r="5"></circle>
      <circle cx="201" cy="205" r="5"></circle>
      <circle cx="119" cy="208" r="5"></circle>
      <circle cx="186" cy="224" r="5"></circle>
    </g>
    <g fill="#35518e" fill-opacity="0.88">
      <circle cx="360" cy="113" r="5"></circle>
      <circle cx="383" cy="99" r="5"></circle>
      <circle cx="398" cy="124" r="5"></circle>
      <circle cx="419" cy="110" r="5"></circle>
      <circle cx="376" cy="138" r="5"></circle>
      <circle cx="410" cy="90" r="5"></circle>
      <circle cx="430" cy="129" r="5"></circle>
      <circle cx="346" cy="128" r="5"></circle>
      <circle cx="441" cy="104" r="5"></circle>
      <circle cx="392" cy="76" r="5"></circle>
      <circle cx="363" cy="88" r="5"></circle>
      <circle cx="425" cy="147" r="5"></circle>
    </g>
    <text x="80" y="28" fill="#5e5548" font-size="16" font-weight="600">Easy blobs</text>
  </svg>
  <figcaption>A clean baseline: two well-separated groups with very little room for ambiguity.</figcaption>
</figure>

In a case like this, it is reasonable to expect that several clustering models will recover essentially the same partition. If the models all agree, then the evaluation should look simple as well.

## Aggregate metrics behave well on the easy problem

That expectation is confirmed by the metrics summary for the easy-blobs scenario.

| Model | ARI | Silhouette | Calinski-Harabasz | Davies-Bouldin |
| --- | ---: | ---: | ---: | ---: |
| Agglomerative | 1.000 | 0.767 | 2308.063 | 0.329 |
| K-means | 1.000 | 0.767 | 2308.063 | 0.329 |
| Spectral | 1.000 | 0.767 | 2308.063 | 0.329 |

The table is almost too clean, and that is exactly why it works as an opening example. Every metric tells the same story. The models recover the same structure, and there is no real tension between geometric intuition and numerical evaluation.

## Making the geometry harder

Now we move to a more difficult scenario. The data are no longer organized as two simple compact groups. The structure is curved, noisier, and more sensitive to the assumptions of the clustering model.

<figure>
  <svg viewBox="0 0 560 300" role="img" aria-label="Hard moons clustering problem" style="width:100%; border:1px solid #e7dbc7; border-radius:20px; background:#fffdfa;">
    <rect x="0" y="0" width="560" height="300" rx="20" fill="#fffdfa"></rect>
    <line x1="55" y1="250" x2="510" y2="250" stroke="#d7cebf" />
    <line x1="55" y1="40" x2="55" y2="250" stroke="#d7cebf" />
    <g fill="#ab2330" fill-opacity="0.88">
      <circle cx="108" cy="168" r="4.6"></circle>
      <circle cx="128" cy="148" r="4.6"></circle>
      <circle cx="150" cy="128" r="4.6"></circle>
      <circle cx="176" cy="112" r="4.6"></circle>
      <circle cx="204" cy="98" r="4.6"></circle>
      <circle cx="236" cy="88" r="4.6"></circle>
      <circle cx="268" cy="84" r="4.6"></circle>
      <circle cx="302" cy="90" r="4.6"></circle>
      <circle cx="334" cy="102" r="4.6"></circle>
      <circle cx="360" cy="118" r="4.6"></circle>
      <circle cx="382" cy="138" r="4.6"></circle>
      <circle cx="398" cy="161" r="4.6"></circle>
    </g>
    <g fill="#35518e" fill-opacity="0.88">
      <circle cx="146" cy="190" r="4.6"></circle>
      <circle cx="169" cy="212" r="4.6"></circle>
      <circle cx="194" cy="228" r="4.6"></circle>
      <circle cx="224" cy="239" r="4.6"></circle>
      <circle cx="256" cy="244" r="4.6"></circle>
      <circle cx="288" cy="238" r="4.6"></circle>
      <circle cx="316" cy="225" r="4.6"></circle>
      <circle cx="340" cy="208" r="4.6"></circle>
      <circle cx="358" cy="188" r="4.6"></circle>
      <circle cx="373" cy="166" r="4.6"></circle>
      <circle cx="265" cy="210" r="4.6"></circle>
      <circle cx="233" cy="217" r="4.6"></circle>
    </g>
    <text x="80" y="28" fill="#5e5548" font-size="16" font-weight="600">Hard moons</text>
  </svg>
  <figcaption>A harder geometric structure: global separation still exists, but local ambiguity becomes much more important.</figcaption>
</figure>

This is the first real tension of the section. A model can still produce a partition that looks globally plausible while making very different local decisions from another model.

## The table becomes more interesting

Once the geometry becomes harder, the aggregate metrics stop agreeing so easily.

| Model | ARI | Silhouette | Calinski-Harabasz | Davies-Bouldin |
| --- | ---: | ---: | ---: | ---: |
| Spectral | 0.722 | 0.398 | 299.124 | 0.930 |
| K-means | 0.235 | 0.485 | 472.211 | 0.773 |
| Agglomerative | 0.194 | 0.476 | 453.296 | 0.776 |

This table should be read slowly.

`ARI` says that spectral clustering is much closer to the teaching labels. But `silhouette`, `Calinski-Harabasz`, and `Davies-Bouldin` all paint a more favorable picture for K-means and agglomerative clustering. So the question is no longer just which model has the highest score. The more interesting question becomes: what structural property is each metric rewarding?

This is the point where aggregate evaluation starts to show its limits. The metrics are still useful, but they are no longer sufficient to explain the whole problem.

## Where are the hard instances?

The notebook answers that question by stopping at the instance level. Instead of summarizing only at the model level, it estimates difficulty through agreement across clustering models. If the models tend to assign the same instance in consistent ways, the item is easier. If the models diverge on that point, the item is harder.

For the easy-blobs case, model agreement is effectively perfect and the difficulty proxy collapses to zero. That is consistent with the first figure and the first table.

For the hard-moons case, the most difficult instances reach a difficulty proxy around `0.654`. They are not spread uniformly across the dataset. They concentrate in the region where the curved geometry is most ambiguous for the competing clustering assumptions.

<figure>
  <svg viewBox="0 0 560 300" role="img" aria-label="Instance difficulty map for the hard moons scenario" style="width:100%; border:1px solid #e7dbc7; border-radius:20px; background:#fffdfa;">
    <rect x="0" y="0" width="560" height="300" rx="20" fill="#fffdfa"></rect>
    <line x1="55" y1="250" x2="510" y2="250" stroke="#d7cebf" />
    <line x1="55" y1="40" x2="55" y2="250" stroke="#d7cebf" />
    <g fill="#e7c98c" fill-opacity="0.9">
      <circle cx="108" cy="168" r="5"></circle>
      <circle cx="128" cy="148" r="5"></circle>
      <circle cx="150" cy="128" r="5"></circle>
      <circle cx="176" cy="112" r="5"></circle>
      <circle cx="204" cy="98" r="5"></circle>
      <circle cx="236" cy="88" r="5"></circle>
      <circle cx="302" cy="90" r="5"></circle>
      <circle cx="334" cy="102" r="5"></circle>
      <circle cx="398" cy="161" r="5"></circle>
      <circle cx="146" cy="190" r="5"></circle>
      <circle cx="169" cy="212" r="5"></circle>
      <circle cx="194" cy="228" r="5"></circle>
      <circle cx="340" cy="208" r="5"></circle>
      <circle cx="358" cy="188" r="5"></circle>
      <circle cx="373" cy="166" r="5"></circle>
    </g>
    <g fill="#b63a2b" fill-opacity="0.95">
      <circle cx="256" cy="244" r="8"></circle>
      <circle cx="288" cy="238" r="8"></circle>
      <circle cx="316" cy="225" r="8"></circle>
      <circle cx="265" cy="210" r="8"></circle>
      <circle cx="233" cy="217" r="8"></circle>
      <circle cx="268" cy="84" r="8"></circle>
      <circle cx="360" cy="118" r="8"></circle>
      <circle cx="382" cy="138" r="8"></circle>
    </g>
    <text x="80" y="28" fill="#5e5548" font-size="16" font-weight="600">Agreement-based difficulty map</text>
  </svg>
  <figcaption>Darker points mark the region where agreement drops and instance difficulty rises. Difficulty is local, not uniform across the dataset.</figcaption>
</figure>

That is the conceptual step the audience should take away from this section. The problem is not merely that one model has a better score than another. The deeper issue is that some instances are structurally harder, and those hard instances are precisely where evaluation becomes more informative.

## Reading this section as a transition

By the end of the notebook, the room should already be ready for the next section. Once we accept that:

- different metrics reward different properties;
- model rankings can change across scenarios;
- some instances are systematically harder than others;

then we need a richer language than a single dataset-level score. That language is introduced next through Item Response Theory, where model ability and item difficulty become explicit parts of the evaluation framework.

## Questions for discussion

- Why do all models look identical in the easy scenario?
- Why does spectral clustering dominate on `ARI` while K-means looks stronger on `silhouette` and `Davies-Bouldin` in the hard scenario?
- Which geometric assumption is each metric implicitly rewarding?
- Why is it important to know where the hard instances are, instead of only reading the final score table?
