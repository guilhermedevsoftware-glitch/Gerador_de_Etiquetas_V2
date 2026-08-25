from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models.usuario import Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""

        erro = None
        if not email or not senha:
            erro = "Informe e-mail e senha."
        else:
            usuario = Usuario.query.filter_by(email=email).first()
            if not usuario or not usuario.checar_senha(senha):
                erro = "E-mail ou senha inválidos."
            elif usuario.status != "ativo":
                erro = "Este usuário está inativo. Contate o administrador."

        if erro:
            flash(erro, "danger")
            return render_template("login.html", email=email)

        login_user(usuario)
        flash(f"Bem-vindo(a), {usuario.nome}!", "success")
        proxima = request.args.get("next")
        return redirect(proxima or url_for("dashboard.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))
