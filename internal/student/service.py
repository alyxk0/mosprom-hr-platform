# internal/student/service.py
from typing import Optional, Dict, Any
from entity.resume import Resume

class StudentService:
    """
    Слой бизнес-логики для студентов (управление резюме, валидация, правила).
    Не зависит от Flask — принимает объект storage (обёртка над БД).
    """

    def __init__(self, storage):
        self.storage = storage

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Вернуть пользователя по id (через storage)."""
        # Предполагаем, что storage умеет обращаться к таблице users
        return self.storage.get_user_by_id(user_id)  # добавь этот метод в Storage если нужно

    def get_resume(self, user_id: str) -> Optional[Resume]:
        """Возвращает объект Resume или None."""
        row = self.storage.get_resume_by_user(user_id)
        if not row:
            return None
        data = row.get('data') if isinstance(row, dict) else row
        try:
            return Resume.from_dict(data)
        except Exception:
            return None

    def save_resume(self, user_id: str, resume: Resume) -> bool:
        """
        Применяет бизнес-правила, валидирует резюме и сохраняет через storage.
        Возвращает True при успехе или False.
        """
        # Пример простого правила: имя и фамилия обязательны
        v = resume.validate()
        if not v.get('ok'):
            # сюда можно поднять специальный Exception или вернуть подробности
            return False

        # Подготовить словарь для сохранения
        resume_dict = resume.to_dict()
        saved = self.storage.save_resume(user_id=user_id, resume_dict=resume_dict)
        return saved is not None

    # пример дополнительного метода: анонимизация и публикация резюме
    def publish_anonymized_resume(self, user_id: str) -> Optional[Dict[str, Any]]:
        res = self.get_resume(user_id)
        if not res:
            return None
        anon = res.anonymize()
        # возможно сохранить в отдельную таблицу public_resumes
        saved = self.storage.save_public_resume(user_id=user_id, resume_dict=anon.to_dict())
        return saved