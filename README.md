
# Old Car Price Prediction

End-to-end ML project scaffold implementing the flow illustrated in the diagram:

- Airflow orchestrates ingestion → training → evaluation → model saving
- Data pipeline (scikit-learn in this scaffold, Spark-ready configs) for preprocessing, training, evaluation
- MLflow for experiment tracking and model registry
- FastAPI service for online prediction, loading the latest model from MLflow (with local fallback)

## Project Structure

```
old-car-price-prediction/
│
├── airflow_dags/
│   └── car_price_pipeline_dag.py
│
├── data/
│   └── .gitkeep
│
├── src/
│   ├── api_service/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── mlflow_loader.py
│   │   └── schemas.py
│   │
│   ├── configs/
│   │   ├── airflow_config.yaml
│   │   ├── mlflow_config.yaml
│   │   └── spark_config.yaml
│   │
│   ├── data_pipeline/
│   │   ├── __init__.py
│   │   ├── evaluate_model.py
│   │   ├── preprocess.py
│   │   ├── save_model.py
│   │   └── train_model.py
│   │
│   ├── scripts/
│   │   ├── __init__.py
│   │   ├── ingest_data.py
│   │   └── utils.py
│   │
│   └── __init__.py
│
├── artifacts/                  # created at runtime for local model pickle
├── mlruns/                     # local MLflow backend store (created at runtime)
├── airflow_logs/               # Airflow logs (created at runtime)
├── requirements.txt
└── README.md
```

Note: The pipeline is implemented with scikit-learn for simplicity. The `src/configs/spark_config.yaml` is a placeholder so you can switch to PySpark later if desired.

## Quickstart (Windows PowerShell)

1) Create a virtual environment and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

2) Generate synthetic sample data

```powershell
python -m src.scripts.ingest_data
```

3) Train and log a model to MLflow (also writes test split)

```powershell
python -m src.data_pipeline.train_model
```

4) Evaluate the latest registered model from MLflow

```powershell
python -m src.data_pipeline.evaluate_model
```

5) Save the latest model to a local pickle (API will also try MLflow first)

```powershell
python -m src.data_pipeline.save_model
```

6) Run the API service

```powershell
python -m uvicorn src.api_service.main:app --reload --host 0.0.0.0 --port 8000
```

Test a prediction:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body (@{
  year=2016; mileage=60000; brand='toyota'; fuel_type='petrol'; transmission='automatic'; owner_count=1
} | ConvertTo-Json) -ContentType 'application/json'
```

Health check:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

## MLflow UI

This project uses a local `mlruns/` folder as the MLflow backend store by default. To view runs and registered models:

```powershell
mlflow ui --backend-store-uri mlruns --host 0.0.0.0 --port 5000
```

Open http://localhost:5000 in your browser.

## Airflow DAG

The DAG `car_price_pipeline_dag` orchestrates the steps: ingest → train → evaluate → save.

Recommended lightweight local setup (PowerShell):

```powershell
# Ensure the project is on PYTHONPATH so Airflow can import src.*
$env:PYTHONPATH = "$(Get-Location)"

# Make Airflow read DAGs from the repo folder
$env:AIRFLOW__CORE__DAGS_FOLDER = "$(Get-Location)\airflow_dags"

# Initialize Airflow metadata DB
airflow db init

# Create a user (only once)
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin

# Start services (run in separate terminals)
airflow webserver -p 8080
airflow scheduler
```

Then open http://localhost:8080, find `car_price_pipeline_dag`, and trigger it.

If you prefer not to run Airflow, you can execute the same steps manually via the module commands shown in Quickstart.

## Configuration

- `src/configs/mlflow_config.yaml`: MLflow `tracking_uri`, `experiment_name`, and `registered_model_name`.
- `src/configs/airflow_config.yaml`: DAG id, schedule, and start offset.
- `src/configs/spark_config.yaml`: Placeholder for Spark settings if you switch to PySpark.

## Notes

- The API attempts to load the latest model from MLflow registry first, then falls back to a local pickle saved by `save_model.py`.
- Generated artifacts:
  - `mlruns/` for MLflow runs and registry (local store)
  - `artifacts/model.pkl` for local serving fallback
  - `data/ingested.csv`, `data/test.csv`
- You can customize model hyperparameters in `src/data_pipeline/train_model.py`.

## Example JSON for /predict

```json
{
  "year": 2016,
  "mileage": 60000,
  "brand": "toyota",
  "fuel_type": "petrol",
  "transmission": "automatic",
  "owner_count": 1
}
```

