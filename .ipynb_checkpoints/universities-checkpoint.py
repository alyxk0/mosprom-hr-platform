from flask import Blueprint, render_template, session, redirect, url_for

universities_bp = Blueprint("universities", __name__)

@universities_bp.route("/university/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
        
    #Здесь фичи
    
    return render_template("university_dashboard.html", user=session["user"])