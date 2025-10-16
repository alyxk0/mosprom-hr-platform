# internal/student/controllers.py
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from entity.resume import Resume

students_bp = Blueprint('students', __name__, url_prefix='/student')

def _get_student_service():
    """
    Возвращает экземпляр StudentService, вложенный в app.
    Мы предполагаем, что при инициализации Server мы положили
    current_app.student_service = StudentService(storage)
    """
    svc = getattr(current_app, "student_service", None)
    if svc is None:
        from internal.student.service import StudentService
        svc = StudentService(current_app.db)
        current_app.student_service = svc
    return svc


@students_bp.route('/dashboard')
def dashboard():
    """
    Точка входа для студента после логина.
    Перенаправляет на основную страницу - поиск работы.
    """
    user = session.get('user')
    if not user:
        flash("Нужно войти в систему", "warning")
        return redirect(url_for('login'))

    return redirect(url_for('students.search_jobs'))


@students_bp.route('/search_jobs')
def search_jobs():
    """
    Отображает главную страницу студента - поиск вакансий.
    """
    user = session.get('user')
    if not user or user.get('user_type') != 'student':
        flash("Доступ только для студентов", "warning")
        return redirect(url_for('login'))

    # ВРЕМЕННЫЕ ДАННЫЕ ДЛЯ ОТОБРАЖЕНИЯ ВАКАНСИЙ
    # В будущем вы будете получать их из базы данных
    demo_vacancies = [
        {'title': 'Python-разработчик (Junior)', 'company': 'ООО "ТехноСтарт"', 'salary': '80 000 руб.'},
        {'title': 'Frontend-разработчик (React)', 'company': 'Digital Innovations', 'salary': '95 000 руб.'},
        {'title': 'Аналитик данных', 'company': 'Data Insights', 'salary': '110 000 руб.'},
        {'title': 'Стажер в отдел QA', 'company': 'Quality Assurance Co.', 'salary': '45 000 руб.'}
    ]

    # Отображаем новый шаблон для поиска работы
    return render_template('student/search_jobs.html', user=user, vacancies=demo_vacancies)


@students_bp.route('/resume', methods=['GET', 'POST'])
def resume():
    user = session.get('user')
    if not user:
        flash("Нужно войти в систему", "warning")
        return redirect(url_for('login'))

    if user.get('user_type') != 'student':
        flash("Доступ только для студентов", "danger")
        return redirect(url_for('index'))

    svc = _get_student_service()

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        summary = request.form.get('summary', '').strip()
        skills_raw = request.form.get('skills', '')
        skills = [s.strip() for s in skills_raw.split(',') if s.strip()]

        exp_companies = request.form.getlist('exp_company[]')
        exp_titles = request.form.getlist('exp_title[]')
        exp_starts = request.form.getlist('exp_start[]')
        exp_ends = request.form.getlist('exp_end[]')
        exp_descriptions = request.form.getlist('exp_description[]')

        ed_institutions = request.form.getlist('ed_institution[]')
        ed_degrees = request.form.getlist('ed_degree[]')
        ed_fields = request.form.getlist('ed_field[]')
        ed_starts = request.form.getlist('ed_start[]')
        ed_ends = request.form.getlist('ed_end[]')
        ed_descriptions = request.form.getlist('ed_description[]')

        resume_obj = Resume(
            first_name=first_name or '',
            last_name=last_name or '',
            email=user.get('email'),
            phone=None,
            summary=summary,
            skills=skills
        )

        for i in range(len(exp_companies)):
            c = exp_companies[i].strip()
            title = exp_titles[i].strip() if i < len(exp_titles) else ''
            start = exp_starts[i].strip() if i < len(exp_starts) else None
            end = exp_ends[i].strip() if i < len(exp_ends) else None
            desc = exp_descriptions[i].strip() if i < len(exp_descriptions) else None
            if not c and not title:
                continue
            resume_obj.add_experience(company=c, title=title, start=start or None, end=end or None, description=desc or None)

        for i in range(len(ed_institutions)):
            inst = ed_institutions[i].strip()
            deg = ed_degrees[i].strip() if i < len(ed_degrees) else None
            fld = ed_fields[i].strip() if i < len(ed_fields) else None
            st = ed_starts[i].strip() if i < len(ed_starts) else None
            en = ed_ends[i].strip() if i < len(ed_ends) else None
            desc = ed_descriptions[i].strip() if i < len(ed_descriptions) else None
            if not inst:
                continue
            resume_obj.add_education(institution=inst, degree=deg or None, field=fld or None, start=st or None, end=en or None, description=desc or None)

        ok = svc.save_resume(user_id=user['id'], resume=resume_obj)
        if not ok:
            flash("Ошибка при сохранении. Проверьте данные.", "danger")
            return render_template('student/resume_form.html', resume=resume_obj, user=user)

        flash("Резюме сохранено", "success")
        return redirect(url_for('students.resume'))

    # GET
    exist = svc.get_resume(user['id'])
    # Отображаем шаблон формы резюме, передавая пользователя для layout
    return render_template('student/resume_form.html', resume=exist, user=user)