# Practical Workshop Script

This file is an internal guide for **your** live practical facilitation during the workshop.

Assumption behind this script:

- your advisor handles the theoretical part;
- you handle the practical part, meaning the transition into the notebooks, the explanation of the activities, the environment reminders, and the guidance on what is expected in each task.

---

## Your Role In The Workshop

In each macro block of the workshop, your role is to:

1. receive the group after the theoretical explanation;
2. connect the theory to the practical execution;
3. quickly show where the activity happens;
4. reinforce that participants do not need to reimplement the helper functions;
5. clearly explain what is expected from each task;
6. release the group into the activity with a concrete sense of expected outcome.

Time reminder:

- you have `15 minutes` per macro section for this guided practical framing;
- this means your delivery should be objective, repeatable, and strongly task-oriented.

---

## Standard Message Before Any Activity

Use a version very close to this in every block:

> Now I will take over the practical part.  
> You can do the activity directly on the site or open it in Colab, whichever you prefer.  
> In both cases, the point is not to rebuild infrastructure from scratch: you can and should reuse the functions that were already developed in the repository.  
> The main goal here is to use those functions to interpret the results and connect the practice back to the theory that was just presented.

You can also add:

> If you are working in Colab, run the setup cell at the top first.  
> If you are working on the site, the browser notebook already includes the helpers and you can work there directly.

Short expectation-setting line:

> It is less important to write a lot of code than to show that you understood what each task is trying to reveal.

---

## General Rule Worth Repeating

You can repeat this reminder whenever you open a notebook:

- `site` and `Colab` are both valid;
- the best environment is the one in which the participant can work most comfortably;
- the project helpers exist to accelerate the analysis;
- the expected output is always a combination of:
  - working code;
  - a figure, table, or interpretable output;
  - a conceptual reading of what appeared.

Simple line worth repeating:

> If a helper function already solves the infrastructure, use the helper function.  
> Save your energy for interpretation.

---

## Block 1

### Supervised Evaluation + Binary IRT and 2PL

This is your first practical block. The theory has already shown why aggregate metrics hide local difficulty; now you bring the group into the concrete manipulation of ICC parameters.

### Goal Of Your Framing

- take the group out of abstraction and into parameter manipulation;
- show that `difficulty` changes the position of the curve;
- show that `discrimination` changes the slope and the informative power of the curve.

### Suggested Use Of The 15 Minutes

- `2 minutes`: transition from theory to practice;
- `3 minutes`: environment and helper functions;
- `7 minutes`: explain the tasks one by one;
- `3 minutes`: final checklist and release.

### Transition Script

> The idea now is to take what just appeared in the theory and make it manipulable.  
> Instead of staying only with the definitions of ability, difficulty, and discrimination, you will change those parameters and observe how the ICC responds.

### Helper Functions Worth Highlighting

Show or explicitly mention:

```python
from utils.handson import (
    binary_irt_probability,
    make_binary_item_bank,
    plot_binary_iccs,
)
```

Suggested line:

> These functions already solve the most operational part of the activity.  
> You do not need to build the curve from scratch if the goal is to compare item behavior.

### What To Say About The Environment

> Anyone who wants to work on the site can use the browser notebook normally.  
> Anyone who prefers Colab can open it there as well.  
> In both cases, these helper functions can be used directly.

### What Is Expected From Each Task

#### Task 1

> In the first task, I expect you to build a small item bank and generate the ICCs.  
> The focus here is not to invent a very sophisticated scenario; it is to produce a small, readable set of curves that can be compared visually.

Points to reinforce:

- three items are usually enough;
- choose parameter values that are different enough for the contrast to be visible.

#### Task 2

> In the second task, the idea is to isolate the effect of difficulty.  
> So I expect you to change difficulty and observe how the curve shifts along the ability axis.

Points to reinforce:

- try to keep discrimination fixed;
- the main gain here is to see that difficulty is primarily a position parameter.

#### Task 3

> In the third task, you focus on discrimination.  
> What I want to see is a comparison between flatter and steeper curves, ideally without mixing that effect with major changes in difficulty.

Points to reinforce:

- compare at least one low-discrimination item and one high-discrimination item;
- the expected reading is: the steeper the transition, the more informative the item is in that region.

### Final Release Line

> If by the end you can look at a curve and say "this changed because difficulty moved on the axis" or "this changed because discrimination made the curve steeper," then the activity has done its job.

---

## Block 2

### Beta4-IRT

Here your mission is to show that the group has moved beyond the binary case and is now working with bounded responses in `(0, 1)` without losing the latent interpretation.

### Goal Of Your Framing

- show that the workflow is now more complete;
- reinforce that interpretation remains the focus;
- prepare the group to build `pij` and read abilities, difficulties, and discriminations in the Beta4 setting.

### Suggested Use Of The 15 Minutes

- `2 minutes`: remind the group of the bridge between 2PL and Beta4;
- `3 minutes`: environment and helper functions;
- `8 minutes`: task-by-task explanation;
- `2 minutes`: success criteria.

### Transition Script

> In the previous block, we manipulated binary responses.  
> Now the question is: what changes when the response is no longer zero or one, but a bounded continuous value?  
> This activity is here to make that pipeline concrete.

### Helper Functions Worth Highlighting

```python
from utils.handson import (
    evaluate_clustering_models_on_dataset,
    get_default_clustering_models,
    make_beta4_item_bank,
    make_toy_clustering_dataset,
    plot_beta4_iccs,
)
from utils.transform import TransformPairwise
```

Suggested line:

> Here you already have functions to generate a dataset, create a model pool, build the inputs, and visualize the curves.  
> Use that to your advantage.

### What To Say About The Environment

> If your goal is to explore the helpers and understand the structure of the activity, the site already covers a lot.  
> If you prefer Colab, that is completely fine as well.  
> And if you want more comfort for the full fitting workflow, Colab is a very good choice.

### What Is Expected From Each Task

#### Task 1

> In the first task, I expect you to create a synthetic dataset with enough variability to make the latent structure interesting.  
> It should not be chaotic, but it also should not be so easy that every model behaves almost the same way.

#### Task 2

> In the second task, you train a small pool of models.  
> The important thing here is diversity: models with different inductive biases make disagreement more informative.

#### Task 3

> In the third task, you generate the matrix `pij`.  
> What I expect is that you read this matrix as the input to the latent model, with rows as models and columns as items.

Points to reinforce:

- it is not a binary matrix;
- the values should reflect bounded responses in `(0, 1)`.

#### Task 4

> In the fourth task, you fit Beta4-IRT and inspect ability, difficulty, and discrimination.  
> The point is not only to run the fit, but to compare what comes out with what you expected from the synthetic construction.

### Final Release Line

> If at the end you can say "this fit makes sense given the dataset and the model pool I created," then you are reading the activity the right way.

---

## Block 3

### Unsupervised Evaluation + CLAIRE

This is the densest practical block, because it combines:

- local difficulty in clustering;
- the transformation of agreement into a response matrix;
- the latent interpretation inside the CLAIRE workflow.

The best way to facilitate this block is to treat it as:

1. a **short practical warm-up** in the Unsupervised Evaluation activity;
2. a **main activity** in the CLAIRE activity.

### Suggested Use Of The 15 Minutes

- `5 minutes`: frame the Unsupervised Evaluation activity;
- `8 minutes`: frame the CLAIRE activity;
- `2 minutes`: closing and prioritization.

---

### Part A

## Unsupervised Evaluation

### Goal Of Your Framing

- show that the group should not stop at aggregate metrics;
- make disagreement between models visible as a local signal;
- prepare the jump into CLAIRE.

### Helper Functions Worth Highlighting

```python
from utils.handson import (
    evaluate_clustering_models_on_dataset,
    get_default_clustering_models,
    make_toy_clustering_dataset,
    plot_clustering_dataset,
    plot_clustering_instance_difficulty,
    summarize_clustering_instance_difficulty,
    summarize_clustering_results,
)
```

### Transition Script

> Here the question stops being only "which model has the best metric?"  
> and becomes "where do the models start to disagree, and which points seem genuinely hard?".

### What Is Expected From Each Task

#### Task 1

> In the first task, you create or adapt a clustering dataset.  
> I expect something that is visually interpretable, but that also contains at least some ambiguous region.

#### Task 2

> In the second task, you compare clustering models.  
> The important thing here is not only to generate a metrics table, but to keep the outputs for the later comparison at the instance level.

#### Task 3

> In the third task, you inspect difficult instances through agreement between models.  
> The expected outcome is precisely to identify where the difficulty concentrates, instead of staying only with the aggregate summary.

### Short Closing Before Moving To CLAIRE

> If you can point to a region of the space where the models disagree more strongly, then you already have the right intuition to move into CLAIRE.

---

### Part B

## CLAIRE

Here you close the reasoning of the block and turn the disagreement intuition into a full latent workflow.

### Goal Of Your Framing

- show that agreement becomes data;
- show that the response matrix is the bridge between clustering and Beta4;
- guide the group task by task without losing the conceptual thread.

### Helper Functions Worth Highlighting

```python
from utils.handson import (
    beta4_expected_response,
    build_claire_response_matrix,
    compute_claire_like_scores,
    estimate_case_statistics,
    make_toy_clustering_partitions,
)
from utils.transform import TransformPairwise
```

If the backend is available, it is also worth mentioning:

```python
from birt import Beta4
```

### What To Say About The Environment

> The site is still a valid option, but here Colab may be more comfortable for anyone who wants to run the full workflow with more freedom.  
> In any case, the activity does not ask you to build the pipeline from scratch: the helper functions already do a large part of the preparation.

### What Is Expected From Each Task

#### Task 1

> In the first task, you generate a synthetic dataset with enough variability to produce meaningful disagreement between models.

#### Task 2

> In the second task, you train a heterogeneous model pool.  
> I expect diversity of inductive biases, because CLAIRE becomes interesting precisely when the models are not near-duplicates.

#### Task 3

> In the third task, you build the CLAIRE response matrix from agreement.  
> The central point here is to understand the transformation, not only to execute the line of code.

#### Task 4

> In the fourth task, you fit Beta4-IRT on that matrix.  
> The objective is to produce the fitted object and prepare the ground for interpretation.

#### Task 5

> In the fifth task, you compare latent-aware summaries with classical clustering metrics.  
> What I want to see here is a reading of continuity: latent ability should relate to familiar metrics, but it should not collapse into just one of them.

#### Task 6

> In the sixth task, you inspect item difficulties and discriminations.  
> The expectation is to connect those values with visually ambiguous or especially informative regions of the dataset.

#### Task 7

> In the seventh task, you generate ICCs for representative items.  
> A comparison between an easy item and a difficult item is often enough to produce a strong interpretation.

#### Task 8

> In the eighth task, you choose one representative item and bring it back into the feature space.  
> This task matters because it closes the loop: the latent parameter should return to the original geometry of the problem.

### Prioritization If Time Gets Tight

If you feel the group will not get through everything, say so explicitly:

> If time gets tight, prioritize Tasks 1 to 4 to close the pipeline, then Task 6 and Task 7 for interpretation.  
> Task 8 can become an extension or a more qualitative closing step.

---

## Short Lines To Reinforce During The Activities

You can repeat these while walking around the room or answering questions:

- "You can use the helper functions; you do not need to reimplement everything."
- "Site or Colab: choose the environment that feels more comfortable."
- "Try to produce interpretation, not just execution."
- "If the figure or table appeared, ask what it is saying about difficulty, discrimination, or agreement."
- "The best answer to a task is code plus conceptual reading."

---

## Standard Closing Before Letting Them Work

A good final line for any block is:

> What I expect from you now is not a large amount of code.  
> What I expect is that each task produces evidence, and that you can explain what that evidence means.  
> Use the site or Colab, use the helper functions when it makes sense, and focus on turning output into interpretation.

---

## Executive Summary To Memorize

If you want a very short version of your role to memorize, it is this:

- theory with your advisor;
- practice with you;
- always remind them `site or Colab`;
- always remind them `you can use the helper functions`;
- always explain `what each task is trying to show`;
- always close with `interpretation > amount of code`.
