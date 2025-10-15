import json

class Config:
    """
    Класс для работы с конфигурационным файлом JSON.
    """

    def __init__(self, file_path='./../config/config.json'):
        """
        Инициализирует объект Config, загружая данные из указанного файла.

        :param file_path: Путь к файлу config.json.
        """
        try:
            with open(file_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise Exception(f"Файл конфигурации не найден по пути: {file_path}")
        except json.JSONDecodeError:
            raise Exception(f"Ошибка декодирования JSON в файле: {file_path}")

    def get_server_config(self):
        """
        Возвращает конфигурацию сервера.
        """
        return self.config.get('server', {})

    def get_db_config(self):
        """
        Возвращает конфигурацию базы данных.
        """
        return self.config.get('DB', {})

    def get_server_host(self):
        """
        Возвращает хост сервера.
        """
        return self.get_server_config().get('host')

    def get_server_port(self):
        """
        Возвращает порт сервера.
        """
        return self.get_server_config().get('port')

    def get_supabase_url(self):
        """
        Возвращает URL Supabase.
        """
        return self.get_db_config().get('SUPABASE_URL')

    def get_supabase_key(self):
        """
        Возвращает ключ Supabase.
        """
        return self.get_db_config().get('SUPABASE_KEY')