# server/server.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash

# Импортируем blueprints
from internal.organisation.organizations import organizations_bp
from internal.student.students import students_bp
from internal.university.universities import universities_bp


class Server:
    """
    Класс, инкапсулирующий всю логику веб-сервера Flask.
    """

    def __init__(self, config, storage):
        self.config = config
        self.storage = storage  # Получаем готовый объект для работы с БД
        self.app = Flask(__name__, template_folder='../templates', static_folder='../static')
        self.app.secret_key = os.urandom(24)

        self._register_blueprints()
        self._register_routes()

        # Прикрепляем объект storage к контексту приложения
        @self.app.before_request
        def before_request():
            current_app.db = self.storage

    def _register_blueprints(self):
        self.app.register_blueprint(organizations_bp)
        self.app.register_blueprint(students_bp)
        self.app.register_blueprint(universities_bp)

    def _register_routes(self):
        # Декораторы теперь ссылаются на self.app
        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/login", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                email = request.form.get("email")
                password = request.form.get("password")
                action = request.form.get("action")

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
                        session['user'] = {'id': user['id'], 'email': user['email'], 'user_type': user['user_type']}

                        if user['user_type'] == "organization": return redirect(url_for("organizations.dashboard"))
                        if user['user_type'] == "student": return redirect(url_for("students.dashboard"))
                        if user['user_type'] == "university": return redirect(url_for("universities.dashboard"))

                    return render_template("login.html", error="Неправильный email или пароль")

            return render_template("login.html")

        @self.app.route("/logout")
        def logout():
            session.pop("user", None)
            return redirect(url_for("index"))

    def run(self):
        """Запускает веб-сервер."""
        self.app.run(
            host=self.config.get_server_host(),
            port=self.config.get_server_port(),
            debug=True
        )