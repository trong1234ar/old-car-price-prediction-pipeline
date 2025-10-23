
# Old Car Price Prediction Pipeline

An end-to-end machine learning pipeline for predicting used car prices, featuring automated data collection, model training, evaluation, and deployment.

## 🚀 Key Features

- **Automated Data Collection**: Web crawler for collecting car listings
- **ML Pipeline**: Complete workflow from data preprocessing to model serving
- **Model Management**: MLflow integration for experiment tracking and model registry
- **API Service**: FastAPI endpoint for real-time predictions
- **Orchestration**: Airflow DAGs for scheduling and monitoring

## 🏗️ Project Structure

```
old-car-price-prediction-pipeline/
├── airflow/
│   └── dags/                  # Airflow DAG definitions
│       ├── etl_pipeline.py    # ETL workflow
│       └── model_pipeline.py  # ML model training 
│
├── configs/                   # Configuration files
│   └── config.py              # Main configuration
│   └── config.yaml            # Airflow configuration
│
├── src/
│   ├── api/                  # FastAPI application
│   │   ├── main.py           # API endpoints
│   │   └── utils.py          # API utilities
│   │
│   ├── crawler/              # Web crawler components
│   │   ├── base_crawler.py   # Base crawler class
│   │   ├── car_dto.py        # Data transfer objects
│   │   └── main_crawler.py   # Crawler specific for Bonbanh.com
│   │
│   ├── ml_pipeline/          # ML pipeline components
│   │   ├── base_pipeline.py  # Base pipeline class
│   │   ├── car_prediction_pipeline.py   # Car prediction pipeline class
│   │
│   ├── comparer/             # Data and model comparison tools
│   └── logger/               # Logging configuration
│   └── scripts/              # Script files running pipeline
│
├── data/                     # Raw and processed data
├── artifacts/                # Saved models and 
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd old-car-price-prediction-pipeline
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   or
   uv pip install -e
   ```

## 🚦 Quick Start
0. **Run tools**
  - Airflow
   ```bash
   airflow standalone
   ```
  - MLflow
   ```bash
   mlflow server --host 127.0.0.1 --port 5000 --default-artifact-root ./mlruns
   ```
   - FastAPI
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```
1. **Run the ETL pipeline**
   ```bash
   python -m src.scripts.data_extract
   python -m src.scripts.data_transform
   ```

2. **Train and evaluate models**
   ```bash
   python -m src.scripts.model_build
   python -m src.scripts.model_eval
   python -m src.scripts.model_reg
   ```

3. **Start the API server**
   ```bash
   uvicorn src.api.main:app --reload
   ```

4. **Make predictions**
   ```bash
   curl -X POST "http://localhost:8000/predict" \
        -H "Content-Type: application/json" \
        -d '{"year": 2019, "mileage": 50000, "brand": "toyota", "model": "camry"}'
   ```

## 📊 Airflow DAGs

The project includes two main DAGs:

1. **ETL Pipeline**: Handles data extraction and transformation
   - Scheduled to run daily
   - Extracts car listing data from BonBanh
   - Processes and stores the cleaned data

2. **Model Pipeline**: Manages the ML workflow
   - Trains new models
   - Evaluates model performance
   - Registers models in MLflow
   - Promotes models to production if they meet criteria

## 📈 MLflow Integration

Track experiments and manage models using MLflow:
- View training metrics and parameters
- Compare model performance
- Manage model versions and stages


## 📧 Contact

mailto: trongntdseb@gmail.com