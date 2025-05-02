import logging
import os
import re
import json

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
log_file = os.path.join(log_dir, "services_logs.log")
services_logger = logging.getLogger("services_logger")
services_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)

from src.utils import make_transactions

def search_by_phones(transactions: list) -> str:
    """Функция возвращает JSON со всеми транзакциями,
    содержащими в описании мобильные номера."""
    services_logger.info("получение списка транзакций")
    phones_transactions = []
    for transaction in transactions:
        if re.search(r'(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', transaction.get("Описание", ""), flags=0):
            phones_transactions.append(transaction)
    services_logger.info("формирование ответа")
    if len(phones_transactions) != 0:
        services_logger.info("поиск произведен успешно")
        return json.dumps(phones_transactions, ensure_ascii=False)
    else:
        services_logger.warning("поиск не дал результатов")
        return json.dumps({"Результаты поиска": "Ничего не нашлось"}, ensure_ascii=False)


if __name__ == '__main__':
    transactions = make_transactions()
    print(search_by_phones(transactions))