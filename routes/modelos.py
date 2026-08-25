from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.modelo_etiqueta import ModeloEtiqueta

modelos_bp = Blueprint("modelos", __name__, url_prefix="/modelos")


def _somente_admin():
    if not current_user.is_admin:
        flash("Apenas administradores podem gerenciar modelos de etiqueta.", "warning")
        return False
    return True


@modelos_bp.route("/")
@login_required
def listar():
    modelos = ModeloEtiqueta.query.order_by(ModeloEtiqueta.nome.asc()).all()
    return render_template("modelos/listar.html", modelos=modelos)


@modelos_bp.route("/<int:modelo_id>/editar", methods=["GET", "POST"])
@login_required
def editar(modelo_id):
    if not _somente_admin():
        return redirect(url_for("modelos.listar"))

    modelo = ModeloEtiqueta.query.get_or_404(modelo_id)

    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        largura = request.form.get("largura", type=float)
        altura = request.form.get("altura", type=float)
        status = request.form.get("status") or "ativo"

        erros = []
        if not nome:
            erros.append("O nome do modelo é obrigatório.")
        if not largura or largura <= 0:
            erros.append("Informe uma largura válida (mm).")
        if not altura or altura <= 0:
            erros.append("Informe uma altura válida (mm).")

        if erros:
            for e in erros:
                flash(e, "danger")
            return render_template("modelos/form.html", modelo=modelo)

        modelo.nome = nome
        modelo.largura = largura
        modelo.altura = altura
        modelo.status = status
        db.session.commit()
        flash("Modelo atualizado com sucesso!", "success")
        return redirect(url_for("modelos.listar"))

    return render_template("modelos/form.html", modelo=modelo)


@modelos_bp.route("/<int:modelo_id>/status", methods=["POST"])
@login_required
def alternar_status(modelo_id):
    if not _somente_admin():
        return redirect(url_for("modelos.listar"))

    modelo = ModeloEtiqueta.query.get_or_404(modelo_id)
    modelo.status = "inativo" if modelo.status == "ativo" else "ativo"
    db.session.commit()
    flash("Status do modelo atualizado.", "success")
    return redirect(url_for("modelos.listar"))
