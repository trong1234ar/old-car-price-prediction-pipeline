from __future__ import annotations
import json

import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.evaluation import RegressionEvaluator
import mlflow
from pyspark.ml import PipelineModel
import mlflow

from configs.config import load_config
from src.scripts.utils import (
    set_up_mlflow,
    load_json,
    save_json,
    get_model_version_by_run_id,
)
from src.logger.logger import get_logger



def run():
    logger = get_logger("model_eval", "INFO", "./log/model_eval.log")
    config = load_config()
    spark = SparkSession.builder.getOrCreate()
    ###-----------------------------------------------
    client = set_up_mlflow(config)
    registered_model_name = config["registry"]["registered_ml_pipeline_name"]
    ###-----------------------------------------------
    run_ids = load_json(config["registry"]["artifact"]["run_id"])

    all_metrics = evaluate_models(spark, config, logger, run_ids)
    logger.info("All models evaluated and metrics calculated")

    update_metrics_to_mlflow(all_metrics, logger)
    logger.info("All metrics added to original training runs")
    
    # Find and promote the best model to candidate
    candidate = find_best_model(client, registered_model_name, all_metrics)
    
    # Save candidate to json
    save_json(candidate, config["registry"]["artifact"]["candidate"])
    logger.info(f"Best model identified: {candidate}")
    
def evaluate_models(spark, config, logger, run_ids):
    """Evaluate all models using PySpark."""
    all_metrics = {}
    for name, run_info in run_ids.items():
        logger.info(f"Evaluating model: {name}")
        run_id, artifact_name = run_info["run_id"], run_info["artifact_name"]
        try:
            logged_pipeline = f'runs:/{run_id}/{artifact_name}'
            pipeline = mlflow.pyfunc.load_model(logged_pipeline)
            # Make predictions
            test_data = spark.read.parquet(config["ml_pipeline"]["data"]["test"])
            prediction = pipeline.predict(test_data)
            prediction = prediction.withColumn("prediction", F.col("prediction").cast("float"))
            # Calculate metrics
            metrics = calculate_comprehensive_metrics(prediction)
            all_metrics[name] = {
                "metrics": metrics,
                "run_id": run_id,
                "artifact_name": artifact_name
            }
        except Exception as e:
            logger.error(f"Error evaluating model {name}: {str(e)}")
            continue
            
    return all_metrics

def calculate_comprehensive_metrics(predictions):
    """Calculate comprehensive evaluation metrics for regression models using PySpark."""
    evaluator_rmse = RegressionEvaluator(
        labelCol="price", predictionCol="prediction", metricName="rmse"
    )
    evaluator_mae = RegressionEvaluator(
        labelCol="price", predictionCol="prediction", metricName="mae"
    )
    evaluator_r2 = RegressionEvaluator(
        labelCol="price", predictionCol="prediction", metricName="r2"
    )

    # Calculate metrics
    metrics = {
        "rmse": float(evaluator_rmse.evaluate(predictions)),
        "mae": float(evaluator_mae.evaluate(predictions)),
        "r2": float(evaluator_r2.evaluate(predictions))
    }

    # Calculate additional metrics using pandas for simplicity
    pdf = predictions.select("price", "prediction").toPandas()
    y_true = pdf["price"]
    y_pred = pdf["prediction"]

    metrics.update({
        "mse": float(np.mean((y_true - y_pred) ** 2)),
        "mape": float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100),
        "accuracy_within_5_percent": float(np.mean(np.abs((y_true - y_pred) / y_true) <= 0.05)),
        "accuracy_within_10_percent": float(np.mean(np.abs((y_true - y_pred) / y_true) <= 0.1))
    })
    
    return metrics



def update_metrics_to_mlflow(all_metrics, logger):
    """Update metrics to MLflow runs."""
    for name, info in all_metrics.items():
        try:
            with mlflow.start_run(run_id=info["run_id"]):
                for metric_name, value in info["metrics"].items():
                    mlflow.log_metric(f"eval_{metric_name}", value)
        except Exception as e:
            logger.error(f"Error updating metrics for {name}: {str(e)}")

def find_best_model(client, registered_model_name, all_metrics):
    """Find the best model based on accuracy within 10%."""
    if not all_metrics:
        raise ValueError("No models were successfully evaluated")
        
    best_model = min(
        all_metrics.items(),
        key=lambda x: x[1]["metrics"]["mae"]
    ) 
    best_version = get_model_version_by_run_id(client, registered_model_name, best_model[1]["run_id"])
    return {
        "model_name": best_model[0],
        "run_id": best_model[1]["run_id"],
        "version": best_version.version,
        "artifact_name": best_model[1]["artifact_name"],
        "mae": best_model[1]["metrics"]["mae"],
        "r2": best_model[1]["metrics"]["r2"]
    }

if __name__ == "__main__":
    run()