---
layout: default
title: Section 5
eyebrow: CLAIRE
lead: The final section turns agreement between clustering models into a response matrix and interprets the fitted latent quantities through CLAIRE.
permalink: /section-5/
---

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/05_00_claire.ipynb">Open guided notebook</a>
  <a class="button secondary" href="https://colab.research.google.com/github/manuelfjr/latent-ability-ml/blob/main/notebooks/05_00_claire.ipynb" target="_blank" rel="noreferrer">Open in Colab</a>
  <a class="button secondary" href="{{ '/section-5-activity/' | relative_url }}">Go to activity</a>
  <a class="button secondary" href="{{ '/section-5-extra/' | relative_url }}">Open extra analysis</a>
</div>

## Associated Notebooks

If you want to run this overview locally or in Colab, the CLAIRE section is anchored by:

- `05_00_claire.ipynb`, which contains the main guided walkthrough for the response-matrix and latent-analysis pipeline.
- `05_01_extra_negative_disc.ipynb`, which serves as the optional companion notebook for the extra analysis linked from this section.

Both notebooks can use the shared helpers from `utils/handson.py` and `utils/transform.py`.

## From unsupervised disagreement to a response matrix

The previous section established that clustering difficulty is local and that disagreement concentrates in meaningful regions of the dataset. CLAIRE turns that intuition into a response matrix. Instead of recording whether a model is correct on an item, it records how strongly that model agrees with the rest of the pool on a given instance.

This is the conceptual leap of the entire workshop. In supervised evaluation, labels tell us what correctness means. In CLAIRE, the raw material is no longer correctness but structured agreement. The dataset is seen through a collection of partitions, and the evaluation signal arises from how those partitions reinforce or contradict one another.

<div class="notice">
  The central claim of CLAIRE is that agreement itself can become data. Once the agreement matrix exists, Beta4-IRT can estimate model ability, instance difficulty, and discrimination from the structure of agreement across the pool.
</div>

## The toy problem keeps the workflow readable

The guided notebook starts from a three-cluster toy problem so that the room can read the geometry before any latent fitting happens.

<figure>
  <img src="{{ '/assets/section-3-toy-problem.svg' | relative_url }}" alt="Three-cluster toy problem used in the CLAIRE walkthrough." />
  <figcaption>The CLAIRE workflow starts with a controlled three-cluster problem so the agreement structure is easy to discuss.</figcaption>
</figure>

This choice is pedagogically important. If the geometry were too complicated from the beginning, the audience would have to learn the response-matrix construction and the latent interpretation at the same time. The toy problem prevents that overload. It keeps the workflow readable: first see the dataset, then see the partitions, then see how agreement becomes a response.

## The response matrix is built from agreement

Formally, let <span class="math-inline">P = {p<sub>ij</sub>}</span><sub>M × N</sub> denote the response matrix, with <span class="math-inline">M</span> clustering models and <span class="math-inline">N</span> instances. Each entry <span class="math-inline">p<sub>ij</sub></span> is the normalized agreement of model <span class="math-inline">i</span> on instance <span class="math-inline">j</span>. For another model <span class="math-inline">i′ ≠ i</span> and another instance <span class="math-inline">j′ ≠ j</span>, the agreement indicator is

$$
c_{i,i'}^{j,j'} = \begin{cases}
1, & \text{if models } i \text{ and } i' \text{ agree about whether instances } j \text{ and } j' \text{ belong together or apart}, \\
0, & \text{otherwise}.
\end{cases}
$$

and the CLAIRE response is

$$
p_{ij} = \frac{1}{(M-1)(N-1)} \sum_{i' \neq i} \sum_{j' \neq j} c_{i,i'}^{j,j'}.
$$

In the workshop code, that construction is carried out by `TransformPairwise` before Beta4 is fitted.

This definition matters because it makes explicit what is being preserved and what is being discarded. CLAIRE is not preserving raw partitions in full detail. It is preserving a normalized summary of how each model agrees with the rest of the pool around each instance. That is exactly why the method can connect clustering geometry to latent item analysis.

## Ability is not just another average agreement score

Once the agreement matrix is fitted with Beta4, the notebook compares the resulting latent abilities with familiar clustering metrics.

<figure>
  <img src="{{ '/assets/section-3-correlation-heatmap.svg' | relative_url }}" alt="Correlation heatmap relating latent ability to classical clustering metrics." />
  <figcaption>Latent ability relates to classical metrics, but it does not collapse to any single one of them.</figcaption>
</figure>

This is an important moment because it protects the method from being misunderstood. CLAIRE ability is not just “another average score” hidden behind latent notation. The correlations with classical metrics are real, but they do not reduce the latent quantity to any single traditional summary. That is exactly what one should hope for from a meaningful latent framework: continuity with familiar evaluation tools, but not redundancy with them.

## Difficulty and discrimination become geometric properties of the dataset

The next plot places the latent quantities back on the dataset. Instances are colored by difficulty and sized by discrimination, so the geometry becomes a latent landscape rather than a single average score.

<figure>
  <img src="{{ '/assets/section-3-difficulty-map.svg' | relative_url }}" alt="Instances colored by difficulty and sized by discrimination in the CLAIRE toy problem." />
  <figcaption>Some instances attract stable agreement, some create uncertainty, and some are especially useful for separating stronger and weaker models.</figcaption>
</figure>

This is where the workshop really closes the circle. The audience can now see that instance difficulty is not an abstraction floating in a parameter table. It is attached to the dataset itself. Some instances attract stable agreement and are therefore easy. Some create uncertainty and disagreement and are therefore difficult. Some have especially strong discrimination because they do more than create confusion: they separate stronger and weaker models in a structured way.

## The easiest and hardest instances induce different ICCs

The guided notebook closes the main CLAIRE path by comparing the response curves of the easiest and most difficult instances.

<figure>
  <img src="{{ '/assets/section-3-icc-extremes.svg' | relative_url }}" alt="ICC comparison between the easiest and most difficult instances in the CLAIRE toy problem." />
  <figcaption>The easiest and hardest instances produce markedly different response profiles, making the latent interpretation visible again at the curve level.</figcaption>
</figure>

This final comparison is important because it returns the audience to a familiar visual language. After all the machinery of partitions, pairwise agreement, and response-matrix construction, we come back to curves. The easiest and hardest instances do not merely occupy different places in a ranking. They induce different response behavior across the latent ability axis. That is the clearest sign that the latent interpretation is doing real analytical work.

## Why CLAIRE is the final section

The workshop ends here because CLAIRE depends on everything that came before. The supervised section taught the room to care about local difficulty. Binary IRT taught the language of ability, difficulty, and discrimination. Beta4 showed that bounded responses can still support that language. Unsupervised evaluation made agreement visible as a meaningful signal. CLAIRE is where those pieces finally become one workflow.

## Questions for Discussion

- Why is agreement a more interesting signal than correctness in this setting?
- What does the response matrix keep from the clustering geometry and what does it discard?
- Why is latent ability different from simply averaging agreement across items?
- What do the easiest and hardest instance ICCs tell us that a ranking table alone cannot?
