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
    get_metrics_by_alias,
    set_up_mlflow
)
from src.comparer.model_comparer import ModelComparer
from src.logger.logger import get_logger

def set_alias(client, registered_model_name, version, alias):
    client.set_registered_model_alias(
        name=registered_model_name,
        alias=alias,
        version=version
    )

def remove_alias(client, registered_model_name, alias):
    client.delete_registered_model_alias(registered_model_name, alias)

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
   
    prod_metrics = get_metrics_by_alias(client, registered_model_name, "Production", logger)
    
    if not prod_metrics:
        # If no production model exists, promote candidate to production
        set_alias(client, registered_model_name, candidate["version"], "Production")
        remove_alias(client, registered_model_name, "Staging")
        logger.info(f"[run] No production model found. Candidate model {candidate['version']} has been set to Production stage")
    else:
        logger.info(f"Get production metrics")
        
        cand_mae = candidate["mae"]
        cand_r2 = candidate["r2"]
        prod_mae = prod_metrics["eval_mae"]
        prod_r2 = prod_metrics["eval_r2"]
        res = cand_mae < prod_mae and cand_r2 > prod_r2
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
