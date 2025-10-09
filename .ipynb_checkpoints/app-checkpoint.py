from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


SUPABASE_URL = "https://cdeefekmliclmxexfprq.supabase.co"
SUPABASE_KEY  =  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNkZWVmZWttbGljbG14ZXhmcHJxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk5MDUyMjksImV4cCI6MjA3NTQ4MTIyOX0.s7Qf-deUh4d-PqJA8TvPWD1i5rB8s5Smxin0xamc_KI"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


from organizations import organizations_bp
from students import students_bp
from universities import universities_bp

app.register_blueprint(organizations_bp)
app.register_blueprint(students_bp)
app.register_blueprint(universities_bp)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        action = request.form.get("action")

        if action == "register":
            user_type = request.form.get("user_type")
            
            response = supabase.table('users').select('id').eq('email', email).execute()
            if response.data:
                return render_template("login.html", error="Пользователь с таким email уже существует")

            password_hash = generate_password_hash(password)

            try:
                supabase.table('users').insert({
                    'email': email,
                    'password_hash': password_hash,
                    'user_type': user_type
                }).execute()
                return render_template("login.html", success="Регистрация успешна! Теперь вы можете войти.")
            except Exception as e:
                return render_template("login.html", error=f"Ошибка сервера: {e}")

        elif action == "login":
            response = supabase.table('users').select('*').eq('email', email).execute()
            
            if not response.data:
                return render_template("login.html", error="Неправильный email или пароль")

            user = response.data[0]
            
            if check_password_hash(user['password_hash'], password):
                session['user'] = {
                    'id': user['id'],
                    'email': user['email'],
                    'user_type': user['user_type']
                }

                # Редирект в зависимости от роли
                if user['user_type'] == "organization":
                    return redirect(url_for("organizations.dashboard"))
                elif user['user_type'] == "student":
                    return redirect(url_for("students.dashboard"))
                elif user['user_type'] == "university":
                    return redirect(url_for("universities.dashboard"))
            else:
                return render_template("login.html", error="Неправильный email или пароль")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)