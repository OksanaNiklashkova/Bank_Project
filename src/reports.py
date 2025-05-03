import json
import logging
from functools import wraps
from typing import Any, Optional, Callable
import os
import pandas as pd
from datetime import datetime
from src.utils import make_transactions

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
log_file = os.path.join(log_dir, "reports_logs.log")
reports_logger = logging.getLogger("services_logger")
reports_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
reports_logger.addHandler(file_handler)

def report_log(filename: str = "report.json") -> Any:
    """Декоратор, который записывает результаты формирования отчетов в файл.
    Можно передать в аргумент декоратора название для файла с отчетами, по умолчанию -
    report.txt"""
    def decorator1(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            reports_logger.info("запрос на создание отчета о транзакциях по категории")
            result = func(*args, **kwargs)
            if isinstance(result, pd.DataFrame):
                dir_path = os.path.dirname(os.path.abspath(__file__))
                reports_data_dir = os.path.join(dir_path, "..", "reports_data")
                os.makedirs(reports_data_dir, exist_ok=True)
                file_path = os.path.join(reports_data_dir, filename)
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        reports_logger.info(f"запись отчета о транзакциях по категории в файл {filename}")
                        json.dump(result.to_dict(orient="records"), file, ensure_ascii=False, indent=4)
                    reports_logger.info(f"отчет о транзакциях по категории успешно сохранен")
                except Exception as e:
                    reports_logger.error("ошибка при сохранении отчета")
                    print(f"Ошибка при сохранении отчета: {e}")
            return result
        return wrapper
    return decorator1


@report_log()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame|str:
    """Функция получает список транзакций (DF), категорию и дату (по умолчанию - текущую)
    и возвращает траты по заданной категории за последние три месяца (от переданной даты)."""
    reports_logger.info(f"получение данных о периоде для отчета о транзакциях по категории {category}")

    if date:
        try:
            end_date = pd.to_datetime(date, dayfirst=True)
        except ValueError as e:
            reports_logger.error(f"Ошибка в формате даты: {date}. Ошибка: {str(e)}")
            return {f"Неверный формат даты - {date}": "Используйте формат ДД.ММ.ГГГГ"}
    else:
        end_date = pd.to_datetime(datetime.now())

    start_date = end_date - pd.DateOffset(months=3)
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], dayfirst=True)
    reports_logger.info(f"формирование отчета о транзакциях по категории {category}")
    filtered_transactions_df = transactions[(transactions['Дата операции'] >= start_date) & \
                               (transactions['Дата операции'] <= end_date) & \
                               (transactions['Категория'] == category)]
    filtered_transactions_df = filtered_transactions_df.copy()
    filtered_transactions_df['Дата операции'] = filtered_transactions_df['Дата операции'].dt.strftime('%d.%m.%Y %H:%M:%S')

    return filtered_transactions_df
