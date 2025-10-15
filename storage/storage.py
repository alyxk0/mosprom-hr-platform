# storage/storage.py
from supabase import create_client, Client


class Storage:
    """
    Класс для инкапсуляции всей логики работы с базой данных Supabase.
    """

    def __init__(self, config):
        """
        Инициализирует клиент Supabase, используя данные из объекта конфига.
        """
        url = config.get_supabase_url()
        key = config.get_supabase_key()

        if not url or not key:
            raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть установлены в конфиге.")

        self.client: Client = create_client(url, key)

    def get_user_by_email(self, email):
        """Получает пользователя по email."""
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Ошибка при поиске пользователя: {e}")
            return None

    def create_user(self, email, password_hash, user_type):
        """Создает нового пользователя."""
        try:
            response = self.client.table('users').insert({
                'email': email,
                'password_hash': password_hash,
                'user_type': user_type
            }).execute()
            return response.data
        except Exception as e:
            print(f"Ошибка при создании пользователя: {e}")
            return None