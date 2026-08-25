from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    session, jsonify, send_file
)
from flask_login import login_required, current_user

from extensions import db
from models.produto import Produto
from models.modelo_etiqueta import ModeloEtiqueta
from models.impressao import Impressao, ItemImpressao
from services.pdf_service import gerar_pdf_etiquetas
from services.barcode_service import gerar_barcode
from services.qrcode_service import gerar_qrcode, montar_conteudo_qrcode

etiquetas_bp = Blueprint("etiquetas", __name__, url_prefix="/etiquetas")

CARRINHO_SESSAO = "carrinho_etiquetas"
MODELO_SESSAO = "modelo_etiquetas_id"


def _obter_carrinho():
    return session.get(CARRINHO_SESSAO, {})


def _salvar_carrinho(carrinho):
    session[CARRINHO_SESSAO] = carrinho
    session.modified = True


def _itens_do_carrinho():
    """Retorna lista de tuplas (Produto, quantidade) a partir da sessão."""
    carrinho = _obter_carrinho()
    itens = []
    for produto_id_str, quantidade in carrinho.items():
        produto = Produto.query.get(int(produto_id_str))
        if produto:
            itens.append((produto, quantidade))
    return itens


@etiquetas_bp.route("/gerar", methods=["GET"])
@login_required
def gerar():
    itens = _itens_do_carrinho()
    quantidade_total = sum(q for _p, q in itens)
    modelos = ModeloEtiqueta.query.filter_by(status="ativo").order_by(ModeloEtiqueta.nome).all()
    modelo_selecionado_id = session.get(MODELO_SESSAO)

    return render_template(
        "etiquetas/gerar.html",
        itens=itens,
        quantidade_total=quantidade_total,
        modelos=modelos,
        modelo_selecionado_id=modelo_selecionado_id,
    )


@etiquetas_bp.route("/buscar-produto")
@login_required
def buscar_produto():
    termo = request.args.get("q", "").strip()
    consulta = Produto.query.filter_by(status="ativo")
    if termo:
        like = f"%{termo}%"
        consulta = consulta.filter(
            db.or_(Produto.nome.ilike(like), Produto.codigo_interno.ilike(like))
        )
    produtos = consulta.order_by(Produto.nome).limit(15).all()
    return jsonify([
        {
            "id": p.id,
            "codigo_interno": p.codigo_interno,
            "nome": p.nome,
            "preco": p.preco_formatado(),
        }
        for p in produtos
    ])


@etiquetas_bp.route("/adicionar", methods=["POST"])
@login_required
def adicionar():
    produto_id = request.form.get("produto_id", type=int)
    quantidade = request.form.get("quantidade", type=int)

    if not produto_id or not Produto.query.get(produto_id):
        flash("Selecione um produto válido.", "danger")
        return redirect(url_for("etiquetas.gerar"))

    if not quantidade or quantidade <= 0:
        flash("A quantidade deve ser maior que zero.", "danger")
        return redirect(url_for("etiquetas.gerar"))

    carrinho = _obter_carrinho()
    chave = str(produto_id)
    carrinho[chave] = carrinho.get(chave, 0) + quantidade
    _salvar_carrinho(carrinho)

    flash("Produto adicionado à lista de etiquetas.", "success")
    return redirect(url_for("etiquetas.gerar"))


@etiquetas_bp.route("/remover/<int:produto_id>", methods=["POST"])
@login_required
def remover(produto_id):
    carrinho = _obter_carrinho()
    carrinho.pop(str(produto_id), None)
    _salvar_carrinho(carrinho)
    flash("Item removido da lista.", "info")
    return redirect(url_for("etiquetas.gerar"))


@etiquetas_bp.route("/limpar", methods=["POST"])
@login_required
def limpar():
    _salvar_carrinho({})
    session.pop(MODELO_SESSAO, None)
    flash("Lista de etiquetas limpa.", "info")
    return redirect(url_for("etiquetas.gerar"))


@etiquetas_bp.route("/visualizar", methods=["POST"])
@login_required
def visualizar():
    modelo_id = request.form.get("modelo_id", type=int)
    itens = _itens_do_carrinho()

    if not itens:
        flash("Adicione ao menos um produto antes de visualizar.", "danger")
        return redirect(url_for("etiquetas.gerar"))

    modelo = ModeloEtiqueta.query.get(modelo_id) if modelo_id else None
    if not modelo:
        flash("Selecione um modelo de etiqueta.", "danger")
        return redirect(url_for("etiquetas.gerar"))

    session[MODELO_SESSAO] = modelo.id

    # Gera imagem auxiliar (barcode/qrcode) apenas para o primeiro produto, para a prévia
    produto_exemplo, _qtd = itens[0]
    imagem_extra = None
    if modelo.tipo == "barcode":
        codigo = produto_exemplo.codigo_barras or produto_exemplo.codigo_interno
        imagem_extra = gerar_barcode(codigo, tipo="code128")
    elif modelo.tipo == "qrcode":
        imagem_extra = gerar_qrcode(montar_conteudo_qrcode(produto_exemplo))

    quantidade_total = sum(q for _p, q in itens)

    return render_template(
        "etiquetas/preview.html",
        itens=itens,
        modelo=modelo,
        produto_exemplo=produto_exemplo,
        imagem_extra=imagem_extra,
        quantidade_total=quantidade_total,
    )


@etiquetas_bp.route("/gerar-pdf", methods=["POST"])
@login_required
def gerar_pdf():
    modelo_id = request.form.get("modelo_id", type=int) or session.get(MODELO_SESSAO)
    itens = _itens_do_carrinho()

    if not itens:
        flash("Adicione ao menos um produto antes de gerar o PDF.", "danger")
        return redirect(url_for("etiquetas.gerar"))

    modelo = ModeloEtiqueta.query.get(modelo_id) if modelo_id else None
    if not modelo:
        flash("Selecione um modelo de etiqueta válido.", "danger")
        return redirect(url_for("etiquetas.gerar"))

    caminho_pdf = gerar_pdf_etiquetas(itens, modelo)

    quantidade_total = sum(q for _p, q in itens)
    impressao = Impressao(
        usuario_id=current_user.id,
        modelo_id=modelo.id,
        quantidade_total=quantidade_total,
        arquivo_pdf=caminho_pdf,
        data_hora=datetime.utcnow(),
    )
    db.session.add(impressao)
    db.session.flush()  # obtém impressao.id antes do commit

    for produto, quantidade in itens:
        db.session.add(ItemImpressao(
            impressao_id=impressao.id,
            produto_id=produto.id,
            quantidade=quantidade,
        ))

    db.session.commit()

    _salvar_carrinho({})
    session.pop(MODELO_SESSAO, None)

    flash("Etiquetas geradas com sucesso!", "success")
    return redirect(url_for("historico.baixar_pdf", impressao_id=impressao.id))
