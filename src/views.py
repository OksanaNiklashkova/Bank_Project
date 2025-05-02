import os.path
from datetime import datetime

import logging
from dotenv import load_dotenv
import json

from src.utils import make_transactions, filter_by_currency_month, get_top_transactions, filtered_by_card_number, get_card_info, get_exchange_rate, get_stocks_rates

load_dotenv()
API_KEY = os.getenv("API_KEY_STOCKS")

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
log_file = os.path.join(log_dir, "views_logs.log")
views_logger = logging.getLogger("services_logger")
views_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
views_logger.addHandler(file_handler)

def get_current_hour():
    views_logger.info("запуск приложения...")
    views_logger.info("запрос текущего времени")
    return datetime.now().hour

def main() -> None:
    """Функция принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ со следующими данными:
    приветствие, информация о каждой карте, сумме расходов и кешбэка за месяц,
    курсы валют, котировки акций"""
    act_time = get_current_hour()
    data = {}
    views_logger.info("запрос информации от пользователя")
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
        views_logger.warning("предупреждение: транзакции для обработки не найдены")
        data["Ошибка"] = "Не удалось получить данные о транзакциях"
    else:
        correct_act_date = None
        while not correct_act_date:
            views_logger.info("запрос даты для анализа данных")
            act_date = input("Введите дату в формате ДД.ММ.ГГГГ: ")
            try:
                correct_act_date = datetime.strptime(act_date, "%d.%m.%Y")
            except ValueError:
                views_logger.error("ошибка: получены некорректные данные")
                print("Формат данных не соответствует запросу!")

        # проверяем, есть ли в файле данные за выбранный период
        if not datetime.strptime("01.01.2018", "%d.%m.%Y")< correct_act_date < datetime.strptime("31.12.2021", "%d.%m.%Y"):
            # если данных за период нет, добавляем в ответ сообщение об ошибке
            views_logger.warning("предупреждение: транзакции за выбранный период отсутствуют")
            data["Ошибка"] = "Данные о транзакциях за период отсутствуют"
        else:
            # если данные за период получены, производим обработку
            act_date = correct_act_date.strftime("%d.%m.%Y")
            transactions = filter_by_currency_month(transactions, act_date)
            data["cards"] = get_card_info(filtered_by_card_number(transactions))
            data['top_transactions'] = get_top_transactions(transactions)
    # независимо от распакованных данных запрашиваем информацию о валюте и акциях
    views_logger.info("запрос пользовательских настроек из файла")
    dir_path = os.path.dirname(os.path.abspath(__file__))
    user_settings_path = os.path.join(dir_path, "..", "user_settings.json")
    with open(user_settings_path, "r", encoding="utf-8") as file:
        settings = json.load(file)
        currency_op = settings["user_currencies"]
        currency_main = settings["user_main_currency"]
        stocks = settings["user_stocks"]
        data["currency_rates"] = get_exchange_rate(currency_op, currency_main)
        data["stock_prices"] = get_stocks_rates(stocks)
    views_logger.info("формирование ответа на запрос")
    json_response = json.dumps(data, ensure_ascii=False)
    print(json_response)
    views_logger.info("Завершение работы...")


if __name__ == '__main__':
    main()
