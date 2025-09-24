from __future__ import annotations
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pathlib import Path

# Import project functions
from src.scripts.ingest_data import run as ingest_run
from src.data_pipeline.train_model import run as train_run
from src.data_pipeline.evaluate_model import run as eval_run
from src.data_pipeline.save_model import run as save_run
from src.scripts.utils import get_configs

cfg = get_configs()["airflow"]
dag_id = cfg.get("dag_id", "car_price_pipeline_dag")

with DAG(
    dag_id=dag_id,
    description="Old car price end-to-end pipeline",
    start_date=datetime.now() - timedelta(days=cfg.get("start_days_ago", 1)),
    schedule=cfg.get("schedule", "@daily"),
    catchup=False,
    tags=["ml", "car-price"],
) as dag:
    ingest = PythonOperator(
        task_id="ingest_data",
        python_callable=ingest_run,
    )

    train = PythonOperator(
        task_id="train_model",
        python_callable=train_run,
    )

    evaluate = PythonOperator(
        task_id="evaluate_model",
        python_callable=eval_run,
    )

    save = PythonOperator(
        task_id="save_model",
        python_callable=save_run,
    )

    ingest >> train >> evaluate >> save
