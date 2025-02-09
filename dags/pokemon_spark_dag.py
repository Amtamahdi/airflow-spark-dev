from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'pokemon_spark_etl',
    default_args=default_args,
    description='ETL Pokemon data using Spark',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 2, 8),
    catchup=False
) as dag:

    # Chemin vers le script spark qui sera exécuté
    spark_submit_task = BashOperator(
        task_id='spark_pokemon_etl',
        bash_command="""
            spark-submit \
            --driver-class-path /opt/airflow/postgresql-42.2.18.jar \
            --jars /opt/airflow/postgresql-42.2.18.jar \
            /opt/airflow/dags/pokemon_spark_etl.py
        """
    )

    spark_submit_task