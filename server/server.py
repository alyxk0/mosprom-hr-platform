# server/server.py
import logging
import os
from flask import Flask, render_template, request, redirect, url_for, session, current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Импортируем blueprints (контроллеры)
from internal.organisation.organizations import organizations_bp
from internal.student.controllers import students_bp   # <--- оставляем этот
from internal.university.universities import universities_bp

from internal.student.service import StudentService



class Server:
    """
    Класс, инкапсулирующий всю логику веб-сервера Flask.
    """

    def __init__(self, config, storage):
        self.config = config
        self.storage = storage  # Получаем готовый объект для работы с БД

        # Создаём приложение Flask
        self.app = Flask(__name__, template_folder='../templates', static_folder='../static')

        # Секретный ключ: в dev можно использовать os.urandom, в prod хранить в env
        secret = os.environ.get("FLASK_SECRET_KEY")
        if secret:
            self.app.secret_key = secret
        else:
            self.app.secret_key = os.urandom(24)

        # Инициализация логгирования (базовая)
        logging.basicConfig(level=logging.DEBUG)

        # Регистрируем blueprints и сервисы
        self._register_blueprints()
        self._register_services()

        # Регистрируем маршруты локальные (index, login, logout)
        self._register_routes()

        # Прикрепляем объект storage к контексту приложения (каждый запрос)
        @self.app.before_request
        def before_request():
            current_app.db = self.storage
            # student_service создаём при старте и не пересоздаём при каждом запросе,
            # но на всякий случай гарантируем доступ:
            if not getattr(current_app, "student_service", None):
                current_app.student_service = StudentService(self.storage)

    def _register_blueprints(self):
        """Регистрируем внешние blueprints (presentation layer)."""
        self.app.register_blueprint(organizations_bp)
        self.app.register_blueprint(students_bp)
        self.app.register_blueprint(universities_bp)

    def _register_services(self):
        """Создаём экземпляры сервисов бизнес-логики и прикрепляем к app."""
        # StudentService нужен в контроллерах — создаём и прикрепляем
        self.app.student_service = StudentService(self.storage)

    def _register_routes(self):
        """Реестрация общих маршрутов (index, login, logout)."""
        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/login", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                email = request.form.get("email")
                password = request.form.get("password")
                action = request.form.get("action")

                # Логируем событие, но не пароль
                logging.debug("Login attempt: action=%s, email=%s", action, email)

                # Используем self.storage для доступа к БД
                if action == "register":
                    user_type = request.form.get("user_type")
                    if self.storage.get_user_by_email(email):
                        return render_template("login.html", error="Пользователь с таким email уже существует")

                    password_hash = generate_password_hash(password)
                    self.storage.create_user(email, password_hash, user_type)
                    return render_template("login.html", success="Регистрация успешна! Теперь вы можете войти.")

                elif action == "login":
                    user = self.storage.get_user_by_email(email)
                    if user and check_password_hash(user['password_hash'], password):
                        # Устанавливаем сессию
                        session['user'] = {'id': user['id'], 'email': user['email'], 'user_type': user['user_type']}

                        # Редирект в зависимости от типа
                        if user['user_type'] == "organization":
                            return redirect(url_for("organizations.dashboard"))
                        if user['user_type'] == "student":
                            return redirect(url_for("students.dashboard")) # <- Это правильно, он ведет в контроллер студентов
                        if user['user_type'] == "university":
                            return redirect(url_for("universities.dashboard"))

                    return render_template("login.html", error="Неправильный email или пароль")

            return render_template("login.html")

        @self.app.route("/logout")
        def logout():
            session.pop("user", None)
            return redirect(url_for("index"))

    def run(self):
        """Запускает веб-сервер."""
        host = self.config.get_server_host()
        port = self.config.get_server_port()
        debug = self.config.get_server_debug() if hasattr(self.config, "get_server_debug") else True
        self.app.run(host=host, port=port, debug=debug)


# Если нужно запускать напрямую
def create_app(config, storage):
    server = Server(config, storage)
    return server.app