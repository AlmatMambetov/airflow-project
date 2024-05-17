from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from currency_dag.currency_utils import *
from bs4 import BeautifulSoup
import requests
from itertools import zip_longest
from time import sleep
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.trigger_rule import TriggerRule

def get_data_pound(execution_date):
    sleep(15)
    currencies_list = get_currency_list(execution_date, 'GBP')
    rows = [list(currency.values()) for currency in currencies_list]
    fields = list(currencies_list[0].keys())

    return rows, fields


def get_data_usd(execution_date):
    sleep(15)
    currencies_list = get_currency_list(execution_date)
    rows = [list(currency.values()) for currency in currencies_list]
    fields = list(currencies_list[0].keys())

    return rows, fields


def get_data_rub(execution_date):
    sleep(15)
    currencies_list = get_currency_list(execution_date, 'RUB')
    rows = [list(currency.values()) for currency in currencies_list]
    fields = list(currencies_list[0].keys())

    return rows, fields


def get_data_kzt(execution_date):
    year, month, day = return_date(execution_date)
    date_obj = f"{year}-{month}-{day}"
    url = f'https://nationalbank.kz/rss/get_rates.cfm?fdate={day}.{month}.{year}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    currencies = soup.find_all('item')
    currencies = [[value for value in currency.text.split('\n') if value] for currency in currencies]
    currency_list = [
        dict(zip_longest(attr, curr)) if len(attr) > len(curr) else zip(attr, curr)
        for curr in currencies
    ]

    currencies_list = [{**currency, 'date': date_obj} for currency in currency_list]
    rows = [list(currency.values()) for currency in currencies_list]
    fields = list(currencies_list[0].keys())

    return rows, fields


def fetch_data_pound(ti=None):
    transformed_data = ti.xcom_pull(key='return_value', task_ids='get_data_pound')
    rows, fields = transformed_data
    dwh_hook = PostgresHook(postgres_conn_id='dwh')
    dwh_hook.insert_rows(
        table='stage.currency_pound',
        rows=rows,
        target_fields=fields,
    )


def fetch_data_usd(ti=None):
    transformed_data = ti.xcom_pull(key='return_value', task_ids='get_data_usd')
    rows, fields = transformed_data
    dwh_hook = PostgresHook(postgres_conn_id='dwh')
    dwh_hook.insert_rows(
        table='stage.currency_usd',
        rows=rows,
        target_fields=fields,
    )


def fetch_data_rub(ti=None):
    transformed_data = ti.xcom_pull(key='return_value', task_ids='get_data_rub')
    rows, fields = transformed_data
    dwh_hook = PostgresHook(postgres_conn_id='dwh')
    dwh_hook.insert_rows(
        table='stage.currency_rub',
        rows=rows,
        target_fields=fields,
    )


def fetch_data_kzt(ti=None):
    transformed_data = ti.xcom_pull(key='return_value', task_ids='get_data_kzt')
    rows, fields = transformed_data
    dwh_hook = PostgresHook(postgres_conn_id='dwh')
    dwh_hook.insert_rows(
        table='stage.currency_kzt',
        rows=rows,
        target_fields=fields,
    )


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 5, 2),
    'end_date': datetime(2024, 12, 31),
    'retries': 1,
}


with DAG('currency_parsing',
         default_args=default_args,
         schedule_interval='@daily',
         params={
            'rate_date': datetime.now().strftime('%d.%m.%Y')
            }
         ) as dag:
    create_schema = PostgresOperator(
        task_id='create_schema',
        postgres_conn_id='dwh',
        sql='scripts/create_schemas.sql'
    )
    create_tables = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='dwh',
        sql='scripts/create_tables.sql'
    )

    get_data_usd = PythonOperator(
        task_id='get_data_usd',
        python_callable=get_data_usd,
        op_kwargs={'execution_date': '{{ execution_date }}'},
        do_xcom_push=True,
    )

    get_data_pound = PythonOperator(
        task_id='get_data_pound',
        python_callable=get_data_pound,
        op_kwargs={'execution_date': '{{ execution_date }}'},
        do_xcom_push=True,
    )

    get_data_rub = PythonOperator(
        task_id='get_data_rub',
        python_callable=get_data_rub,
        op_kwargs={'execution_date': '{{ execution_date }}'},
        do_xcom_push=True,
    )

    get_data_kzt = PythonOperator(
        task_id='get_data_kzt',
        python_callable=get_data_kzt,
        op_kwargs={'execution_date': '{{ execution_date }}'},
        do_xcom_push=True,
    )

    fetch_data_pound = PythonOperator(
        task_id='fetch_data_pound',
        python_callable=fetch_data_pound
    )

    fetch_data_usd = PythonOperator(
        task_id='fetch_data_usd',
        python_callable=fetch_data_usd
    )

    fetch_data_rub = PythonOperator(
        task_id='fetch_data_rub',
        python_callable=fetch_data_rub
    )

    fetch_data_kzt = PythonOperator(
        task_id='fetch_data_kzt',
        python_callable=fetch_data_kzt
    )

    dummy_task = DummyOperator(
        task_id='dummy_task'
    )

    dbt_task = BashOperator(
        task_id='run_dbt',
        bash_command='dbt run',
        trigger_rule=TriggerRule.ALL_SUCCESS
    )

    create_schema >> create_tables >> [get_data_pound, get_data_usd, get_data_rub, get_data_kzt]
    get_data_pound >> fetch_data_pound >> dummy_task
    get_data_usd >> fetch_data_usd >> dummy_task
    get_data_rub >> fetch_data_rub >> dummy_task
    get_data_kzt >> fetch_data_kzt >> dummy_task
    dummy_task >> dbt_task