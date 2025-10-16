import re
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType
import findspark
import pandas as pd

from configs.config import load_config
from src.logger.logger import get_logger


def run():
    logger = get_logger("transform", "INFO", "./log/transform.log")

    # Initialize Spark
    spark = init_spark()
    logger.info("Initialized spark")
    # Load configuration
    config = load_config()
    input_path = config["data"]["raw"]
    output_path = config["data"]["warehouse"]
    data = get_data(spark, input_path)
    # Run the transformation
    transformed_data = transform_data(data)
    logger.info("Transformed data")
    # Save data transformed
    transformed_data.write \
        .mode("overwrite") \
        .parquet(output_path)
    logger.info(f"Saved to: {output_path}")

    spark.stop()

def init_spark():
    findspark.init()
    
    return SparkSession.builder \
        .master("local[*]") \
        .appName("CarDataTransformation") \
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

def get_data(spark, input_path):
    try:
        # schema = _get_spark_schema()
        pd_df = pd.read_csv(input_path)
        df = spark.createDataFrame(pd_df)
        
    except:
        df = spark.read.parquet(input_path)
    return df

def transform_data(data):
    
    split_address_func = split_address_udf()
    
    # Apply transformations
    transformed_df = data.withColumn("id", F.regexp_replace(F.col('id'), r'[^0-9]', '')) \
                    .withColumn("kilometers", F.regexp_replace(F.col('kilometers'), r'[^0-9]', '')) \
                    .withColumn("seats", F.regexp_replace(F.col('seats'), r'[^0-9]', '')) \
                    .withColumn("doors", F.regexp_replace(F.col('doors'), r'[^0-9]', '')) \
                    .withColumn("published_date", F.try_to_timestamp(F.col("published_date"), F.lit("d/MM/yyyy"))) \
                    .withColumn("updated_at", F.try_to_timestamp(F.col("updated_at"))) \
                    .withColumn("deleted_at", F.try_to_timestamp(F.col("deleted_at"))) \
                    .withColumn("district", split_address_func(F.col("address"))) \
                    .withColumn("year", F.col("year").cast("int")) \
                    .withColumn("seats", F.col("seats").cast("int")) \
                    .withColumn("doors", F.col("doors").cast("int")) \
                    .withColumn("kilometers", F.col("kilometers").cast("long")) \
                    .withColumn("price", F.col("price").cast("long")) \

    return transformed_df

def split_address_udf():
    """Create a UDF to extract district from address"""
    def split_address(address):
        districts = ["Ba Đình", "Cầu Giấy", "Đống Đa", "Hai Bà Trưng", 
                "Hoàn Kiếm", "Thanh Xuân", "Hoàng Mai", "Long Biên", 
                "Hà Đông", "Tây Hồ", "Nam Từ Liêm", "Bắc Từ Liêm"]

        if address is None:
            return None
        address = str(address)
        for district in districts:
            if district in address:
                return district
        return None
    return F.udf(split_address, StringType())


if __name__ == "__main__":
    run()
