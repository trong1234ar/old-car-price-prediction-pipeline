
import json
import os

from pyspark.sql import SparkSession
from mlflow.models.signature import infer_signature
import findspark
import mlflow
from pyspark.sql.types import StringType
import pyspark.sql.functions as F

from configs.config import load_config
from src.logger.logger import get_logger
from src.scripts.utils import set_up_mlflow, init_spark


def run():
    logger = get_logger("ml_pipeline", "INFO", "./log/model_build.log")
    config = load_config()
    spark = init_spark()
    client = set_up_mlflow(config)
    models_to_test = {"random_forest": "./src/wrapper/rf_wrapper.py",
                    # "xgboost": "./src/wrapper/xgb_wrapper.py",
                    "adaboost": "./src/wrapper/adaboost_wrapper.py",
                    "linear": "./src/wrapper/linear_wrapper.py",
                    }
    run_ids = {}

    # Initialize Spark for data loading
    data = spark.read.parquet(config["data"]["warehouse"])
    train, test = data.randomSplit([0.8, 0.2], seed=38)
    data = data.withColumn('seats', F.when(F.col('seats') == 0, 4).otherwise(F.col('seats')))
    data = data.withColumn('doors', F.when(F.col('doors') == 0, 4).otherwise(F.col('doors')))

    # Apply filters
    data = data.filter(
        (F.col('price') < 1e11) & 
        (F.col('kilometers') < 5e5) & 
        (F.col('year') >= 2010) & 
        (F.col('seats') <= 7)
    )

    col_to_drop = ["id", 'href', 'status', 'address', 'updated_at', 'published_date', 'deleted_at', "district"]
    for col in col_to_drop:
        try:
            train = train.drop(col)
        except:
            pass
        try:
            test = test.drop(col)
        except:
            pass


    train = train.withColumn("doors", train["doors"].cast(StringType())) \
                 .withColumn("seats", train["seats"].cast(StringType()))
    test = test.withColumn("doors", test["doors"].cast(StringType())) \
               .withColumn("seats", test["seats"].cast(StringType()))
    train.write.mode("overwrite").parquet(config['ml_pipeline']["data"]["train"])
    test.write.mode("overwrite").parquet(config['ml_pipeline']["data"]["test"])

    for model_name, model_path in models_to_test.items():
        try:
            with mlflow.start_run(run_name=f"{model_name}_pipeline"):
                # Then log the fitted model
                artifact_name=config['registry']['artifact_name']
                registered_model_name=config['registry']['registered_ml_pipeline_name']
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


if __name__ == "__main__":
    run()
