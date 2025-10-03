from __future__ import annotations
import pickle
from pathlib import Path
import mlflow
import mlflow.sklearn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error, max_error
import numpy as np
import pandas as pd
from mlflow.sklearn import load_model
from typing import Dict, Tuple, Optional

from configs.config import load_config
from src.ml_pipeline.utils import (
    set_up_mlflow,
    load_json,
    get_model_by_version,
    get_model_by_alias,
    get_metrics_by_alias,
    load_data_and_split,
)
from src.comparer.model_comparer import ModelComparer

def set_alias(client, model_registry_name, version, alias):
    client.set_registered_model_alias(
        name=model_registry_name,
        alias=alias,
        version=version
    )
    print(f"[set_alias] Model {version} has been set to {alias} stage")

def remove_alias(client, model_registry_name, alias):
    client.delete_registered_model_alias(model_registry_name, alias)
    print(f"[remove_alias] Alias {alias} has been removed from model {model_registry_name}")
    
# def set_all_staging_to_archive(client, registered_model_name):
#     for v in client.search_model_versions(f"name='{registered_model_name}'"):
#         if "Staging" in v.aliases:
#             set_alias(client, registered_model_name, v.version, "Archived")
#             remove_alias(client, registered_model_name, "Staging")
#     print(f"[set_all_staging_to_archive] All models in Staging stage have been archived")

# def get_model_by_version(model_registry_name, version):
#     try:
#         model_uri = f"models:/{model_registry_name}/{version}"
#         model = load_model(model_uri)
#         return model
#     except Exception as e:
#         print(f"[get_model_by_version] Error getting model with version: {e}")
#         return None
      
# def get_model_by_alias(model_registry_name, alias):
#     try:
#         model_uri = f"models:/{model_registry_name}@{alias}"
#         model = load_model(model_uri)
#         return model
#     except Exception as e:
#         print(f"[get_model_by_alias] Error getting model with alias: {e}")
#         return None



def run():
    # Step for model registry
    # 1. Set all staging to archived
    # 2. Set candidate to staging
    # 3. Get candidate model
    # 4. Get production model
    # 5. Compare candidate and production model
    # 6. Set candidate to production
    config = load_config()
    client = set_up_mlflow(config)
    registered_model_name = config["registry"]["registered_model_name"]
    candidate = load_json(config["models"]["artifact"]["candidate"])

    # set_all_staging_to_archive(client, registered_model_name) # 1
    set_alias(client, registered_model_name, candidate["version"], "Staging") # 2

    prod_model = get_model_by_alias(registered_model_name, "Production") # 4
    cand_model = get_model_by_version(registered_model_name, candidate["version"]) # 3
    
    if not prod_model:
        # If no production model exists, promote candidate to production
        set_alias(client, registered_model_name, candidate["version"], "Production")
        remove_alias(client, registered_model_name, "Staging")
        print(f"[run] No production model found. Candidate model {candidate['version']} has been set to Production stage")
    else:
        X_test, y_test = load_data_and_split(config["preprocesser"]["test"])
        comparer = ModelComparer()
        res = comparer.compare(prod_model, cand_model, X_test, y_test)
        if res:
            remove_alias(client, registered_model_name, "Production")
            set_alias(client, registered_model_name, candidate["version"], "Production")
            remove_alias(client, registered_model_name, "Staging")
            print(f"[run] Candidate model {candidate['version']} has been set to Production stage")
        else:
            remove_alias(client, registered_model_name, "Staging")
            print(f"[run] Candidate model {candidate['version']} failed to promote to Production stage")

        

    

if __name__ == "__main__":
    run()
