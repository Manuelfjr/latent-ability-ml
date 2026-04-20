---
layout: default
title: Section 2
eyebrow: Binary IRT and 2PL
lead: Item Response Theory gives us a language for talking about who is strong, which items are hard, and which items truly separate respondents.
permalink: /section-2/
---

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/02_00_binary_irt_and_2pl.ipynb">Open guided notebook</a>
  <a class="button secondary" href="{{ '/section-2-activity/' | relative_url }}">Go to activity</a>
</div>

## Binary IRT as a language for evaluation

The first section ended with a simple but important tension: aggregate scores tell us something, but they do not tell us which instances are truly informative. Section 2 gives that intuition a formal language. Instead of speaking only about a model score, we begin to speak about latent ability on one side and item properties on the other.

In the binary IRT setting, each response is treated as success or failure. That could be a correct answer, a solved item, or any binary outcome that distinguishes stronger and weaker respondents. The central question becomes probabilistic: given a respondent with latent ability \(\theta_i\) and an item with latent parameters, what is the probability of success?

<div class="notice">
  The conceptual move of this section is to stop thinking of all items as equivalent. Some items are easy, some are hard, and some are far better than others at separating weaker and stronger respondents.
</div>

## A small item bank makes the ideas visible

The notebook begins with a tiny item bank because the geometry of the curves is easier to read when the number of items is small. In this setting, every curve is an item characteristic curve, or ICC. The horizontal axis is ability, the vertical axis is the probability of success, and the position and slope of the curve are what carry the interpretation.

When a curve sits farther to the right, the item is harder. A respondent needs more latent ability before the probability of success rises substantially. When the curve becomes steeper, the item has stronger discrimination. It does a better job of distinguishing those just below the relevant ability region from those just above it.

## The 1PL picture: difficulty changes, slope stays fixed

The 1PL model is the cleanest starting point because every item shares the same discrimination. In that case, the only thing that changes from one item to another is difficulty, so the curves keep the same shape and simply shift left or right.

<figure>
  <img src="{{ '/assets/section-2-1pl.svg' | relative_url }}" alt="1PL-style item characteristic curves with equal discrimination and different difficulties." />
  <figcaption>With discrimination fixed, difficulty determines where each ICC begins to rise.</figcaption>
</figure>

This is why the 1PL view is so useful pedagogically. It shows that difficulty is fundamentally about location on the ability axis. An easy item reaches high probability early. A hard item stays low until higher ability values are reached.

The notebook writes this in the usual logistic form:

$$
p_{ij} = \frac{1}{1 + e^{-a_j(\theta_i - \delta_j)}}
$$

and then specializes to the 1PL intuition by fixing <span class="math-inline">a<sub>j</sub> = 1</span>. Once that happens, the curves differ only through <span class="math-inline">&delta;<sub>j</sub></span>, the item difficulty.

## The 2PL model adds discrimination

The 2PL model keeps the same basic probability structure but allows each item to have its own discrimination. That means items are no longer distinguished only by where the curve sits. They are also distinguished by how abruptly the curve rises.

<figure>
  <img src="{{ '/assets/section-2-2pl-signs.svg' | relative_url }}" alt="Binary 2PL curves comparing negative and positive discriminations." />
  <figcaption>The sign and magnitude of discrimination change how the ICC reacts to ability. Positive discrimination is the standard case; negative discrimination inverts the relationship.</figcaption>
</figure>

This figure is especially useful because it makes the sign of discrimination visible. In the usual classroom interpretation, positive discrimination is the normal and desirable case: higher ability should correspond to higher probability of success. A negative discrimination parameter would mean the opposite, which is precisely why it is so informative when it appears. It signals an item whose response behavior runs against the expected ordering.

## Holding difficulty fixed reveals what discrimination does

The notebook also isolates discrimination by fixing difficulty and allowing only the slope parameter to vary.

<figure>
  <img src="{{ '/assets/section-2-discrimination.svg' | relative_url }}" alt="Binary IRT curves with common difficulty and varying discrimination." />
  <figcaption>When difficulty is held constant, discrimination controls how sharply the probability changes around the transition region.</figcaption>
</figure>

This is one of the most important visual moments of the section. If all three items become difficult at roughly the same point on the ability axis, then the difference between them is not where they are centered, but how informative they are around that transition. A high-discrimination item creates a sharp boundary. A low-discrimination item changes more gradually and is less decisive.

## A table of probabilities makes the curves concrete

The heatmap in the notebook turns the ICCs into a compact table of actual probabilities for a few selected ability values.

<figure>
  <img src="{{ '/assets/section-2-heatmap.svg' | relative_url }}" alt="Heatmap of binary IRT success probabilities across respondents and items." />
  <figcaption>The same ICC logic can be read numerically as success probabilities across respondents and items.</figcaption>
</figure>

What matters here is not the exact decimal in each cell, but the pattern. As ability increases, the probability of success rises for positively discriminating items. The pace of that rise depends on discrimination, and the point at which it becomes likely depends on difficulty. The heatmap is therefore not separate from the curves; it is another way of reading the same structure.

## Why this matters for the rest of the workshop

At this point, the audience has enough language to reinterpret the problem from Section 1. Once we move beyond a single dataset-level score, evaluation becomes a relationship between respondents and items. Ability is no longer just “who scored higher.” Difficulty is no longer just “which dataset felt hard.” Discrimination tells us whether an item actually helps to order the respondents.

That prepares the transition to the final section. Logistic ICCs are excellent for binary intuition, but many AI evaluation settings are not naturally binary. Agreement values, proportions, and bounded continuous responses require a richer model family. That is where Beta4-IRT enters the story, and where CLAIRE turns agreement into a latent-evaluation workflow.

## Questions That Organize the Section

- What changes visually when only difficulty moves, and what stays fixed?
- Why does stronger discrimination make an item more informative near its transition region?
- Why is negative discrimination so important conceptually, even if it is not the standard classroom case?
- How does this section change the way we interpret the hard instances from Section 1?
