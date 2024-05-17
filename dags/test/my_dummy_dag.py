from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime


def print_hello():
    print("Hello, world!")


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 16),
    'retries': 1
}

with DAG('hello_world_dag',
         default_args=default_args,
         schedule_interval='*/1 * * * *',
         catchup=False) as dag:
    hello_task = PythonOperator(
        task_id='hello_task',
        python_callable=print_hello
    )

    hello_task