# Comment Category Prediction Challenge (Kaggle)

Machine Learning Practice project, IIT Madras Diploma in Data Science. Community prediction competition on Kaggle: predict the category assigned to each user comment (Neutral, Toxic, Threat, Hate) from the comment text and its metadata.

## Approach

- **Text features:** TF-IDF on word n-grams (1 to 2) and character n-grams (3 to 5) to handle misspellings and toxic text variations.
- **Tabular features:** upvotes, downvotes, identity-reference indicators, and custom features such as comment length, punctuation rate and engagement score.
- **Expert models (Stratified 5-fold cross-validation, out-of-fold predictions):**
  - Logistic Regression on the sparse TF-IDF text features
  - LightGBM on the dense metadata and identity features
  - Multinomial Naive Bayes for frequency diversity
- **Meta-model:** a tuned Multi-Layer Perceptron stacker that learns how to weight each expert.
- **Evaluation:** macro F1, per-class classification report and normalized confusion matrix.

## Result

The stacked ensemble reached the competition cutoff of 0.80+ macro F1 and generalized better than simple averaging of the models.

## Iterations

1. Logistic Regression baseline on word TF-IDF
2. Added engagement metadata and custom features
3. Added LightGBM and character n-grams
4. Simple averaging of models
5. Final: 5-fold out-of-fold stacking with an MLP meta-learner

## Files

| File | Purpose |
|---|---|
| `23ds2000055-notebook-t12026.ipynb` | Full notebook: data load, EDA, modelling, submission, results |

The competition data (`train.csv`, `test.csv`) is not included, as it is subject to the competition rules. It is available to participants on the Kaggle competition page.

Tools: Python, pandas, scikit-learn, LightGBM, SciPy, matplotlib, seaborn.
