import os
import sys
import json

from pyspark.sql import SparkSession
import findspark
import mlflow
from mlflow.pyfunc import PythonModel
from mlflow.models import set_model


from configs.config import load_config
from src.ml_pipeline.car_prediction_pipeline import CarPricePredictionPipeline

class RandomForestWrapper(PythonModel):
    def __init__(self):
        self.model_name="xgboost"
        self.target_col = "price"
        self.config = load_config()
        self._init_spark()
            
        # Load and prepare data
        self.train = self.spark.read.parquet(self.config["ml_pipeline"]["data"]["train"])
        self.test = self.spark.read.parquet(self.config["ml_pipeline"]["data"]["test"])
        # Initialize and train pipeline
        self.pipeline = CarPricePredictionPipeline(
            config=self.config, 
            target_col=self.target_col, 
            model_name=self.model_name
        )
        self.pipeline.fit(self.train)
    
    def _init_spark(self):
        findspark.init()
        self.spark = SparkSession.builder \
            .master("local") \
            .getOrCreate()
        
    def predict(self, model_input):
        """Make predictions"""
        return self.pipeline.predict(model_input)


set_model(RandomForestWrapper())