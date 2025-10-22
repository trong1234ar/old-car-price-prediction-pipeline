from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.append(str(project_root))

from src.scripts.model_build import run as run_model_build
from src.scripts.model_eval import run as run_model_eval
from src.scripts.model_reg import run as run_model_reg
from src.logger.logger import get_logger
from configs.config import load_config


# Set up logger
# logger = get_logger("airflow_dag", "INFO", "/logs/model_pipeline.log")
config = load_config()
with DAG(
    dag_id="car_price_ml_pipeline",
    description="Old car price ML prediction pipeline",
    default_args={
        "depends_on_past": False,   
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
        },
    start_date=datetime.now() - timedelta(days=config.get("start_days_ago", 1)),
    schedule="0 10 * * *",  # 00:00 UTC = 07:00 Bangkok time
    catchup=False,
    tags=["ml", "car-price"],
) as dag:

    model_build_task = PythonOperator(
        task_id='model_build',
        python_callable=run_model_build,
        dag=dag,
    )

    model_eval_task = PythonOperator(
        task_id='model_evaluation',
        python_callable=run_model_eval,
        dag=dag,
    )

    model_reg_task = PythonOperator(
        task_id='model_registration',
        python_callable=run_model_reg,
        dag=dag,
    )

    # Define task dependencies
    model_build_task >> model_eval_task >> model_reg_task
