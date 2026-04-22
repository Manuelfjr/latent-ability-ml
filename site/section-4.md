---
layout: default
title: Section 4
eyebrow: Unsupervised Evaluation
lead: Aggregate evaluation is useful, but it can hide that some clustering instances are consistently harder than others.
permalink: /section-4/
---

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/04_00_unsupervised_evaluation_toy_problems.ipynb">Open guided notebook</a>
  <a class="button secondary" href="{{ '/section-4-activity/' | relative_url }}">Go to activity</a>
</div>

## Unsupervised evaluation and instance difficulty

Clustering is often evaluated through aggregate metrics. This is a useful starting point, but it is not the whole story. A single score can summarize the behavior of a model over the entire dataset while hiding that some regions are trivial and others are genuinely ambiguous.

That is the central idea of this section. We begin with a clean clustering problem, move to a harder geometric structure, compare the aggregate metrics, and then shift the attention to the instances where model agreement starts to break down. By the time we do that, the audience is no longer surprised by the move toward local structure, because the earlier sections have already taught the habit of asking where difficulty lives.

<div class="notice">
  The goal of this section is to make one point very clear: evaluation should not stop at a dataset-level summary when the difficulty is not uniformly distributed across the instances.
</div>

## A first visual baseline

We start with an easy toy problem. The two groups are well separated, compact, and visually stable. In this situation, the intuitive notion of a good clustering and the numerical evaluation are aligned.

<figure>
  <img src="{{ '/assets/section-1-easy.svg' | relative_url }}" alt="Easy toy clustering problem with two clearly separated groups." />
  <figcaption>A clean baseline: two well-separated groups with very little room for ambiguity.</figcaption>
</figure>

This first figure matters because it establishes what an uncomplicated case looks like. The groups are so clean that different clustering models have little room to disagree in meaningful ways. That is exactly the kind of dataset on which average metrics are honest and sufficient. If everything is stable geometrically, a single number per model can often summarize the story without much distortion.

## Aggregate metrics behave well on the easy problem

| Model | ARI | Silhouette | Calinski-Harabasz | Davies-Bouldin |
| --- | ---: | ---: | ---: | ---: |
| Agglomerative | 1.000 | 0.767 | 2308.063 | 0.329 |
| K-means | 1.000 | 0.767 | 2308.063 | 0.329 |
| Spectral | 1.000 | 0.767 | 2308.063 | 0.329 |

This table is useful precisely because it is boring. All three methods agree, and all three metrics tell the same story. That is not a weakness. It is the correct behavior for a clean dataset. The section uses this baseline to make a stronger contrast later: when the geometry becomes more complicated, the evaluation story stops being so uniform.

## Making the geometry harder

Now we move to a more difficult scenario. The data are no longer organized as two simple compact groups. The structure is curved, noisier, and more sensitive to the assumptions of the clustering model.

<figure>
  <img src="{{ '/assets/section-1-hard.svg' | relative_url }}" alt="Harder toy clustering problem with moon-shaped groups." />
  <figcaption>A harder geometric structure: global separation still exists, but local ambiguity becomes much more important.</figcaption>
</figure>

This figure changes the whole tone of the section. The dataset is still interpretable, but now there are multiple plausible local readings. Some models are better aligned with curved structure, while others prefer compact partitions. The important point is that difficulty is no longer a vague impression. It is rooted in the geometry.

## The table becomes more interesting

| Model | ARI | Silhouette | Calinski-Harabasz | Davies-Bouldin |
| --- | ---: | ---: | ---: | ---: |
| Spectral | 0.722 | 0.398 | 299.124 | 0.930 |
| K-means | 0.235 | 0.485 | 472.211 | 0.773 |
| Agglomerative | 0.194 | 0.476 | 453.296 | 0.776 |

This is the moment when average metrics stop being enough. Different metrics reward different structural properties, so the table now becomes a site of tension rather than consensus. Spectral clustering looks best under ARI because it stays closer to the teaching labels. K-means and agglomerative clustering appear more favorable under silhouette and the other compactness-style metrics. The section deliberately slows down here, because this is where many real evaluation problems become conceptually messy.

The question is no longer just which model has the highest number. The question becomes: what structural property is each metric rewarding, and where in the dataset is that reward coming from?

## Where are the hard instances?

The notebook answers that question by estimating difficulty through agreement across clustering models. If the models treat an instance consistently, it is easier. If the models diverge on it, the instance is harder.

<figure>
  <img src="{{ '/assets/section-1-difficulty.svg' | relative_url }}" alt="Agreement-based difficulty map for the harder clustering scenario." />
  <figcaption>Difficulty is local, not uniform across the dataset.</figcaption>
</figure>

This is the conceptual center of the section. The hard instances are not spread everywhere. They are concentrated in the region where the geometry itself invites disagreement. Once that becomes visible, the earlier conflict in the metrics table is easier to understand. The metrics were not merely disagreeing abstractly; they were responding differently to a specific local structure in the dataset.

That is why the section is so important for the final CLAIRE material. It makes agreement visible as a meaningful signal in its own right. Before we ever turn agreement into a response matrix, we have already learned to see it as evidence about instance difficulty.

## Why this section now matters for CLAIRE

This section comes after Beta4 on purpose. The room already knows how latent difficulty and discrimination can be estimated from bounded responses. The unsupervised setting now supplies the geometric and agreement-based intuition that CLAIRE will turn into a response matrix in the final section.

In that sense, this section is the last conceptual bridge of the workshop. It combines the local reading habit from the supervised case, the latent language from IRT, and the bounded-response flexibility from Beta4, then hands all of that to CLAIRE in the form of agreement-based evaluation.
