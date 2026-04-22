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

The first section already showed that average model scores can hide which examples are genuinely informative. Section 2 gives that intuition a formal language. Instead of speaking only about a model score, we begin to speak about latent ability on one side and item properties on the other.

In the binary IRT setting, each response is treated as success or failure. That could be a correct answer, a solved item, or any binary outcome that distinguishes stronger and weaker respondents. The central question becomes probabilistic: given a respondent with latent ability <span class="math-inline">&theta;<sub>i</sub></span> and an item with latent parameters, what is the probability of success?

This is a conceptual shift away from flat evaluation tables. We are no longer pretending that every item is equally revealing. We are also no longer pretending that a respondent can be summarized without reference to the particular items they faced. Ability and item structure have to be read together.

<div class="notice">
  The central achievement of this section is not just learning a formula. It is learning how to read evaluation relationally: a response depends at once on who is answering and on what kind of item is being faced.
</div>

## A small item bank makes the ideas visible

The notebook begins with a tiny item bank because the geometry of the curves is easier to read when the number of items is small. In this setting, every curve is an item characteristic curve, or ICC. The horizontal axis is ability, the vertical axis is the probability of success, and the position and slope of the curve carry the interpretation.

When a curve sits farther to the right, the item is harder. A respondent needs more latent ability before the probability of success rises substantially. When the curve becomes steeper, the item has stronger discrimination. It does a better job of distinguishing those just below the relevant ability region from those just above it.

That visual language is one of the most important assets of IRT. It gives the audience a way to see evaluation as a structured map rather than a single leaderboard. Once the room can read an ICC, it can start to ask richer questions: where does an item become informative, which items separate respondents best, and which items contribute little to ranking because they are too easy, too hard, or too flat?

## The 1PL picture: difficulty changes, slope stays fixed

The 1PL model is the cleanest starting point because every item shares the same discrimination. In that case, the only thing that changes from one item to another is difficulty, so the curves keep the same shape and simply shift left or right.

<figure>
  <img src="{{ '/assets/section-2-1pl.svg' | relative_url }}" alt="1PL-style item characteristic curves with equal discrimination and different difficulties." />
  <figcaption>With discrimination fixed, difficulty determines where each ICC begins to rise.</figcaption>
</figure>

This is where the idea of item difficulty becomes visually precise. Easy items begin to rise earlier. Hard items stay low until higher ability values are reached. The 1PL picture is intentionally restrictive, but that restriction is pedagogically useful: it isolates one idea at a time.

The notebook writes this in the usual logistic form:

$$
p_{ij} = \frac{1}{1 + e^{-a_j(\theta_i - \delta_j)}}
$$

and then specializes to the 1PL intuition by fixing <span class="math-inline">a<sub>j</sub> = 1</span>. Once that happens, the curves differ only through <span class="math-inline">&delta;<sub>j</sub></span>, the item difficulty.

That simplification is powerful because it forces the audience to see what difficulty actually does. It is not a vague statement about an item being “challenging.” It is a location parameter. It tells us where the transition from low to high success probability occurs.

## The 2PL model adds discrimination

The 2PL model keeps the same basic probability structure but allows each item to have its own discrimination. That means items are no longer distinguished only by where the curve sits. They are also distinguished by how abruptly the curve rises.

<figure>
  <img src="{{ '/assets/section-2-2pl-signs.svg' | relative_url }}" alt="Binary 2PL curves comparing negative and positive discriminations." />
  <figcaption>The sign and magnitude of discrimination change how the ICC reacts to ability. Positive discrimination is the standard case; negative discrimination inverts the relationship.</figcaption>
</figure>

This is the point where IRT stops being only about difficulty and becomes a language of information. A highly discriminative item is valuable because it sharpens distinctions precisely where ranking matters. Two respondents with similar but not identical ability can receive very different probabilities on such an item. A weakly discriminative item changes too gradually and therefore separates respondents less cleanly.

Negative discrimination also appears here as an important conceptual warning. In ordinary didactic examples, we expect stronger respondents to have higher success probabilities. A negative slope signals the opposite. Even before later sections revisit this idea in more complex settings, the audience should already understand that the sign of discrimination is not a minor technical detail. It changes the very direction of the ranking logic.

## Holding difficulty fixed reveals what discrimination does

The notebook also isolates discrimination by fixing difficulty and allowing only the slope parameter to vary.

<figure>
  <img src="{{ '/assets/section-2-discrimination.svg' | relative_url }}" alt="Binary IRT curves with common difficulty and varying discrimination." />
  <figcaption>When difficulty is held constant, discrimination controls how sharply the probability changes around the transition region.</figcaption>
</figure>

This is one of the most useful visual moments of the section. If all three items become difficult at roughly the same point on the ability axis, the main difference between them is no longer *where* they change but *how informative* they are around that change. A high-discrimination item creates a sharp boundary. A low-discrimination item changes more gradually and is less decisive.

This helps the room see that item discrimination is not an abstract coefficient. It is a statement about how much evaluative resolution an item contributes near the region where respondents are being separated.

## A table of probabilities makes the curves concrete

The heatmap in the notebook turns the ICCs into a compact table of actual probabilities for a few selected ability values.

<figure>
  <img src="{{ '/assets/section-2-heatmap.svg' | relative_url }}" alt="Heatmap of binary IRT success probabilities across respondents and items." />
  <figcaption>The same ICC logic can be read numerically as success probabilities across respondents and items.</figcaption>
</figure>

This numerical view matters because it closes the gap between visual intuition and probability statements. The curves are no longer just shapes. They correspond to concrete success probabilities that vary jointly with respondent ability and item parameters. The audience can move back and forth between the graphic and the table and realize that both are expressing the same structure.

## Why this matters for the rest of the workshop

Once we move beyond a single dataset-level score, evaluation becomes a relationship between respondents and items. Ability is no longer just “who scored higher.” Difficulty is no longer just “which dataset felt hard.” Discrimination tells us whether an item actually helps to order the respondents.

That prepares the transition to the next section. Logistic ICCs are excellent for binary intuition, but many AI evaluation settings are not naturally binary. Agreement values, proportions, and bounded continuous responses require a richer model family. That is where Beta4-IRT enters the story.

In that sense, Section 2 is the conceptual spine of the workshop. It gives the language that later sections will extend, generalize, and repurpose in settings that are more realistic than simple right-or-wrong responses.

## Questions That Organize the Section

- What changes visually when only difficulty moves, and what stays fixed?
- Why does stronger discrimination make an item more informative near its transition region?
- Why is negative discrimination so important conceptually, even if it is not the standard classroom case?
- How does this section change the way we interpret difficult examples from supervised evaluation?
