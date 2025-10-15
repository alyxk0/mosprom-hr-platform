# cmd/app.py
import sys
import os

# Настройка путей для корректного импорта наших модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем наши классы-компоненты
from config.config import Config
from storage.storage import Storage
from server.server import Server

def main():
    """
    Главная функция, которая инициализирует и запускает приложение.
    """
    # 1. Создаем объект конфигурации
    try:
        cfg = Config()
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации: {e}")
        return

    # 2. Создаем объект для работы с хранилищем (БД), передавая ему конфиг
    db_storage = Storage(config=cfg)

    # 3. Создаем объект сервера, передавая ему конфиг и хранилище
    web_server = Server(config=cfg, storage=db_storage)

    # 4. Запускаем сервер
    web_server.run()


if __name__ == "__main__":
    main()