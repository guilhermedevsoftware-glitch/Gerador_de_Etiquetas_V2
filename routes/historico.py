import os
from datetime import datetime

from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from extensions import db
from models.impressao import Impressao, ItemImpressao
from models.usuario import Usuario
from models.modelo_etiqueta import ModeloEtiqueta
from services.pdf_service import gerar_pdf_etiquetas

historico_bp = Blueprint("historico", __name__, url_prefix="/historico")

POR_PAGINA = 10


@historico_bp.route("/")
@login_required
def listar():
    data_inicial = request.args.get("data_inicial", "").strip()
    data_final = request.args.get("data_final", "").strip()
    usuario_id = request.args.get("usuario_id", type=int)
    modelo_id = request.args.get("modelo_id", type=int)
    pagina = request.args.get("pagina", 1, type=int)

    consulta = Impressao.query

    # Usuário comum só vê o próprio histórico
    if not current_user.is_admin:
        consulta = consulta.filter(Impressao.usuario_id == current_user.id)
    elif usuario_id:
        consulta = consulta.filter(Impressao.usuario_id == usuario_id)

    if data_inicial:
        try:
            dt_ini = datetime.strptime(data_inicial, "%Y-%m-%d")
            consulta = consulta.filter(Impressao.data_hora >= dt_ini)
        except ValueError:
            flash("Data inicial inválida.", "warning")

    if data_final:
        try:
            dt_fim = datetime.strptime(data_final, "%Y-%m-%d")
            dt_fim = dt_fim.replace(hour=23, minute=59, second=59)
            consulta = consulta.filter(Impressao.data_hora <= dt_fim)
        except ValueError:
            flash("Data final inválida.", "warning")

    if modelo_id:
        consulta = consulta.filter(Impressao.modelo_id == modelo_id)

    consulta = consulta.order_by(Impressao.data_hora.desc())
    paginacao = consulta.paginate(page=pagina, per_page=POR_PAGINA, error_out=False)

    usuarios = Usuario.query.order_by(Usuario.nome).all() if current_user.is_admin else []
    modelos = ModeloEtiqueta.query.order_by(ModeloEtiqueta.nome).all()

    return render_template(
        "historico/listar.html",
        impressoes=paginacao.items,
        paginacao=paginacao,
        usuarios=usuarios,
        modelos=modelos,
        data_inicial=data_inicial,
        data_final=data_final,
        usuario_id=usuario_id,
        modelo_id=modelo_id,
    )


def _obter_impressao_autorizada(impressao_id):
    impressao = Impressao.query.get_or_404(impressao_id)
    if not current_user.is_admin and impressao.usuario_id != current_user.id:
        abort(403)
    return impressao


@historico_bp.route("/<int:impressao_id>")
@login_required
def detalhes(impressao_id):
    impressao = _obter_impressao_autorizada(impressao_id)
    return render_template("historico/detalhes.html", impressao=impressao)


@historico_bp.route("/<int:impressao_id>/pdf")
@login_required
def baixar_pdf(impressao_id):
    impressao = _obter_impressao_autorizada(impressao_id)

    caminho = impressao.arquivo_pdf
    if not caminho or not os.path.exists(caminho):
        # Regenera o PDF caso o arquivo original não exista mais em disco
        itens = [(item.produto, item.quantidade) for item in impressao.itens if item.produto]
        if not itens:
            flash("Não foi possível localizar os produtos dessa impressão.", "danger")
            return redirect(url_for("historico.listar"))
        caminho = gerar_pdf_etiquetas(itens, impressao.modelo)
        impressao.arquivo_pdf = caminho
        db.session.commit()

    nome_download = f"etiquetas_{impressao.id}.pdf"
    return send_file(caminho, as_attachment=False, download_name=nome_download, mimetype="application/pdf")
