# storage/storage.py
from supabase import create_client, Client
import logging


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
            logging.error("Ошибка при поиске пользователя:", e)
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
            logging.error("Ошибка при создании пользователя:", e)
            return None

    # ============ методы дл сохранения резюме ================
    def save_resume(self, user_id: str, resume_dict: dict):
        """Создать или обновить резюме пользователя. Здесь простая вставка — можно сделать UPSERT."""
        try:
            # Вариант: попробуем обновить, если уже есть резюме, иначе вставить.
            existing = self.client.table('resumes').select('id').eq('user_id', user_id).execute()
            if existing.data:
                resume_id = existing.data[0]['id']
                response = self.client.table('resumes').update({'data': resume_dict}).eq('id', resume_id).execute()
            else:
                response = self.client.table('resumes').insert({'user_id': user_id, 'data': resume_dict}).execute()
            self._log_response(response)
            return response.data
        except Exception as e:
            print(f"[Storage] Ошибка при сохранении резюме: {repr(e)}")
            if hasattr(e, "args") and e.args:
                print("Exception.args:", e.args)
            return None

    def get_resume_by_user(self, user_id: str):
        try:
            response = self.client.table('resumes').select('*').eq('user_id', user_id).execute()
            self._log_response(response)
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"[Storage] Ошибка при получении резюме: {repr(e)}")
            return None
