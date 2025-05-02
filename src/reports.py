import json
from functools import wraps
from typing import Any, Optional, Callable, TextIO
import os
import pandas as pd
from datetime import datetime, date
from src.utils import make_transactions


def report_log(filename: str = "report.json") -> Any:
    """Декоратор, который записывает результаты формирования отчетов в файл.
    Можно передать в аргумент декоратора название для файла с отчетами, по умолчанию -
    report.txt"""
    def decorator1(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            result = func(*args, **kwargs)
            if not result.empty:
                dir_path = os.path.dirname(os.path.abspath(__file__))
                reports_data_dir = os.path.join(dir_path, "..", "reports_data")
                os.makedirs(reports_data_dir, exist_ok=True)
                file_path = os.path.join(reports_data_dir, filename)
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        json.dump(result.to_dict(orient="records"), file, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"Ошибка при сохранении отчета: {e}")
            return result
        return wrapper
    return decorator1


@report_log()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """Функция получает список транзакций (DF), категорию и дату (по умолчанию - текущую)
    и возвращает траты по заданной категории за последние три месяца (от переданной даты)."""
    if date:
        end_date = pd.to_datetime(date, dayfirst=True)
    else:
        end_date = pd.to_datetime(datetime.now())
    start_date = end_date - pd.DateOffset(months=3)
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], dayfirst=True)

    filtered_transactions_df = transactions[(transactions['Дата операции'] >= start_date) & \
                               (transactions['Дата операции'] <= end_date) & \
                               (transactions['Категория'] == category)]
    filtered_transactions_df = filtered_transactions_df.copy()
    filtered_transactions_df['Дата операции'] = filtered_transactions_df['Дата операции'].dt.strftime('%d.%m.%Y %H:%M:%S')

    return filtered_transactions_df


if __name__ == '__main__':
    print((spending_by_category(transactions=pd.DataFrame(make_transactions()), category="Переводы", date="02.05.2020")).to_dict(orient="records"))