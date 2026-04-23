---
layout: default
title: Section 1
eyebrow: Supervised Evaluation
lead: Before latent-variable modeling, we begin with a familiar setting and ask which examples remain genuinely hard even when labels are available.
permalink: /section-1/
---

<div class="button-row">
  <a class="button" href="{{ site.repo_url }}/blob/main/notebooks/01_00_supervised_evaluation_toy_problems.ipynb">Open guided notebook</a>
  <a class="button secondary" href="{{ '/section-1-activity/' | relative_url }}">Go to activity</a>
</div>

## Supervised evaluation and example difficulty

The workshop opens in the most comfortable possible setting: we have labels, we have familiar supervised models, and we have the usual summary metrics that everyone already knows how to read. That is deliberate. The first section is not trying to surprise the audience with a new model. It is trying to change the habit of reading evaluation.

In many machine-learning workflows, a table of average scores is treated as the end of the discussion. If one model achieves the highest accuracy or the highest F1 score, the analysis often stops there. But average scores describe what happened after everything has already been pooled together. They do not tell us whether the mistakes are concentrated in one narrow region, whether two models disagree on the same examples, or whether a few particularly ambiguous examples are doing most of the analytical work.

That is the intellectual shift of this opening section: even in a supervised setting, evaluation becomes more interesting when we ask not only *which model did better on average?* but also *which examples remain difficult, and why?*

<div class="notice">
  The goal of this section is to establish a baseline intuition that will be used throughout the workshop: difficulty is often local. A model can look strong globally and still hesitate repeatedly in the same small region of the data.
</div>

## A small dataset makes the geometry visible

We begin with a compact two-dimensional classification problem so that the audience can read the geometry directly before looking at any metrics. That matters pedagogically because the visual structure comes first: some parts of the space are clean and stable, while others sit near the class frontier and invite uncertainty.

<figure>
  <img src="{{ '/assets/section-1-supervised.svg' | relative_url }}" alt="Toy supervised classification problem with two classes." />
  <figcaption>A simple supervised setting is enough to show that some regions are clean and others are genuinely ambiguous.</figcaption>
</figure>

The figure is not just decorative. It immediately suggests a hypothesis: if two classes overlap or come close in a narrow band of the feature space, that is where the interesting evaluation story should live. Far from the boundary, many models will behave similarly. Near the boundary, small differences in inductive bias, regularization, or local neighborhood structure can produce visibly different decisions.

That is why the section starts with a geometry the room can see. Before we ask the models what is hard, we let the data suggest where difficulty is likely to arise.

## A metrics table is still useful, but it is not enough

The guided notebook compares a small pool of classifiers on the same dataset.

| Model | Accuracy | Balanced Accuracy | F1 | Mean Difficulty Proxy |
| --- | ---: | ---: | ---: | ---: |
| Knn | 0.990 | 0.988 | 0.988 | 0.037 |
| Logistic Regression | 0.990 | 0.988 | 0.988 | 0.093 |
| Decision Tree | 0.979 | 0.977 | 0.976 | 0.011 |

At first glance, the table suggests that the story is almost finished. Two models are extremely strong and nearly tied, while the decision tree is slightly behind. But this is exactly where the section asks the audience to slow down. If the table is read too quickly, it encourages a ranking mindset: first place, second place, third place. If it is read carefully, it raises a deeper question: how can models with nearly identical average scores still express different uncertainty profiles over the examples?

The answer is that the table compresses heterogeneous local behavior into a single line per model. Logistic regression can be cautious in one region, KNN can be more decisive there, and the tree can make harder local commitments. None of that is visible in the summary alone. The table is useful, but it is only a compression of a much richer pattern.

This is the first major lesson of the workshop. Average metrics are not wrong. They are incomplete.

## Example difficulty appears when models hesitate or disagree

The next move in the notebook is to aggregate behavior per example. Instead of asking only which model scored highest, we ask which examples stay near the decision boundary, provoke disagreement across the model pool, or repeatedly attract lower confidence.

<figure>
  <img src="{{ '/assets/section-1-supervised-difficulty.svg' | relative_url }}" alt="Example difficulty proxy and model disagreement in the toy supervised dataset." />
  <figcaption>Difficulty is local: the ambiguous examples cluster in a region of the feature space rather than being spread uniformly across the dataset.</figcaption>
</figure>

This figure is where the section becomes conceptually important. The difficult examples are not scattered uniformly across the data as if difficulty were just random noise. They concentrate. That concentration is what makes the notion analytically useful. It tells us that difficulty is not merely an afterthought attached to isolated mistakes. It is a structural property of a region.

Once the audience sees that concentration, a more mature reading of evaluation becomes possible. We no longer say only that a classifier achieved a certain score. We can say that a classifier performed well overall, but the real tension of the problem lives in a narrow zone where several examples are systematically less stable. That kind of statement is richer, more faithful to the geometry, and much closer to the kinds of questions that latent-variable models are designed to formalize.

## Why this section has to come first

The first section does not yet introduce latent ability, item difficulty, or discrimination as formal parameters. But it prepares all three ideas informally.

A strong model is one that behaves well not only on easy examples but also near the ambiguous region. A hard example is one that repeatedly attracts hesitation, disagreement, or unstable classification behavior. And an informative example is one whose response pattern reveals something meaningful about differences between models.

Those are already the ingredients of the language that comes next. IRT does not appear out of nowhere in Section 2. It arrives as a disciplined way of naming distinctions that the room has already started to notice here.

## Reading this section as a transition

By the end of the section, the audience should be ready to accept three claims.

First, evaluation should not stop at a single aggregate number. Second, local difficulty is often more revealing than global ranking alone. Third, some examples are especially valuable because they separate stronger and weaker models more clearly than others.

That is exactly the bridge into IRT. Once those claims feel natural in a supervised setting, the transition to latent ability, item difficulty, and item discrimination becomes much smoother. The next section simply turns these qualitative observations into a probabilistic language.

## Questions for Discussion

- Why is it still useful to inspect example-level difficulty even when labels are available?
- What do average metrics hide about the geometry of the problem?
- Why do ambiguity and disagreement tend to concentrate in a region rather than spread uniformly across the dataset?
- How does this prepare the transition to IRT?
