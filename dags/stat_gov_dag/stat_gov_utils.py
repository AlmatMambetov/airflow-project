from bs4 import BeautifulSoup
import requests
import pandas as pd
import psycopg2

config = {
    'database': 'stat_gov_db',
    'user': 'stat_gov_user',
    'password': 'statgov',
    'host': 'localhost',
    'port': '5487',
}


def postgres_connection(config):
    conn = psycopg2.connect(database=config['database'],
                            user=config['user'],
                            password=config['password'],
                            host=config['host'],
                            port=config['port'],
                            )

    return conn


def get_transport_data(url):
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    data = soup.find_all('div', class_='element-file-formats')
    xlsx_url = f"https://stat.gov.kz{data[-1].find('a').get('href')}"

    rows_to_skip = list(range(1, 85)) + list(range(162, 530)) + list(range(609, 100000))
    df = pd.read_excel(xlsx_url, skiprows=rows_to_skip, header=1)

    return df


def transform_data(df):
    start_index_1 = df[df.iloc[:, 0] == 'Перевезено пассажиров, тыс. человек'].index[0]
    start_index_2 = df[df.iloc[:, 0] == 'Перевезено пассажиров, тыс. человек'].index[1]

    df_1 = df.iloc[start_index_1 + 1: start_index_1 + 19]
    df_2 = df.iloc[start_index_2 + 1: start_index_2 + 19]

    df_1.insert(0, 'transport_type', 'Железнодорожный транспорт')
    df_2.insert(0, 'transport_type', 'Воздушный транспорт')

    df = pd.concat([df_1, df_2], ignore_index=True)
    df.insert(0, 'category', 'Перевезено пассажиров, тыс. человек')
    df = df.rename(columns={'Unnamed: 0': 'year'})
    df.columns = ['category', 'transport_type', 'year',
                  '01.01',
                  '02.01',
                  '03.01',
                  '04.01',
                  '05.01',
                  '06.01',
                  '07.01',
                  '08.01',
                  '09.01',
                  '10.01',
                  '11.01',
                  '12.01']

    df = df.melt(id_vars=['year', 'category', 'transport_type'], var_name='month', value_name='value')

    df['year_month'] = df['year'].astype(str) + '.' + df['month']
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    df_pivot = df.pivot_table(index=['year_month', 'category', 'transport_type'],
                              values='value', aggfunc='first')

    df_pivot['value_int'] = (
        df_pivot['value_float']
                             .astype(str)
                             .str.replace('.', '')
                             .apply(lambda x: x.ljust(6, '0'))
                             .astype(int)
    )

    columns = list(df_pivot)
    x, y = columns.index('value_float'), columns.index('value_int')
    columns[x], columns[y] = columns[y], columns[x]
    df_pivot = df_pivot[columns]

    return df_pivot


def replace_columns(df):
    columns = list(df)
    x, y = columns.index('value_float'), columns.index('value_int')
    columns[x], columns[y] = columns[y], columns[x]
    df = df[columns]

    return df

def insert_data(df, conn):
    conn = conn
    df.to_sql('transport_data_temp', con=conn, if_exists='replace', schema='stage')

