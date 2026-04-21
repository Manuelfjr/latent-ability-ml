---
layout: default
title: Section 3
eyebrow: Beta4-IRT and CLAIRE
lead: The final section moves from binary intuition to bounded responses, agreement-based matrices, and the latent-evaluation logic behind CLAIRE.
permalink: /section-3/
---

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/03_00_beta4_and_claire.ipynb">Open guided notebook</a>
  <a class="button secondary" href="{{ '/section-3-activity/' | relative_url }}">Go to activity</a>
  <a class="button secondary" href="{{ '/section-3-extra/' | relative_url }}">Open extra analysis</a>
</div>

## From binary intuition to bounded responses

The previous section built the language of ability, difficulty, and discrimination in binary Item Response Theory. This final section keeps that latent logic, but moves to the setting that motivated the research itself: responses that are no longer binary, yet still live on a bounded interval and still carry a meaningful ranking structure.

That is why Beta4-IRT appears here. It is not a decorative extension. It is the model that allows bounded responses to retain the interpretability of IRT while becoming flexible enough for agreement-based evaluation.

<div class="notice">
  The central claim of this section is that a response matrix can be built from model agreement rather than external labels. Once that matrix exists, Beta4-IRT can estimate model ability, instance difficulty, and instance discrimination from the agreement structure itself.
</div>

## The Beta4 response model

In the notebook, the observed response is written as

$$
p_{ij} \sim \mathrm{Beta}(\alpha_{ij}, \beta_{ij}),
$$

with the Beta4 parameterization

$$
\alpha_{ij} = \left(\frac{\theta_i}{\delta_j}\right)^{a_j}, \qquad
\beta_{ij} = \left(\frac{1 - \theta_i}{1 - \delta_j}\right)^{a_j}.
$$

The important idea is that ability and difficulty remain bounded in the unit interval, while discrimination still controls how abruptly the expected response changes. The ICC intuition from Section 2 is therefore preserved, but the response is no longer restricted to 0 or 1.

## Beta4 curves can reverse direction when discrimination changes sign

The notebook first visualizes Beta4 curves under different discrimination regimes. Positive discrimination produces the familiar increasing behavior. Negative discrimination flips the local ranking logic.

<figure>
  <img src="{{ '/assets/section-3-beta4-signs.svg' | relative_url }}" alt="Beta4 item characteristic curves under positive and negative discrimination." />
  <figcaption>Beta4 keeps the latent-response interpretation of IRT, but its bounded formulation allows richer curve behavior than the usual logistic view.</figcaption>
</figure>

This is the first conceptual bridge to CLAIRE. If responses are bounded proportions or agreements, the model still needs to express items that are strongly informative, weakly informative, or even locally misleading.

## Simulating a bounded response matrix before touching CLAIRE

Before moving to clustering, the notebook constructs a synthetic latent-ability experiment. Abilities <span class="math-inline">&theta;<sub>i</sub></span> are sampled from a Beta distribution, difficulties <span class="math-inline">&delta;<sub>j</sub></span> are sampled from another Beta distribution, and discriminations <span class="math-inline">a<sub>j</sub></span> are sampled from a Gaussian law. These sampled parameters are then used to generate a bounded response matrix $p_{ij}$.

In the notebook this is stated explicitly as

$$
\theta_i \sim \mathrm{Beta}(1,1), \qquad \delta_j \sim \mathrm{Beta}(1,1), \qquad a_j \sim \mathcal{N}(1, \sigma_0^2).
$$

So the synthetic experiment starts from two bounded latent quantities, ability and difficulty, both living on the unit interval, while discrimination is allowed to vary around 1 on a Normal scale. This matters because it separates three different sources of variation before any fitting happens: where models are located, where items are located, and how sharply each item reacts to that latent ordering.

This is a crucial step pedagogically. It shows that Beta4-IRT is able to recover latent quantities in a setting where the data-generating process is known. Instead of asking the room to trust the model abstractly, the notebook first checks whether the estimated parameters track the generating ones.

The first thing to inspect is the generating sample itself. In the notebook, model abilities come from a Beta law, item difficulties come from another Beta law, and discriminations come from a Gaussian distribution centered at 1. Looking at the sampled values before fitting the model helps the room separate two questions: what was generated, and what Beta4 manages to recover from the resulting response matrix.

<figure>
  <img src="{{ '/assets/section-3-sim-distributions.svg' | relative_url }}" alt="Sampled distributions of theta, delta, and a in the synthetic Beta4 experiment." />
  <figcaption>The synthetic experiment starts by sampling model ability, item difficulty, and item discrimination from the distributions declared in the notebook. These sampled values are the reference against which the fitted parameters are later compared.</figcaption>
</figure>

<div class="grid-2">
  <figure>
    <img src="{{ '/assets/section-3-sim-abilities.svg' | relative_url }}" alt="Estimated ability against the generating ability in the synthetic Beta4 simulation." />
    <figcaption>Estimated abilities align with the generating ability values, so the latent scale can be interpreted before we move to agreement-based data.</figcaption>
  </figure>
  <figure>
    <img src="{{ '/assets/section-3-sim-difficulties.svg' | relative_url }}" alt="Estimated difficulty against the generating difficulty in the synthetic Beta4 simulation." />
    <figcaption>The same recovery logic appears for difficulty: the estimates follow the true item positions rather than drifting arbitrarily.</figcaption>
  </figure>
</div>

<figure>
  <img src="{{ '/assets/section-3-sim-discriminations.svg' | relative_url }}" alt="Estimated discrimination against the generating discrimination in the synthetic Beta4 simulation." />
  <figcaption>Discrimination is the hardest parameter to read intuitively, so this recovery plot matters: Beta4 is not only estimating a bounded location, it is also recovering how informative each item is.</figcaption>
</figure>

What these three plots establish is simple but important. Beta4-IRT is not introduced only because it is mathematically elegant. It is introduced because it can recover ability, difficulty, and discrimination from bounded responses in a controlled synthetic setting. Once that is clear, we can move to the real contribution of the section: using that same machinery on model agreement.

## CLAIRE begins with a toy clustering problem, not with labels from a benchmark

The first CLAIRE example in the notebook is intentionally easy to read visually. A synthetic dataset with three clusters is generated so that the room can see immediately that different clustering models may impose different partitions over the same geometry.

<figure>
  <img src="{{ '/assets/section-3-toy-problem.svg' | relative_url }}" alt="Three-cluster toy problem used in the CLAIRE walkthrough." />
  <figcaption>The CLAIRE workflow starts with a controlled three-cluster problem so that model agreement can be inspected before moving to the latent estimation step.</figcaption>
</figure>

This is the right place to say explicitly what changes relative to a standard supervised evaluation. We are not about to score models against external labels and stop there. We are about to train a heterogeneous pool of clustering models, collect their partitions, and transform those partitions into a response matrix built from pairwise agreement.

## The response matrix is built from agreement

That transformation is the decisive move in CLAIRE. Instead of registering whether a model was correct on an item, each response records how much the model agrees with the rest of the pool on that item. The matrix is therefore no longer a correctness table in the usual sense. It is a structured agreement table.

Formally, let <span class="math-inline">P = {p<sub>ij</sub>}</span><sub>M × N</sub> denote the response matrix, with <span class="math-inline">M</span> clustering models and <span class="math-inline">N</span> instances. Each entry <span class="math-inline">p<sub>ij</sub></span> is the normalized agreement of model <span class="math-inline">i</span> on instance <span class="math-inline">j</span>. To define it, the notebook uses the same pairwise logic that appears in the paper: for another model <span class="math-inline">i′ ≠ i</span> and another instance <span class="math-inline">j′ ≠ j</span>, we write an agreement indicator

$$
c_{i,i'}^{j,j'} = \begin{cases}
1, & \text{if models } i \text{ and } i' \text{ agree about whether instances } j \text{ and } j' \text{ belong together or apart}, \\
0, & \text{otherwise}.
\end{cases}
$$

and then define

$$
p_{ij} = \frac{1}{(M-1)(N-1)} \sum_{i' \neq i} \sum_{j' \neq j} c_{i,i'}^{j,j'}.
$$

This means that every response in CLAIRE is a proportion of pairwise agreement, not a binary correctness label. In the workshop code, that exact construction is carried out by the `TransformPairwise` class before the Beta4 model is fitted.

Once this agreement matrix exists, Beta4-IRT can be fitted to it exactly as before. The interpretation then shifts naturally:

- model ability becomes the capacity to agree well on difficult instances;
- instance difficulty becomes the rarity of stable agreement on that instance;
- discrimination becomes the degree to which an instance separates stronger and weaker models.

## Ability is not just another evaluation metric

After fitting Beta4 to the agreement matrix, the notebook compares the resulting latent abilities with familiar external and internal clustering metrics. The value of this comparison is not that all metrics should collapse to the same ranking. The value is that latent ability reorganizes the metric picture.

<figure>
  <img src="{{ '/assets/section-3-correlation-heatmap.svg' | relative_url }}" alt="Correlation heatmap relating latent ability to classical clustering metrics." />
  <figcaption>Latent ability relates to classical metrics, but it does not reduce to any single one of them. It captures how a model behaves on the difficult part of the agreement landscape.</figcaption>
</figure>

A score table tells us how a model performs according to a criterion. The latent view tells us how the pool is structured, which instances matter more, and where agreement begins to separate stronger from weaker solutions.

## Difficulty and discrimination become geometric properties of the dataset

The next plot places the latent quantities back on the dataset itself. Instances are colored by difficulty and sized by discrimination, so the geometry of the problem becomes a latent landscape rather than a single average score.

<figure>
  <img src="{{ '/assets/section-3-difficulty-map.svg' | relative_url }}" alt="Instances colored by difficulty and sized by discrimination in the CLAIRE toy problem." />
  <figcaption>The latent view turns the dataset into a map: some instances attract stable agreement, some create uncertainty, and some are especially useful for separating stronger and weaker models.</figcaption>
</figure>

This is where the first two sections come back. Section 1 argued that difficulty is local. Section 2 showed how difficulty and discrimination shape an item response curve. CLAIRE now estimates those same ideas from agreement itself.

## The easiest and hardest instances induce different ICCs

The notebook closes the main CLAIRE path by comparing the expected response curves of the easiest and most difficult instances. This is a compact way to show that the latent quantities are not decorative labels attached after the fact. They imply genuinely different response behavior.

<figure>
  <img src="{{ '/assets/section-3-icc-extremes.svg' | relative_url }}" alt="ICC comparison between the easiest and most difficult instances in the CLAIRE toy problem." />
  <figcaption>The easiest and most difficult instances produce markedly different response profiles, making the latent interpretation visible again at the curve level.</figcaption>
</figure>

Once the room sees this comparison, the logic of CLAIRE becomes much easier to state clearly: the framework is not only ranking models. It is identifying which instances are easy, which ones are difficult, and which ones are genuinely diagnostic for evaluation.

## The companion notebook isolates negative discrimination

The extra notebook `03_01` exists because negative discrimination is easy to mention and much harder to interpret. There, the agreement structure is perturbed directly in a controlled region of the data so that the workshop can inspect what happens when some items begin to work against the expected ranking logic.

<figure>
  <img src="{{ '/assets/section-3-negative-discrimination.svg' | relative_url }}" alt="Negative discrimination after direct partition perturbation in the extra notebook." />
  <figcaption>By perturbing a localized region of the agreement structure, the extra notebook shows how negative discrimination can emerge as a concrete geometric phenomenon rather than as a mysterious parameter estimate.</figcaption>
</figure>

The extra page should therefore be read as analytical support for this section. The main overview establishes the workflow. The companion notebook shows what happens when that workflow is stressed in a targeted way.

## From bounded responses to latent evaluation

By the end of the section, the whole sequence should read as one continuous argument. Beta4-IRT handles bounded responses. A synthetic simulation shows that the model can recover ability, difficulty, and discrimination. CLAIRE then replaces correctness with agreement, fits Beta4 to the resulting response matrix, and interprets the fitted parameters as model ability and item-level structure.

That is the research bridge this workshop is building: from classical evaluation tables to a latent evaluation framework in which agreement itself becomes data.

## Questions That Organize the Section

- Why does it matter to verify Beta4 on a synthetic response matrix before using it on agreement data?
- What changes when the response matrix is built from agreement rather than from correctness?
- Why is latent ability different from simply averaging agreement across items?
- What do the easiest and hardest instance ICCs tell us that a ranking table alone cannot?
- Why is negative discrimination important enough to deserve a companion notebook of its own?
