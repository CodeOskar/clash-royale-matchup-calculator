import pandas as pd
from prepare_data import create_data_frame
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss
from xgboost import XGBClassifier
import numpy as np
#import shap

DATA_FILE = 'data/extracted_battles.json'

def augment_symmetry(df):
    df_swapped = df.copy()

    cols_a = [c for c in df.columns if c.endswith("_a")]
    cols_b = [c for c in df.columns if c.endswith("_b")]

    for a, b in zip(cols_a, cols_b):
        df_swapped[a], df_swapped[b] = df[b], df[a]

    # swap diff features if you add them
    if "elixir_diff" in df.columns and "cycle_diff" in df.columns:
        df_swapped["elixir_diff"] = -df["elixir_diff"]
        df_swapped["cycle_diff"] = -df["cycle_diff"]

    # flip label
    df_swapped["label"] = 1 - df["label"]

    return pd.concat([df, df_swapped], ignore_index=True)

df = augment_symmetry(create_data_frame(DATA_FILE))
X = df.drop(columns=["label"])
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss"
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("Accuracy:", accuracy_score(y_test, y_pred))
print("ROC AUC:", roc_auc_score(y_test, y_prob))
print("Log Loss:", log_loss(y_test, y_prob))


#explainer = shap.Explainer(model)
#shap_values = explainer(X_test)

#shap.plots.bar(shap_values)