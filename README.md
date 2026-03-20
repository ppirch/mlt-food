# 🍽️ Multi-Task Learning for Food Classification and Weight Estimation

> Official implementation of the paper:
> **“Multi-Task Learning Frameworks to Classify Food and Estimate Weight From a Single Image”** (IEEE)

---

## Overview

Accurate dietary monitoring is critical in healthcare, especially for elderly patients where **malnutrition risk is high**. Traditional approaches rely on manual observation, which is **labor-intensive and inefficient**.

This project proposes a **multi-task learning (MTL) framework** that jointly performs:

* **Food classification** (categorical task)
* **Food weight estimation** (regression task)

from a **single RGB image**, reducing deployment complexity compared to sequential pipelines.

Unlike traditional single-task approaches, multi-task learning enables **shared feature representation**, improving efficiency and generalization across related tasks ([Frontiers][1]).

---

## Method

### Architecture

Our framework consists of:

* Shared **CNN backbone** (ResNet family)
* Two task-specific heads:

  * Classification head (Softmax)
  * Regression head (Weight estimation)

### Model Diagram

```
             Input Image
                  │
          ┌───────▼────────┐
          │ Shared Backbone│  (ResNet50 / 101 / 152)
          └───────┬────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
  Classification Head   Regression Head
     (Food Label)        (Weight)
```

---

## Loss Function Strategy

A key challenge in MTL is **balancing multiple objectives**. We explore:

* Manual loss weighting
* Uncertainty-based weighting
* **Auxiliary task-based weighting (best)**

Multi-task loss is defined as a weighted combination of task-specific losses:

[
L = \sum_{t} w_t L_t
]

Proper weighting prevents domination of one task and improves overall performance ([Frontiers][1]).

---

## Key Findings

* MTL reduces **Mean Absolute Percentage Error (MAPE)** significantly
* Auxiliary loss weighting improves both:

  * Classification accuracy
  * Regression performance
* Scaling backbone improves results:

  * ResNet50 → ResNet101 → ResNet152

## Citation

```bibtex
@INPROCEEDINGS{10202056,
  author={Siwathammarat, Pakin and Jesadaporn, Panas and Chawachat, Jakarin},
  booktitle={2023 20th International Joint Conference on Computer Science and Software Engineering (JCSSE)}, 
  title={Multi-Task Learning Frameworks to Classify Food and Estimate Weight From a Single Image}, 
  year={2023},
  volume={},
  number={},
  pages={368-373},
  keywords={Uncertainty;Memory management;Estimation;Machine learning;Manuals;Multitasking;Task analysis;multi-task learning;image classification;regression;food estimation;weight estimation},
  doi={10.1109/JCSSE58229.2023.10202056}}
```

---

## License

MIT License
