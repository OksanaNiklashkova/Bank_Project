import os.path
from datetime import datetime

import requests
from dotenv import load_dotenv
import json

from src.utils import make_transactions, filter_by_currency_month, get_top_transactions, filtered_by_card_number, get_card_info, get_exchange_rate, get_stocks_rates

load_dotenv()
API_KEY = os.getenv("API_KEY_STOCKS")

def get_current_hour():
    return datetime.now().hour

def main() -> None:
    """Функция принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ со следующими данными:
    приветствие, информация о каждой карте, сумме расходов и кешбэка за месяц,
    курсы валют, котировки акций"""

    act_time = get_current_hour()
    data = {}
    if 6 <= act_time < 11:
        data["greeting"] = "Доброе утро!"
    elif 11 <= act_time < 17:
        data["greeting"] = "Добрый день!"
    elif 17 <= act_time < 23:
        data["greeting"] = "Добрый вечер!"
    else:
        data["greeting"] = "Доброй ночи!"
    transactions = make_transactions()
    # проверяем, удалось ли прочитать файл xlsx
    if not transactions or not isinstance(transactions, list) or len(transactions) == 0:
        data["Ошибка"] = "Не удалось получить данные о транзакциях"
    else:
        act_date = input("Введите дату: ")
        # проверяем, есть ли в файле данные за выбранный период
        if not datetime.strptime("01.01.2018", "%d.%m.%Y")< datetime.strptime(act_date, "%d.%m.%Y") < datetime.strptime("31.12.2021", "%d.%m.%Y"):
            # если данных за период нет, добавляем в ответ сообщение об ошибке
            data["Ошибка"] = "Данные о транзакциях за период отсутствуют"
        else:
            # если данные за период получены, производим обработку
            transactions = filter_by_currency_month(transactions, act_date)
            data["cards"] = get_card_info(filtered_by_card_number(transactions))
            data['top_transactions'] = get_top_transactions(transactions)
            data["currency_rates"] = get_exchange_rate(["USD", "EUR"], "RUB")
            data["stock_prices"] = get_stocks_rates(['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA'])
    # независимо от распакованных данных запрашиваем информацию о валюте и акциях
    dir_path = os.path.dirname(os.path.abspath(__file__))
    user_settings_path = os.path.join(dir_path, "..", "user_settings.json")
    with open(user_settings_path, "r", encoding="utf-8") as file:
        settings = json.load(file)
        currency_op = settings["user_currencies"]
        currency_main = settings["user_main_currency"]
        stocks = settings["user_stocks"]
        data["currency_rates"] = get_exchange_rate(currency_op, currency_main)
        data["stock_prices"] = get_stocks_rates(stocks)
    json_response = json.dumps(data, ensure_ascii=False)
    print(json_response)


if __name__ == '__main__':
    main()


