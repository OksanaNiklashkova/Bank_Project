from typing import Any, Dict
import os
import requests
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime


load_dotenv()
API_KEY = os.getenv("API_KEY_STOCKS")


def make_transactions(file_path: str | None = None) -> Any:
    """Функция, считывающая транзакции из xlsx-файла и возвращающая
    их в виде списка словарей python"""
    if not file_path:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(file_dir, "..", "data", "operations.xlsx")
    try:
        data_frame = pd.read_excel(file_path)
        data_xlsx = data_frame.to_dict(orient="records")
        return data_xlsx
    except FileNotFoundError:
        print("Ошибка! Файл не найден!")
    except Exception:
        print("Данные имеют неверный формат!")


def filter_by_currency_month(transactions: list, act_date: str) -> list:
    """Функция отбирает транзакции за текущий месяц"""
    end_date = datetime.strptime(act_date, "%d.%m.%Y")
    start_date = end_date.replace(day=1)
    filtered_by_month_transactions = []
    for t in transactions:
        t_date = datetime.strptime(t.get('Дата операции', "01.01.2000").split()[0], "%d.%m.%Y")
        if start_date <= t_date <= end_date:
            filtered_by_month_transactions.append(t)
    transactions = filtered_by_month_transactions
    return transactions

def get_top_transactions(transactions: list) -> dict:
    """Функция вычисляет ТОП-5 транзакций по сумме"""
    transactions_df = pd.DataFrame(transactions)
    top_df = transactions_df.sort_values(by='Сумма платежа', ascending=False, key=lambda x: abs(x))[:5]
    top_transactions = top_df.to_dict(orient="records")
    return top_transactions


def filtered_by_card_number(transactions: list) -> list[Dict]:
    """Функция сортирует транзакции по номеру карты"""
    transactions_df = pd.DataFrame(transactions)
    transactions_by_cards = [
        {'Номер карты': card, 'Транзакции': group.to_dict('records')}
        for card, group in transactions_df.groupby('Номер карты')
    ]
    return transactions_by_cards


def get_card_info(transactions: list) -> list:
    """Функция получает выводимую информацию: номер карты,
    сумму расходов за текущий месяц, включая дату, указанную в запросе,
    начисленный кешбэк, ТОП-5 транзакций по сумме"""
    cards = []
    for item in transactions:
        card = {}
        cards.append(card)
        card["last_digits"]= item.get('Номер карты')[1:]
        transactions_df = pd.DataFrame(item.get('Транзакции'))
        payments = float(round((transactions_df['Сумма платежа'][transactions_df['Сумма платежа'] < 0].sum()) * (-1), 2))
        cashback = float(round(transactions_df['Кэшбэк'].replace(pd.NA, 0).sum(), 2))

        card["total_spent"] =  float(payments)
        card["cashback"] = float(cashback)
    return cards


def get_exchange_rate(currency_op: list, currency_main: str) -> list:
    """Функция запрашивает курс заданной валюты к валюте счета пользователя"""
    currency_rates = []
    url = "https://api.twelvedata.com/exchange_rate"
    for item in currency_op:
        params = {"symbol": f"{item}/{currency_main}", "apikey": API_KEY}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        currency_rates.append(data)
    return currency_rates



def get_stocks_rates(stocks: list) -> list:
    """Функция запрашивает актуальный курс выбранных акций из индекса S&P500"""
    stocks_rates = []
    url = "https://api.twelvedata.com/price"
    for item in stocks:
        stock_info = {}
        stock_info["stock"] = item
        params = {"symbol": item, "apikey": API_KEY}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        data['price'] = round(float(data['price']), 2)
        stock_info.update(data)
        stocks_rates.append(stock_info)
    return stocks_rates
