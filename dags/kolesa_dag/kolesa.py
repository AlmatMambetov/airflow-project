from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from kolesa_dag.kolesa_utils import *
from time import sleep
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter

def _get_data():
    cars_dict = []
    page_num = 1
    connect_timeout = 10
    read_timeout = 10
    session = requests.Session()
    retry = requests.packages.urllib3.util.retry.Retry(connect=3, backoff_factor=0.5)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    while True:
        sleep(10)
        kolesa_url = f'https://kolesa.kz/cars/toyota/alphard/?page={page_num}'
        response = session.get(kolesa_url, headers=headers, timeout=(connect_timeout, read_timeout))
        soup = BeautifulSoup(response.text, 'lxml')
        cars = soup.find_all('a', class_='a-card__link')

        if not cars:
            break

        for data in cars:
            car_url = data.get('href')
            full_car_url = f'https://kolesa.kz{car_url}'
            sleep(5)

            # Send request to each advertisement
            response = session.get(full_car_url, headers=headers,timeout=(connect_timeout, read_timeout))
            soup_page = BeautifulSoup(response.text, 'html.parser')

            cars_dict = extract_car_data(soup_page, cars_dict)

        page_num += 1

    cars = clean_dict(cars_dict)

    row = [list(car.values()) for car in cars]
    column = list(cars[0].keys())

    return row, column


def _save_data(ti=None):
    transformed_data = ti.xcom_pull(key='return_value', task_ids='_get_data')
    rows, columns = transformed_data

    dwh_hook = PostgresHook(postgres_conn_id='dwh')
    dwh_hook.insert_rows(
        table='kolesa_parsing',
        rows=rows,
        columns=columns,
    )

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 5),
    'retries': 0,
}

with DAG('kolesa_dag',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='dwh',
        sql='scripts/create_kolesa.sql',
    )

    get_data = PythonOperator(
        task_id='get_data',
        python_callable=_get_data,
        do_xcom_push=True,
    )

    save_data = PythonOperator(
    task_id='save_data',
    python_callable=_save_data,
    )


    create_table >> get_data >> save_data

