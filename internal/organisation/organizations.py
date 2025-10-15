from flask import Blueprint, render_template, session, redirect, url_for

organizations_bp = Blueprint("organizations", __name__)

@organizations_bp.route("/organization/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    #Здесь сделать основное короче
    
    return render_template("organization_dashboard.html", user=session["user"])