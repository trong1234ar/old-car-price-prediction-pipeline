
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import RegressionEvaluator
import findspark

from src.logger.logger import get_logger
from configs.config import load_config
from src.ml_pipeline.car_prediction_pipeline import CarPricePredictionPipeline

def run():
    logger = get_logger("ml_pipeline", "INFO", "./log/run_ml_pipeline.log")
    config = load_config()
    file_path = config["data"]["warehouse"]

    spark = init_spark()
    data = spark.read.parquet(file_path)
    train, test = data.randomSplit([0.8, 0.2], seed=42)

    pipeline = CarPricePredictionPipeline(target_col="price", model_name="random_forest", config=config, logger=logger)
    # pipeline.fit(train)
    # df_predict = pipeline.predict(test)

    # 1. R² (R-squared)
    r2 = RegressionEvaluator(
        labelCol="price",
        predictionCol="prediction",
        metricName="r2"
    ).evaluate(df_predict)
    # 2. RMSE (Root Mean Squared Error)
    rmse = RegressionEvaluator(
        labelCol="price",
        predictionCol="prediction",
        metricName="rmse"
    ).evaluate(df_predict)

    logger.info("Evaluation of Random Forest")
    logger.info(f"R²: {r2:.4f}")
    logger.info(f"RMSE: {rmse:.4f}")

    # Dictionary of models
    # models = load_models(config)
    
    # Train all models and log to MLflow
    model_name = 'Random Forest'
    run_ids = {}
    # for model_name, model in models.items():
    #     print(f"Training {model_name}...")
        
    with mlflow.start_run(run_name=f"{model_name}") as run:
        # Train the model
        pipeline.fit(train)
        
        # Log model to MLflow
        mlflow.sklearn.log_model(
            pipeline, 
            name=model_name,
            registered_model_name=config["registry"]["registered_model_name"]
        )
        
        # Log model parameters
        if hasattr(model, 'get_params'):
            params = model.get_params()
            for param_name, param_value in params.items():
                mlflow.log_param(param_name, param_value)
        
        # Store run ID for later use
        run_ids[model_name] = run.info.run_id
        
        print(f"[train_model] {model_name} model logged to MLflow with run_id: {run.info.run_id}")
    
    print(f"[train_model] All {len(run_ids)} models trained and logged to MLflow successfully")
    
    with open(config["models"]["artifact"]["run_id"], "w") as f:
        json.dump(run_ids, f)
    print(f"[save_run_ids] Run IDs saved to {config['models']['artifact']['run_id']}")


def init_spark():
    findspark.init()
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("CarPricePredictionPipeline") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true") \
        .config("spark.python.worker.faulthandler.enabled", "true") \
        .config("spark.sql.execution.arrow.pyspark.fallback.enabled", "true") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.memory.offHeap.enabled", "true") \
        .config("spark.memory.offHeap.size", "2g") \
        .getOrCreate()
    return spark

def set_up_mlflow(config):
    mlflow.set_tracking_uri(config["registry"]["uri"])
    mlflow.set_experiment(config["registry"]["experiment_name"])

if __name__ == "__main__":
    run()
