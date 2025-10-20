from __future__ import annotations
import pickle
from pathlib import Path
import mlflow
import mlflow.sklearn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error, max_error
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

from configs.config import load_config
from src.scripts.utils import (
    load_json,
    get_model_by_version,
    get_model_by_alias,
    load_data_and_split,
    set_up_mlflow
)
from src.comparer.model_comparer import ModelComparer
from src.logger.logger import get_logger

def set_alias(client, model_registry_name, version, alias):
    client.set_registered_model_alias(
        name=model_registry_name,
        alias=alias,
        version=version
    )

def remove_alias(client, model_registry_name, alias):
    client.delete_registered_model_alias(model_registry_name, alias)

def get_model_by_run_id(artifact_name, run_id):
    logged_pipeline = f'runs:/{run_id}/{artifact_name}'
    model = mlflow.pyfunc.load_model(logged_pipeline)
    return model


def run():
    logger = get_logger("model_reg", "INFO", "./log/model_reg.log")
    config = load_config()
    client = set_up_mlflow(config)
    registered_model_name = config["registry"]["registered_ml_pipeline_name"]
    logger.info(f"[Set up] Completed")
    
    candidate = load_json(config["registry"]["artifact"]["candidate"])
    # set_all_staging_to_archive(client, registered_model_name) # 1
    set_alias(client, registered_model_name, candidate["version"], "Staging") # 2
    logger.info(f"Set candidate model {candidate['version']} to Staging stage")
   
    prod_model = get_model_by_alias(registered_model_name, "Production") # 4
    cand_model = get_model_by_version(registered_model_name, candidate["version"]) # 3
    logger.info(f"Get candidate model and production model")
    
    if not prod_model:
        # If no production model exists, promote candidate to production
        set_alias(client, registered_model_name, candidate["version"], "Production")
        remove_alias(client, registered_model_name, "Staging")
        logger.info(f"[run] No production model found. Candidate model {candidate['version']} has been set to Production stage")
    else:
        X_test, y_test = load_data_and_split(config["preprocesser"]["test"])
        comparer = ModelComparer()
        res = comparer.compare(prod_model, cand_model, X_test, y_test)
        if res:
            remove_alias(client, registered_model_name, "Production")
            set_alias(client, registered_model_name, candidate["version"], "Production")
            remove_alias(client, registered_model_name, "Staging")
            logger.info(f"[run] Candidate model {candidate['version']} has been set to Production stage")
        else:
            remove_alias(client, registered_model_name, "Staging")
            logger.info(f"[run] Candidate model {candidate['version']} failed to promote to Production stage")


if __name__ == "__main__":
    run()
