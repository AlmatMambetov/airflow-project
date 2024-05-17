from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from stat_gov_dag.stat_gov_utils import *
from datetime import timedelta



def load_data():
    url = 'https://stat.gov.kz/ru/industries/business-statistics/stat-transport/dynamic-tables/'
    data = get_transport_data(url)
    transport_data = transform_data(data)

    conn = postgres_connection(config)
    insert_data(transport_data, conn)


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 5, 13),
    'catchup': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=15),
}

with DAG('stat_gov_dag',
         default_args=default_args,
         schedule_interval='0 0 13 * *') as dag:
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='stats',
        sql='scripts/create_table.sql'
    )

    extract_df = PythonOperator(
        task_id='extract_df',
        python_callable=load_data,
        do_xcom_push=True,
    )

    save_data = PostgresOperator(
        task_id='save_data',
        postgres_conn_id='stats',
        sql='scripts/save_data.sql'
    )

    create_table >> extract_df >> save_data
