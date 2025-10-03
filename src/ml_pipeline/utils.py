import json
import pandas as pd
import mlflow
from mlflow.sklearn import load_model

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