from unittest.mock import patch, mock_open
import json
import pytest

from src.views import get_current_hour
import src.views

def test_get_current_hour() -> None:
    """Тест для функции, получающей текущее время (час),
    проверяет, что возвращаемое значение - целое число"""
    result = get_current_hour()
    assert isinstance(result, int)


def test_main1(get_transactions_2: list, capsys: pytest.CaptureFixture[str]) -> None:
    """Тест для функции main - норма"""
    test_cases = [
        (6, "Доброе утро!"),
        (11, "Добрый день!"),
        (17, "Добрый вечер!"),
        (23, "Доброй ночи!"),
    ]
    test_settings = {
        "user_currencies": ["USD"],
        "user_main_currency": "RUB",
        "user_stocks": ["AAPL"]
    }

    with patch('src.views.get_current_hour') as mock_hour, \
            patch('src.views.make_transactions', return_value=get_transactions_2),\
            patch("builtins.input", return_value="19.01.2018"),\
            patch('src.views.filter_by_currency_month', return_value=get_transactions_2),\
            patch('src.views.filtered_by_card_number', return_value=get_transactions_2),\
            patch('src.views.get_card_info', return_value=[{"last_digits": "4556", "total_spent": 88068.0, "cashback": 880.0},]),\
            patch('src.views.get_top_transactions', return_value = {"top_transactions": [{"date": "12.01.2018", "amount": -87068.0},]}), \
            patch('builtins.open', mock_open(read_data=json.dumps(test_settings))), \
            patch('src.views.get_exchange_rate', return_value={"currencies": [{"currency": "USD", "rate": 81.726},]}),\
            patch("src.views.get_stocks_rates", return_value={"stocks": [{"stock": "AAPL", "price": "212.44"},]}):

        for hour, expected_greeting in test_cases:
            mock_hour.return_value = hour
            src.views.main()
            captured = capsys.readouterr()
            assert expected_greeting in captured.out
            assert "last_digits" in captured.out
            assert "top_transactions" in captured.out
            assert "currencies" in captured.out
            assert "stocks" in captured.out


def test_main2(get_transactions_2: list, capsys: pytest.CaptureFixture[str]) -> None:
    """Тест для функции main - введен неверный формат даты, нет данных за выбранный период"""

    test_settings = {
        "user_currencies": ["USD"],
        "user_main_currency": "RUB",
        "user_stocks": ["AAPL"]
    }

    with patch('src.views.get_current_hour', return_value=12),\
         patch('src.views.make_transactions', return_value=get_transactions_2),\
         patch("builtins.input", side_effect=['20/02/2023', '20.02.2023']), \
         patch('builtins.open', mock_open(read_data=json.dumps(test_settings))),\
         patch('src.views.get_exchange_rate', return_value={"currencies": [{"currency": "USD", "rate": 81.726},]}),\
         patch("src.views.get_stocks_rates", return_value={"stocks": [{"stock": "AAPL", "price": "212.44"},]}):

         src.views.main()
         captured = capsys.readouterr()
         assert "Формат данных не соответствует запросу!" in captured.out
         assert "Данные о транзакциях за период отсутствуют" in captured.out


def test_main3(capsys: pytest.CaptureFixture[str]) -> None:
    """Тест для функции main - файл не найден, пуст или имеет не-xlsx формат"""
    test_cases = [
        (6, "Доброе утро!"),
        (11, "Добрый день!"),
        (17, "Добрый вечер!"),
        (23, "Доброй ночи!"),
    ]

    with patch('src.views.get_current_hour') as mock_hour, \
         patch('src.views.make_transactions', return_value=[]):
                for hour, expected_greeting in test_cases:
                    mock_hour.return_value = hour
                    src.views.main()
                    captured = capsys.readouterr()
                    assert expected_greeting in captured.out
                    assert "Не удалось получить данные о транзакциях" in captured.out


def test_main_logging(get_transactions_2, capsys):
    """Тест проверяет запись в лог при завершении работы"""
    test_settings = {
        "user_currencies": ["USD"],
        "user_main_currency": "RUB",
        "user_stocks": ["AAPL"]
    }

    with patch('src.views.get_current_hour', return_value=12), \
            patch('src.views.make_transactions', return_value=get_transactions_2), \
            patch("builtins.input", return_value="19.01.2023"), \
            patch('builtins.open', mock_open(read_data=json.dumps(test_settings))), \
            patch('src.views.views_logger.info') as mock_logger:
        src.views.main()
        mock_logger.assert_any_call("Завершение работы...")
