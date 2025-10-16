# from __future__ import annotations
# import json
# import time

# import pandas as pd
# import numpy as np
# from sklearn.metrics import (
#     mean_absolute_error, 
#     mean_squared_error, 
#     r2_score, 
#     mean_absolute_percentage_error,
#     max_error
# )
# import mlflow
# import pickle

# from configs.config import load_config
# from src.ml_pipeline.utils import (
#     set_up_mlflow,
#     load_data_and_split,
#     load_data,
#     load_json,
#     save_json,
#     get_model_by_version,
#     get_model_version_by_run_id,
# )

# def calculate_comprehensive_metrics(y_true, y_pred):
#     """Calculate comprehensive evaluation metrics for regression models."""
#     metrics = {}
    
#     # Basic metrics
#     metrics["mse"] = float(mean_squared_error(y_true, y_pred))
#     metrics["rmse"] = float(np.sqrt(mean_squared_error(y_true, y_pred)))
#     metrics["mae"] = float(mean_absolute_error(y_true, y_pred))
#     metrics["mape"] = float(mean_absolute_percentage_error(y_true, y_pred))

#     metrics["r2"] = float(r2_score(y_true, y_pred))
#     metrics["accuracy_within_5_percent"] = float(
#         np.mean(np.abs((y_true - y_pred) / y_true) <= 0.05)
#     )
#     metrics["accuracy_within_10_percent"] = float(
#         np.mean(np.abs((y_true - y_pred) / y_true) <= 0.1)
#     )
    
#     return metrics



# def evaluate(config, client, model_registry_name, run_ids):
#     X_test, y_test = load_data_and_split(config["preprocesser"]["test"])
#     all_metrics = {}
    
#     if run_ids:
#         models_to_evaluate = run_ids.items()
#     else:
#         raise ValueError("run_ids is required")
    
#     for name, run_id in models_to_evaluate:
#         print(f"\n=== Evaluating {name} ===")
#         model_version = get_model_version_by_run_id(client, model_registry_name, run_id)
#         model = get_model_by_version(model_registry_name, model_version.version)
#         preds = model.predict(X_test)
#         metrics = calculate_comprehensive_metrics(y_test, preds)
        
#         all_metrics[name] = metrics
              
#     return all_metrics

# def update_all_metrics_to_mlflow(config, all_metrics, run_ids):
#     # Log evaluation metrics to original training runs
#     train = load_data(config["preprocesser"]["train"])
#     train_dataset = mlflow.data.from_pandas(train, name="training_data")
    
#     for name, metrics in all_metrics.items():
#         training_run_id = run_ids[name]
        
#         with mlflow.start_run(run_id=training_run_id):
#             for metric_name, value in metrics.items():
#                 mlflow.log_metric(key=f"eval_{metric_name}", value=value, dataset=train_dataset)
#             print(f"[evaluate_model] Added evaluation metrics to training run: {training_run_id}")

# def find_candidate_model(model_registry_name, all_metrics, run_ids):
#     best_model_name = max(all_metrics.keys(), key=lambda x: all_metrics[x]["accuracy_within_10_percent"])
#     best_version = get_model_version_by_run_id(model_registry_name, run_ids[best_model_name])

#     return {"name": best_model_name, "version": best_version.version, "run_id": run_ids[best_model_name]}

# def run():
#     config = load_config()
#     model_registry_name = config["registry"]["registered_model_name"]
#     run_ids = load_json(config["models"]["artifact"]["run_id"])
#     client = set_up_mlflow(config)

#     all_metrics = evaluate(config, client, model_registry_name, run_ids)
#     print("[evaluate_model] All models evaluated and metrics added to original training runs")
    
#     update_all_metrics_to_mlflow(config, all_metrics, run_ids)
#     print("[update_all_metrics_to_mlflow] All metrics added to original training runs")
    
#     # Find and promote the best model to candidate
#     candidate = find_candidate_model(model_registry_name, all_metrics, run_ids)
#     save_json(candidate, config["models"]["artifact"]["candidate"])
#     print(f"[found_candidate_model] Best model: {candidate}")

# if __name__ == "__main__":
#     run()