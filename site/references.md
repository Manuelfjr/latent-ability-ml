---
layout: default
title: References
eyebrow: Bibliography
lead: Selected references for the workshop, organized around item response theory, AI evaluation, Beta4-IRT, clustering evaluation, and CLAIRE.
permalink: /references/
---

This page gathers the main references behind the workshop. The list is not meant to be exhaustive. Instead, it is organized as a compact academic guide to the literature that directly supports the conceptual and practical path of the material.

## Foundational Item Response Theory

These references provide the classical psychometric background for the workshop. They are especially useful for understanding the meanings of `ability`, `difficulty`, `discrimination`, and the logic of item characteristic curves.

- Embretson, S. E., & Reise, S. P. (2000). *Item Response Theory for Psychologists*. Lawrence Erlbaum Associates.
- de Ayala, R. J. (2009). *The Theory and Practice of Item Response Theory*. Guilford Press.
- Thissen, D., & Wainer, H. (Eds.). (2001). *Test Scoring*. Lawrence Erlbaum Associates.

## Item Response Theory in Artificial Intelligence

This article is one of the main bridges between psychometrics and AI evaluation. It is a central reference for the workshop because it shows how IRT can be used to analyze machine learning classifiers at the level of individual instances rather than only through aggregate scores.

- Martínez-Plumed, F., Prudêncio, R. B. C., Martínez-Usó, A., & Hernández-Orallo, J. (2019). *Item response theory in AI: Analysing machine learning classifiers at the instance level*. *Artificial Intelligence, 271*, 18-42. DOI: [10.1016/j.artint.2018.09.004](https://doi.org/10.1016/j.artint.2018.09.004)

## Beta-Family IRT and Beta4-IRT

The workshop sections on bounded responses build on the idea that not every meaningful response is binary. The reference below is the direct paper behind the `Beta4-IRT` part of the workshop, while the software reference records the implementation used in the activities and backend.

- Ferreira-Junior, M., Reinaldo, J. T., Lima Neto, E. A., & Prudêncio, R. B. (2023). *β4-IRT: A new β3-IRT with enhanced discrimination estimation*. *arXiv preprint*. DOI: [10.48550/arXiv.2303.17731](https://doi.org/10.48550/arXiv.2303.17731)
- Ferreira Junior, M. (2025). *birt-gd* (Version 0.1.49) [Software]. PyPI. Available at: [https://pypi.org/project/birt-gd/0.1.49/](https://pypi.org/project/birt-gd/0.1.49/)
- Source code for the implementation used throughout the workshop: [https://github.com/Manuelfjr/birt-gd](https://github.com/Manuelfjr/birt-gd)

## Clustering Evaluation Background

The unsupervised part of the workshop discusses why common clustering measures are useful but limited. The references below are included because they help situate the move from classical internal or external indices toward agreement-based latent evaluation.

- Rousseeuw, P. J. (1987). *Silhouettes: A graphical aid to the interpretation and validation of cluster analysis*. *Journal of Computational and Applied Mathematics, 20*, 53-65. DOI: [10.1016/0377-0427(87)90125-7](https://doi.org/10.1016/0377-0427(87)90125-7)
- Davies, D. L., & Bouldin, D. W. (1979). *A cluster separation measure*. *IEEE Transactions on Pattern Analysis and Machine Intelligence, 1*(2), 224-227. DOI: [10.1109/TPAMI.1979.4766909](https://doi.org/10.1109/TPAMI.1979.4766909)
- Halkidi, M., Batistakis, Y., & Vazirgiannis, M. (2001). *On clustering validation techniques*. *Journal of Intelligent Information Systems, 17*, 107-145. DOI: [10.1023/A:1012801612483](https://doi.org/10.1023/A:1012801612483)

## CLAIRE and Agreement-Based Evaluation

The final section of the workshop is anchored in CLAIRE, where the central evaluative signal is no longer correctness but structured agreement across clustering models. This paper is the main research reference for the last part of the workshop.

- Ferreira-Junior, M., Lima Neto, E. A., Ferreira, M. R. P., Silva Filho, T. M., & Prudêncio, R. B. C. (2025). *CLAIRE: clustering evaluation based on item response theory and model agreement*. *Machine Learning, 114*(11), 256. DOI: [10.1007/s10994-025-06911-0](https://doi.org/10.1007/s10994-025-06911-0)

## How These References Map to the Workshop

The workshop is not organized as a literature review, but the sequence of sections follows a clear bibliographic logic:

1. the opening sections rely on classical IRT references to define the latent quantities carefully;
2. the supervised-evaluation section is connected to the AI use of IRT through Martínez-Plumed et al. (2019);
3. the bounded-response section builds directly on `β4-IRT`;
4. the clustering sections begin with classical validation measures before moving beyond them;
5. the final step reaches `CLAIRE`, where agreement-based response matrices allow latent analysis in unsupervised evaluation.

For that reason, the references above are best read not as isolated citations but as the conceptual scaffold of the workshop itself.
