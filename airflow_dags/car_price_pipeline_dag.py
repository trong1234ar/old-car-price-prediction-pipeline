from __future__ import annotations
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pathlib import Path

# Import project functions
from src.scripts.extract import run as extract_run
from src.scripts.transform import run as transform_run
from configs.config import load_config

config = load_config()

with DAG(
    description="Old car price ETL pipeline",
    start_date=datetime.now() - timedelta(days=config.get("start_days_ago", 1)),
    schedule=config.get("schedule", "@daily"),
    catchup=False,
    tags=["ml", "car-price"],
) as dag:
    extract = BashOperator(
        task_id="extract_data",
        bash_command='python -m src.scripts.extract',
    )
    transform = BashOperator(
        task_id="transform_data",
        bash_command='python -m src.scripts.transform',
    )

    # train = PythonOperator(
    #     task_id="train_model",
    #     python_callable=train_run,
    # )

    # evaluate = PythonOperator(
    #     task_id="evaluate_model",
    #     python_callable=eval_run,
    # )

    # save = PythonOperator(
    #     task_id="save_model",
    #     python_callable=save_run,
    # )

    extract >> transform
