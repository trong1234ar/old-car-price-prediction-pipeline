import os
import sys
from typing import Dict, List, Optional
import logging

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from datetime import datetime
import mlflow
from mlflow.tracking import MlflowClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from configs.config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
config = load_config()
MODEL_NAME = config["registry"]["registered_model_name"]

# Initialize FastAPI app
app = FastAPI(
    title="Car Price Prediction API",
    description="API for predicting used car prices",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class CarFeatures(BaseModel):
    year: int = Field(..., gt=1900, lt=datetime.now().year + 1, description="Year of the car")
    mileage: float = Field(..., ge=0, description="Mileage of the car in km")
    brand: str = Field(..., min_length=2, description="Brand of the car")
    model: str = Field(..., min_length=1, description="Model of the car")
    fuel: str = Field(..., description="Fuel type of the car")
    
    @validator('fuel')
    def validate_fuel_type(cls, v):
        valid_fuels = ['gasoline', 'diesel', 'electric', 'hybrid', 'plug-in_hybrid']
        if v.lower() not in valid_fuels:
            raise ValueError(f'fuel must be one of {valid_fuels}')
        return v.lower()

class PredictionResponse(BaseModel):
    price: float = Field(..., description="Predicted price of the car")
    currency: str = "USD"
    model_version: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    model_version: Optional[str] = None
    model_stage: str = "Production"

# Global model variable
model = None

# Preprocessing function
def preprocess_input(input_data: Dict) -> pd.DataFrame:
    """
    Preprocess the input data to match the model's training format.
    This should match the preprocessing done during training.
    """
    try:
        # Create a DataFrame with the input data
        df = pd.DataFrame([input_data])
        
        # Apply any necessary transformations here
        # For example, creating derived features, handling missing values, etc.
        
        # Ensure column order matches training
        expected_columns = ['year', 'mileage', 'brand', 'model', 'fuel']
        df = df[expected_columns]
        
        return df
    except Exception as e:
        logger.error(f"Error in preprocessing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing input data: {str(e)}"
        )

def load_production_model():
    """Load the production model from MLflow Model Registry"""
    try:
        model_uri = f"models:/{MODEL_NAME}@Production"
        logger.info(f"Loading model from {model_uri}")
        model = mlflow.pyfunc.load_model(model_uri)
        logger.info(f"Successfully loaded model {MODEL_NAME} from Production")
        return model
    except Exception as e:
        logger.error(f"Error loading production model: {str(e)}")
        return None

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the model when the application starts"""
    global model
    try:
        model = load_production_model()
        if model is None:
            logger.error("Failed to load production model on startup")
    except Exception as e:
        logger.error(f"Error during model initialization: {str(e)}")

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health():
    """Health check endpoint to verify the API is running"""
    status = "ok" if model is not None else "error"
    model_version = None
    
    if model is not None:
        try:
            # Get model version from MLflow
            client = MlflowClient()
            model_version = client.get_model_version_by_alias(MODEL_NAME, "Production").version
        except Exception as e:
            logger.warning(f"Could not get model version: {str(e)}")
    
    return {
        "status": status,
        "model_version": model_version,
        "model_stage": "Production"
    }

# Prediction endpoint
@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction"]
)
async def predict(car: CarFeatures):
    """
    Predict the price of a used car based on its features.
    
    - **year**: Year of the car (e.g., 2018)
    - **mileage**: Mileage in kilometers (e.g., 45000.5)
    - **brand**: Car brand (e.g., "toyota")
    - **model**: Car model (e.g., "camry")
    - **fuel**: Fuel type (gasoline, diesel, electric, hybrid, plug-in_hybrid)
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not available. Please try again later."
        )
    
    try:
        # Convert input to dict and preprocess
        input_data = car.dict()
        
        # Preprocess the input data
        df = preprocess_input(input_data)
        
        # Make prediction
        prediction = model.predict(df)
        
        # Get model version
        client = MlflowClient()
        model_version = client.get_model_version_by_alias(MODEL_NAME, "Production").version
        
        # Return the prediction
        return {
            "price": float(prediction[0]),
            "currency": "USD",
            "model_version": model_version,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while making the prediction: {str(e)}"
        )

# Model info endpoint
@app.get("/model/info", tags=["Model"])
async def model_info():
    """Get information about the currently loaded model"""
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not available"
        )
    
    try:
        client = MlflowClient()
        model_version = client.get_model_version_by_alias(MODEL_NAME, "Production")
        
        return {
            "name": MODEL_NAME,
            "version": model_version.version,
            "stage": "Production",
            "run_id": model_version.run_id,
            "created_at": model_version.creation_timestamp.isoformat(),
            "description": model_version.description or "No description available"
        }
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve model information"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
