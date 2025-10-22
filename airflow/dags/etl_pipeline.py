from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sdk import DAG

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.append(str(project_root))

from configs.config import load_config
from src.scripts.data_extract import run as extract_run
from src.scripts.data_transform import run as transform_run

config = load_config()


with DAG(
    dag_id="car_price_etl_pipeline",
    description="Old car price ETL pipeline",
    default_args={
        "depends_on_past": False,   
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        },
    start_date=datetime.now() - timedelta(days=config.get("start_days_ago", 1)),
    schedule="0 0 * * *",  # 00:00 UTC = 07:00 Bangkok time
    catchup=False,
    tags=["ml", "car-price"],
) as dag:
    extract = PythonOperator(
        task_id="extract_data",
        python_callable=extract_run,
    )
    transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_run,
    )

    extract >> transform
