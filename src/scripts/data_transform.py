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
from src.scripts.utils import init_spark


def run():
    logger = get_logger("transform", "INFO", "./log/data_transform.log")

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
                    .withColumn("published_date", F.try_to_timestamp(F.col("published_date"), F.lit("d/MM/yyyy"))) \
                    .withColumn("updated_at", F.try_to_timestamp(F.col("updated_at"))) \
                    .withColumn("deleted_at", F.try_to_timestamp(F.col("deleted_at"))) \
                    .withColumn("district", split_address_func(F.col("address"))) \
                    .withColumn("year", F.col("year").try_cast("int")) \
                    .withColumn("seats", F.floor(F.col('seats').try_cast("double")).try_cast("int")) \
                    .withColumn("doors", F.floor(F.col('doors').try_cast("double")).try_cast("int")) \
                    .withColumn("kilometers", F.col("kilometers").try_cast("long")) \
                    .withColumn("price", F.col("price").try_cast("long"))
    for column in transformed_df.dtypes:
        if column[1] == 'string':  # Check if column is of string type
            transformed_df = transformed_df.withColumn(column[0], 
                F.when(F.col(column[0]) == "-", F.lit(None))
                .otherwise(F.col(column[0]))
            )
    transformed_df = transformed_df.dropDuplicates(["id"])

    return transformed_df

def split_address_udf():
    """Create a UDF to extract district from address"""
    def split_address(address):
        districts = ["Hoàng Mai","Đông Anh","Hà Đông","Đống Đa","Sóc Sơn",
                    "Chương Mỹ","Long Biên","Ba Vì","Hai Bà Trưng","Cầu Giấy",
                    "Bắc Từ Liêm","Thanh Xuân","Gia Lâm","Thanh Trì","Nam Từ Liêm",
                    "Thường Tín","Hoài Đức","Mê Linh","Phú Xuyên","Thanh Oai",
                    "Ba Đình","Thạch Thất","Ứng Hòa","Mỹ Đức","Quốc Oai",
                    "Phúc Thọ","Đan Phượng","Tây Hồ","Sơn Tây","Hoàn Kiếm"]

        if address is None:
            return None
        address = str(address)
        for district in districts:
            if district.lower() in address.lower():
                return district
        return None
    return F.udf(split_address, StringType())


if __name__ == "__main__":
    run()

# fix transform seats doors - chua check