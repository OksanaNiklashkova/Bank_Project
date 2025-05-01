import datetime
import json

from src.utils import make_transactions, filter_by_currency_month, get_top_transactions, filtered_by_card_number, get_card_info, get_exchange_rate, get_stocks_rates

def main(act_date: str|None = None) -> list|None:
    """Функция принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ со следующими данными:
    приветствие, информация о каждой карте, сумме расходов и кешбэка за месяц,
    курсы валют, котировки акций"""
    date_time = datetime.datetime.now()
    act_time = date_time.hour
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
    transactions = filter_by_currency_month(transactions, '16.01.2018')
    data["cards"] = get_card_info(filtered_by_card_number(transactions))
    data['top_transactions'] = get_top_transactions(transactions)
    data["currency_rates"] = get_exchange_rate(["USD", "EUR"], "RUB")
    data["stock_prices"] = get_stocks_rates(['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA'])
    json_response = json.dumps(data, ensure_ascii=False)

    print(json_response)


if __name__ == '__main__':
    act_date = input("Введите дату: ")
    main()


