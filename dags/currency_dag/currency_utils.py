import freecurrencyapi
from datetime import datetime, timedelta

ua = 'Mozilla/5.0 (Linux; Android 9; CPH1938) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36'
headers = {
    'User_Agent': ua
}


attr = ['currency', 'title', 'rate', 'quantity', 'index', 'change', 'date']


client = freecurrencyapi.Client('fca_live_UJwzOYk366WrojFIhKhJzteQTClSTyNLfvs3rCq7')


def get_currency_list(execution_date, base_currency='USD'):
    execution_date = datetime.strptime(execution_date[:10], '%Y-%m-%d')
    prev_date = execution_date - timedelta(days=1)
    year, month, day = prev_date.year, prev_date.month, prev_date.day
    date_obj = f"{year}-{month}-{day}"
    data = client.historical(f'{year}-{int(month):02d}-{int(day):02d}', base_currency=base_currency)
    historical_data = data['data'][f'{year}-{int(month):02d}-{int(day):02d}']

    currencies_list = [{'title': key, 'rate': value} for key, value in historical_data.items()]
    currencies_list = [{**currency, 'date': date_obj} for currency in currencies_list]
    return currencies_list


def return_date(execution_date):
    execution_date = datetime.strptime(execution_date[:10], '%Y-%m-%d')
    prev_date = execution_date - timedelta(days=1)
    return prev_date.year, prev_date.month, prev_date.day
