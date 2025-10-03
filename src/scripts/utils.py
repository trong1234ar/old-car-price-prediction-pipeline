import os
from typing import Dict, Any

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_configs() -> Dict[str, Any]:
    cfg_dir = PROJECT_ROOT / "src" / "configs"
    return {
        "airflow": load_yaml(cfg_dir / "airflow_config.yaml"),
        "spark": load_yaml(cfg_dir / "spark_config.yaml"),
        "mlflow": load_yaml(cfg_dir / "mlflow_config.yaml"),
    }


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "airflow_logs").mkdir(exist_ok=True)
    (PROJECT_ROOT / "mlruns").mkdir(exist_ok=True)


def get_mlflow_paths(cfg: Dict[str, Any]):
    tracking_uri = cfg["mlflow"].get("tracking_uri", str(PROJECT_ROOT / "mlruns"))
    experiment_name = cfg["mlflow"].get("experiment_name", "old-car-price-exp")
    registered_model_name = cfg["mlflow"].get("registered_model_name", "old-car-price-model")
    return tracking_uri, experiment_name, registered_model_name


def get_data_paths():
    return {
        "ingested": DATA_DIR / "ingested.csv",
        "train": DATA_DIR / "train.csv",
        "test": DATA_DIR / "test.csv",
        "local_model": ARTIFACTS_DIR / "model.pkl",
    }

def cars_to_df(cars):
    df = pd.DataFrame([car.dict() for car in cars])
    return df
