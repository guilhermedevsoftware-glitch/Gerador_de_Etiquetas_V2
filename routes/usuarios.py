from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models.usuario import Usuario

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def _somente_admin():
    if not current_user.is_admin:
        abort(403)


@usuarios_bp.route("/")
@login_required
def listar():
    _somente_admin()
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template("usuarios/listar.html", usuarios=usuarios)


@usuarios_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    _somente_admin()

    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        confirmar_senha = request.form.get("confirmar_senha") or ""
        perfil = request.form.get("perfil") or "usuario"
        status = request.form.get("status") or "ativo"

        erros = _validar_usuario(nome, email, senha, confirmar_senha, exigir_senha=True)

        if erros:
            for e in erros:
                flash(e, "danger")
            return render_template("usuarios/form.html", usuario=None, modo="novo")

        usuario = Usuario(nome=nome, email=email, perfil=perfil, status=status)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/form.html", usuario=None, modo="novo")


@usuarios_bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
def editar(usuario_id):
    _somente_admin()
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        confirmar_senha = request.form.get("confirmar_senha") or ""
        perfil = request.form.get("perfil") or "usuario"
        status = request.form.get("status") or "ativo"

        exigir_senha = bool(senha or confirmar_senha)
        erros = _validar_usuario(
            nome, email, senha, confirmar_senha,
            exigir_senha=exigir_senha, usuario_id=usuario_id
        )

        if usuario.id == current_user.id and status == "inativo":
            erros.append("Você não pode desativar o seu próprio usuário.")
        if usuario.id == current_user.id and perfil != "administrador" and current_user.is_admin:
            erros.append("Você não pode remover seu próprio perfil de administrador.")

        if erros:
            for e in erros:
                flash(e, "danger")
            return render_template("usuarios/form.html", usuario=usuario, modo="editar")

        usuario.nome = nome
        usuario.email = email
        usuario.perfil = perfil
        usuario.status = status
        if senha:
            usuario.set_senha(senha)

        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/form.html", usuario=usuario, modo="editar")


@usuarios_bp.route("/<int:usuario_id>/excluir", methods=["POST"])
@login_required
def excluir(usuario_id):
    _somente_admin()
    usuario = Usuario.query.get_or_404(usuario_id)

    if usuario.id == current_user.id:
        flash("Você não pode excluir o seu próprio usuário.", "danger")
        return redirect(url_for("usuarios.listar"))

    try:
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuário excluído com sucesso!", "success")
    except Exception:
        db.session.rollback()
        flash(
            "Não é possível excluir esse usuário pois ele já possui etiquetas geradas. "
            "Desative-o em vez de excluir.",
            "danger",
        )
    return redirect(url_for("usuarios.listar"))


def _validar_usuario(nome, email, senha, confirmar_senha, exigir_senha=False, usuario_id=None):
    erros = []
    if not nome:
        erros.append("O nome é obrigatório.")

    if not email or "@" not in email or "." not in email.split("@")[-1]:
        erros.append("Informe um e-mail válido.")
    else:
        consulta = Usuario.query.filter_by(email=email)
        if usuario_id:
            consulta = consulta.filter(Usuario.id != usuario_id)
        if consulta.first():
            erros.append("Já existe um usuário cadastrado com esse e-mail.")

    if exigir_senha:
        if not senha or len(senha) < 6:
            erros.append("A senha deve possuir no mínimo 6 caracteres.")
        elif senha != confirmar_senha:
            erros.append("A confirmação de senha não confere.")

    return erros
