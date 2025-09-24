from __future__ import annotations
from pathlib import Path
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn

from ..scripts.utils import get_configs, get_data_paths, get_mlflow_paths
from .preprocess import split_features_target


def run():
    config = {
        "data_preprocessed": {
            "test": "data/preprocessed/test.csv"
        },
        "model": "models/model.pkl"
    }
    test = pd.read_csv(config["data_preprocessed"]["test"])
    X_test, y_test = test.drop(columns=["price"]), test["price"]
    # tracking_uri, experiment_name, registered_model_name = get_mlflow_paths(cfg)
    tracking_uri, experiment_name, registered_model_name = "mlruns", "test", "test"
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    # Load latest model from registry
    model_uri = f"models:/{registered_model_name}/latest"
    model = mlflow.sklearn.load_model(model_uri)

    preds = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, preds))
    r2 = float(r2_score(y_test, preds))

    with mlflow.start_run(run_name="evaluation"):
        mlflow.log_metrics({"eval_mae": mae, "eval_r2": r2})

    print(f"[evaluate_model] MAE={mae:.2f} R2={r2:.3f}")


if __name__ == "__main__":
    run()
