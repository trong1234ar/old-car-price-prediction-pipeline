# from __future__ import annotations
# import os
# import json

# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
# # from sklearn.svm import SVR
# # from sklearn.metrics import mean_absolute_error, r2_score
# # import xgboost as xgb
# # import lightgbm as lgb
# import mlflow
# import mlflow.sklearn

# from configs.config import load_config

# def load_data_train(config):
#     return pd.read_parquet(config["data"]["warehouse"])

# def load_models(config):
#     models = {
#         config["models"]["model"]["random_forest"]["name"]: RandomForestRegressor(
#             n_estimators=200,
#             max_depth=None,
#             random_state=42,
#             n_jobs=-1,
#         ),
#         config["models"]["model"]["xgboost"]["name"]: xgb.XGBRegressor(
#             n_estimators=200,
#             max_depth=None,
#             random_state=42,
#             n_jobs=-1,
#         ),
#         config["models"]["model"]["adaboost"]["name"]: AdaBoostRegressor(
#             n_estimators=200,
#             random_state=42,
#         ),
#         config["models"]["model"]["svm"]["name"]: SVR(
#             kernel='rbf',
#             C=1.0,
#             gamma='scale',
#         )
#     }
#     return models

# def set_up_mlflow(config):
#     mlflow.set_tracking_uri(config["registry"]["uri"])
#     mlflow.set_experiment(config["registry"]["experiment_name"])

# def run():
#     config = load_config()
#     set_up_mlflow(config)
    
#     data = load_data_train(config)
#     train, test = train_test_split(data, test_size=0.2, random_state=42)
#     X_train, y_train = train.drop(columns=["price"]), train["price"]
#     X_test, y_test = test.drop(columns=["price"]), test["price"]

#     # Dictionary of models
#     models = {'RF': RandomForestRegressor(
#             n_estimators=200,
#             max_depth=None,
#             random_state=42,
#             n_jobs=-1,
#         )}
    
#     # Train all models and log to MLflow
#     run_ids = {}
#     for model_name, model in models.items():
#         print(f"Training {model_name}...")
        
#         with mlflow.start_run(run_name=f"{model_name}") as run:
#             # Train the model
#             model.fit(X_train, y_train)
            
#             # Log model to MLflow
#             mlflow.sklearn.log_model(
#                 model, 
#                 name=model_name,
#                 registered_model_name=config["registry"]["registered_model_name"]
#             )
            
#             # Log model parameters
#             if hasattr(model, 'get_params'):
#                 params = model.get_params()
#                 for param_name, param_value in params.items():
#                     mlflow.log_param(param_name, param_value)
            
#             # Store run ID for later use
#             run_ids[model_name] = run.info.run_id
            
#             print(f"[train_model] {model_name} model logged to MLflow with run_id: {run.info.run_id}")
    
#     print(f"[train_model] All {len(run_ids)} models trained and logged to MLflow successfully")
    
#     # with open(config["models"]["artifact"]["run_id"], "w") as f:
#     #     json.dump(run_ids, f)
#     # print(f"[save_run_ids] Run IDs saved to {config['models']['artifact']['run_id']}")

    
# if __name__ == "__main__":
#     run()
