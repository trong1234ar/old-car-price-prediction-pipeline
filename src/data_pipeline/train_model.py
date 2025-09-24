from __future__ import annotations
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import pickle

def run():
    config = {
        "data_preprocessed": {
            "train": "data/preprocessed/train.csv",
        },
        "model": "models/model.pkl"
    }
    train = pd.read_csv(config["data_preprocessed"]["train"])
    X_train, y_train = train.drop(columns=["price"]), train["price"]

    # Save splits for evaluation script
    # X_test.assign(price=y_test).to_csv(paths["test"], index=False)

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    os.makedirs(os.path.dirname(config["model"]), exist_ok=True)
    with open(config["model"], "wb") as f:
        pickle.dump(model, f)
    # with mlflow.start_run() as run:
    #     mlflow.log_params({
    #         "model": "RandomForestRegressor",
    #         "n_estimators": model.n_estimators,
    #         "max_depth": model.max_depth,
    #         "random_state": model.random_state,
    #         "test_size": 0.2,
    #     })

    #     pipe.fit(X_train, y_train)
    #     preds = pipe.predict(X_test)
    #     mae = float(mean_absolute_error(y_test, preds))
    #     r2 = float(r2_score(y_test, preds))
    #     mlflow.log_metrics({"mae": mae, "r2": r2})

    #     # Log model
    #     mlflow.sklearn.log_model(pipe, artifact_path="model", registered_model_name=registered_model_name)

    #     print(f"[train_model] Run {run.info.run_id} - MAE={mae:.2f} R2={r2:.3f}")
if __name__ == "__main__":
    run()
