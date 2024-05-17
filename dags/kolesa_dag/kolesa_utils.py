import pandas as pd
import re
from decimal import Decimal

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
headers = {
    'User-Agent': user_agent
}

header_keys = ['mark', 'model', 'year']
price_classes = ['offer-price', 'offer__price', 'a-header__price']
header_classes = ['header-content', 'offer__header-wrap']
description_classes = ['a-black a-notes', 'text']


def extract_car_data(soup_page, cars_dict):
    ''' Extracting data from each page '''

    data_header = find_info(soup_page, header_classes)
    header_values = data_header.find(['h4', 'h1']).text.strip().split()
    car_info_1 = dict(zip(header_keys, header_values))

    data_price = find_info(soup_page, price_classes)
    price_digits = re.findall(r'\d+', data_price.text.strip())
    price = Decimal(''.join(price_digits))
    car_info_1['price'] = price

    data_description = find_info(soup_page, description_classes)
    if data_description:
        description = re.sub(r'\s+', ' ', data_description.find('p').text).strip()
        car_info_1['description'] = description

    labels_list, values_list = populate_list(soup_page)

    car_info_2 = dict(zip(labels_list, values_list))
    car_info = {
        **car_info_1,
        **car_info_2
    }

    cars_dict.append(car_info)

    return cars_dict


def find_info(soup, class_names):
    for class_name in class_names:
        data = soup.find('div', class_=class_name)
        if data:
            break

    return data


def find_elements(soup, tag_names, class_names):
    elements = None
    for class_name in class_names:
        elements = soup.find_all(tag_names, class_=class_name)
        if elements:
            break
    return elements


def populate_list(soup) -> list:
    class_labels = ['value-title', 'a-properties__label']
    class_values = ['value', 'a-properties__value']

    label_tags = ['dt', 'div']
    value_tags = ['dd', 'div']

    labels = find_elements(soup, label_tags, class_labels)
    values = find_elements(soup, value_tags, class_values)

    labels_list = [label.text.strip() for label in labels]
    values_list = [value.text.strip() for value in values]

    return labels_list, values_list


def clean_dict(dict_to_clean):
    cars_df = pd.DataFrame(dict_to_clean)
    cars_df = cars_df.drop_duplicates()
    cars_df = cars_df.drop('Наличие', axis=1)
    new_column_names = ['city', 'generation', 'body', 'engine_volume',
                        'mileage', 'transmission', 'drive_unit',
                        'steering_wheel', 'color', 'is_customized']

    columns_to_rename = cars_df.columns[5:]
    cars_df = cars_df.rename(columns=dict(zip(columns_to_rename, new_column_names)))

    mileage_index = cars_df.columns.get_loc('mileage')
    cars_df.insert(mileage_index + 1, 'unit', value=None)
    cars_df['unit'] = cars_df['mileage'].astype(str).str.split().apply(lambda x: x[-1].strip())
    cars_df['mileage'] = cars_df['mileage'].astype(str).str.split().apply(lambda x: ''.join(x[:-1]) if x else None)
    cars_df['engine_volume'] = cars_df['engine_volume'].str.split().apply(lambda x: x[0]).astype('float')
    cars_df['is_customized'] = cars_df['is_customized'].map({'Да': True, 'Нет': False})
    cars_df['city'] = cars_df['city'].replace(cities)
    cars = cars_df.to_dict('records')

    return cars


cities = {
    'Алматы': 'Almaty','Астана': 'Astana','Тараз': 'Taraz','Атырау': 'Atyrau','Актобе': 'Aktobe',
    'Актау': 'Aktau','Талдыкорган': 'Taldykorgan','Уральск': 'Uralsk','Шымкент': 'Shymkent',
    'Караганда': 'Karaganda','Шалкар': 'Shalkar','Жалагаш': 'Zhalagash',
    'Жанаозен': 'Zhanaozen','Кызылорда': 'Kyzylorda','Павлодар': 'Pavlodar',
    'Петропавловск': 'Petropavlovsk', 'Туркестан': 'Turkistan', 'Костанай': 'Kostanay',
    'Усть-Каменогорск': 'Ust-Kamenogorsk', 'Аральск': 'Aralsk',  'Каскелен': 'Kaskelen',
    'Мангистау': 'Mangistau',
    'Семей': 'Semey', 'Экибастуз': 'Ekibastuz', 'Каргалы': 'Kargaly', 'Темиртау': 'Temirtau',
    'Улытау': 'Ulytau', 'Жанакорган': 'Zhanakorgan', 'Жосалы': 'Zhosaly',
    'Кандыагаш': 'Kandyagash', 'Рудный': 'Rudnyi',  'Сарыагаш': 'Saryagash',  'Жаркент': 'Zharkent',
    'Каражал': 'Karazhal',  'Аксай': 'Aksay',  'Мерке': 'Merke',
    'Кульсары': 'Kulsary',  'Шиели': 'Shieli',  'Жетысай': 'Zhetisay',
}

