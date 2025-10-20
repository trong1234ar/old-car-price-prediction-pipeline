import mlflow
from fastapi import FastAPI


from configs.config import load_config
from src.scripts.utils import get_model_by_alias, init_spark
from src.scripts.data_transform import transform_data
from src.crawler.car_dto import Car
from src.logger.logger import get_logger
from src.api.utils import pydantic_to_schema

logger = get_logger("api", "INFO", "./log/fastapi.log")

def load_model(model_registry_name, alias):
    model = get_model_by_alias(model_registry_name, alias)
    return model

app = FastAPI(
    title="Old Car Price Prediction",
    description="API for predicting used car prices",
)

config = load_config()
spark = init_spark()
model = load_model(config["registry"]["registered_ml_pipeline_name"], "Production")
schema = pydantic_to_schema(Car)
logger.info(f"[load_model] Model loaded successfully")

@app.get("/")
async def home():
    return {"message": "Welcome to Old Car Price Prediction API"}

@app.post("/predict")
async def predict(car: Car):
    row = car.model_dump()
    input_df = spark.createDataFrame([row], schema=schema)
    input_df = transform_data(input_df)

    pred_df = model.predict(input_df)
    value = pred_df.first().prediction
    value = format(int(value), ",")
    return value