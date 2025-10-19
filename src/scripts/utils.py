import os
from typing import Dict, Any
import json

from pathlib import Path
import pandas as pd
import mlflow


# PROJECT_ROOT = Path(__file__).resolve().parents[2]
# DATA_DIR = PROJECT_ROOT / "data"
# ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
# ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


# def load_yaml(path: Path) -> Dict[str, Any]:
#     with open(path, "r", encoding="utf-8") as f:
#         return yaml.safe_load(f)


# def get_configs() -> Dict[str, Any]:
#     cfg_dir = PROJECT_ROOT / "src" / "configs"
#     return {
#         "airflow": load_yaml(cfg_dir / "airflow_config.yaml"),
#         "spark": load_yaml(cfg_dir / "spark_config.yaml"),
#         "mlflow": load_yaml(cfg_dir / "mlflow_config.yaml"),
#     }


# def ensure_dirs():
#     DATA_DIR.mkdir(parents=True, exist_ok=True)
#     (PROJECT_ROOT / "airflow_logs").mkdir(exist_ok=True)
#     (PROJECT_ROOT / "mlruns").mkdir(exist_ok=True)


# def get_mlflow_paths(cfg: Dict[str, Any]):
#     tracking_uri = cfg["mlflow"].get("tracking_uri", str(PROJECT_ROOT / "mlruns"))
#     experiment_name = cfg["mlflow"].get("experiment_name", "old-car-price-exp")
#     registered_model_name = cfg["mlflow"].get("registered_model_name", "old-car-price-model")
#     return tracking_uri, experiment_name, registered_model_name


# def get_data_paths():
#     return {
#         "ingested": DATA_DIR / "ingested.csv",
#         "train": DATA_DIR / "train.csv",
#         "test": DATA_DIR / "test.csv",
#         "local_model": ARTIFACTS_DIR / "model.pkl",
#     }

def cars_to_df(cars):
    df = pd.DataFrame([car.dict() for car in cars])
    return df

# def set_up_mlflow(config: Dict[str, Any]):
#     mlflow.set_tracking_uri(config["registry"]["uri"])
#     mlflow.set_experiment(config["registry"]["experiment_name"])


def get_model_by_version(model_registry_name, version):
    try:
        model_uri = f"models:/{model_registry_name}/{version}"
        model = load_model(model_uri)
        return model
    except Exception as e:
        print(f"[get_model_by_version] Error getting model with version: {e}")
        return None
      
def get_model_by_alias(model_registry_name, alias):
    try:
        model_uri = f"models:/{model_registry_name}@{alias}"
        model = load_model(model_uri)
        return model
    except Exception as e:
        print(f"[get_model_by_alias] Error getting model with alias: {e}")
        return None

def get_model_version_by_run_id(client, model_registry_name, run_id):
    model_versions = client.search_model_versions(f"name='{model_registry_name}'")
    model_version = None
    
    for version in model_versions:
        if version.run_id == run_id:
            model_version = version
            break
    return model_version

def get_model_version_by_alias(client, model_registry_name, alias):
    model_versions = client.search_model_versions(f"name='{model_registry_name}'")
    model_version = None
    
    for version in model_versions:
        if alias in version.aliases:
            model_version = version
            break
    return model_version

def get_metrics_by_alias(client, model_registry_name, alias):
    mv = get_model_version_by_alias(client, model_registry_name, alias)
    run_id = mv.run_id
    run = client.get_run(run_id)
    metrics = run.data.metrics
    return metrics

def set_up_mlflow(config):
    mlflow.set_tracking_uri(config["registry"]["uri"])
    mlflow.set_experiment(config["registry"]["experiment_name"])
    client = mlflow.MlflowClient()
    return client

def load_data_and_split(data_path):
    data = pd.read_csv(data_path)
    X, y = data.drop(columns=["price"]), data["price"]
    return X, y

def load_data(data_path):
    data = pd.read_csv(data_path)
    return data

def load_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def save_json(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)