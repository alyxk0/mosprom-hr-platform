from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import random

students_bp = Blueprint("students", __name__)

# --- ЗАГЛУШКИ ДЛЯ ИИ-ПОМОЩНИКА (DEMO) ---
demo_vacancies = [
    {"title": "Junior Python Developer", "company": "ОЭЗ Технополис", "salary": "от 80 000 руб."},
    {"title": "Data Scientist (Стажер)", "company": "Микрон", "salary": "не указана"},
    {"title": "Инженер-конструктор", "company": "Ангстрем", "salary": "от 120 000 руб."},
]

ai_knowledge_base = {
    "стажировк": "Стажировки обычно проходят летом. Вы можете подать заявку через ваш ВУЗ в разделе 'Учебным заведениям'.",
    "резюме": "Чтобы ваше резюме заметили, подробно опишите ваши учебные проекты и стек технологий.",
    "технополис": "ОЭЗ «Технополис Москва» объединяет ведущие высокотехнологичные компании.",
}

@students_bp.route("/student/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("student_dashboard.html", user=session["user"], vacancies=demo_vacancies)

@students_bp.route("/api/ai_assistant", methods=["POST"])
def ai_assistant():
    # Простая логика бота на основе ключевых слов
    data = request.get_json()
    user_message = data.get("message", "").lower()
    
    response = ""
    
    # 1. Поиск ответа в базе знаний
    found_answer = False
    for key, value in ai_knowledge_base.items():
        if key in user_message:
            response = value
            found_answer = True
            break
            
    # 2. Если спрашивают про работу/вакансии, предлагаем случайную
    if "ваканси" in user_message or "работ" in user_message or "ищу" in user_message:
        vac = random.choice(demo_vacancies)
        response = f"Я нашел интересную вакансию для вас: <b>{vac['title']}</b> в компании {vac['company']} ({vac['salary']}). Хотите откликнуться?"
        found_answer = True

    # 3. Дефолтный ответ
    if not found_answer:
        greeting = ["Привет!", "Здравствуйте!", "Готов помочь."]
        if any(x in user_message for x in ["привет", "здравствуй", "хай"]):
            response = f"{random.choice(greeting)} Я ИИ-помощник платформы. Спросите меня о вакансиях или стажировках."
        else:
            response = "Извините, я пока учусь и не понял ваш запрос. Попробуйте спросить о 'вакансиях' или 'стажировках'."

    return jsonify({"response": response})