from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

films = [
    {
        "title": "The Shawshank Redemption",
        "year": 1994,
        "director": "Frank Darabont",
        "genre": ["drama", "crime"],
        "country": "USA"
    },
    {
        "title": "The Godfather",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "genre": ["crime", "drama"],
        "country": "USA"
    },
    {
        "title": "The Dark Knight",
        "year": 2008,
        "director": "Christopher Nolan",
        "genre": ["action", "crime", "drama"],
        "country": "USA"
    },
    {
        "title": "Pulp Fiction",
        "year": 1994,
        "director": "Quentin Tarantino",
        "genre": ["crime", "drama"],
        "country": "USA"
    },
    {
        "title": "Forrest Gump",
        "year": 1994,
        "director": "Robert Zemeckis",
        "genre": ["drama", "romance"],
        "country": "USA"
    },
    {
        "title": "Inception",
        "year": 2010,
        "director": "Christopher Nolan",
        "genre": ["action", "adventure", "sci-fi"],
        "country": "USA"
    },
    {
        "title": "The Matrix",
        "year": 1999,
        "director": "The Wachowskis",
        "genre": ["action", "sci-fi"],
        "country": "USA"
    },
    {
        "title": "The Silence of the Lambs",
        "year": 1991,
        "director": "Jonathan Demme",
        "genre": ["crime", "drama", "thriller"],
        "country": "USA"
    },
    {
        "title": "Gladiator",
        "year": 2000,
        "director": "Ridley Scott",
        "genre": ["action", "drama"],
        "country": "USA"
    },
    {
        "title": "The Lion King",
        "year": 1994,
        "director": "Roger Allers, Rob Minkoff",
        "genre": ["animation", "adventure", "drama"],
        "country": "USA"
    }
]


def save_data():
    rows = [list(film.values()) for film in films]
    fields= list(films[0].keys())

    postgres_hook = PostgresHook(postgres_conn_id="dwh")
    postgres_hook.insert_rows(
        table='movies',
        rows=rows,
        target_fields=fields,
        commit_every=1000
    )

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 9),
    'retries': 0
}

with DAG('movie_night',
         default_args=default_args,
         schedule_interval='@once',
         catchup=False) as dag:
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='dwh',
        sql='scripts/create_movies.sql'
    )

    save_data = PythonOperator(
        task_id='save_data',
        python_callable=save_data
    )

    create_table >> save_data
