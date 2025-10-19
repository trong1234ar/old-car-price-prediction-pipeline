
import json
import os

from pyspark.sql import SparkSession
from mlflow.models.signature import infer_signature
import findspark
import mlflow

from configs.config import load_config
from src.logger.logger import get_logger
from src.scripts.utils import set_up_mlflow


def run():
    logger = get_logger("ml_pipeline", "INFO", "./log/train_model.log")
    config = load_config()
    spark = init_spark()
    # set_up_mlflow(config)
    models_to_test = {"random_forest": "./src/wrapper/rf_wrapper.py",
                    # "xgboost": "./src/wrapper/xgb_wrapper.py",
                    "adaboost": "./src/wrapper/adaboost_wrapper.py",
                    "linear": "./src/wrapper/linear_wrapper.py",
                    }
    run_ids = {}

    # Initialize Spark for data loading
    data = spark.read.parquet(config["data"]["warehouse"])
    sample_data = data.limit(10).toPandas()
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("test_model_train")


    for model_name, model_path in models_to_test.items():
        try:
            with mlflow.start_run(run_name=f"{model_name}_pipeline"):
                # Then log the fitted model
                artifact_name="test"
                registered_model_name="test"
                model_info = mlflow.pyfunc.log_model(
                    python_model=model_path,
                    name=artifact_name,
                    registered_model_name=registered_model_name
                )
                run_ids[model_name] = {"run_id": model_info.run_id, "artifact_name": artifact_name}
                logger.info(f"[train_model] {model_name} model logged to MLflow with run_id: {model_info.run_id}")
        except Exception as e:
            logger.warning(f"[train_model] Failed to log {model_name} model to MLflow: {str(e)}")
            continue

    with open(config['registry']["artifact"]["run_id"], "w") as f:
        json.dump(run_ids, f)
    logger.info(f"[save_run_ids] Run IDs saved to {config['registry']['artifact']['run_id']}")

def init_spark():
    findspark.init()
    spark = SparkSession.builder \
        .master("local") \
        .appName("CarPricePredictionPipeline") \
        .getOrCreate()
    return spark

def set_up_mlflow(config):
    mlflow.set_tracking_uri(config["registry"]["uri"])
    mlflow.set_experiment(config["registry"]["experiment_name"])

if __name__ == "__main__":
    run()
