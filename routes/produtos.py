from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.produto import Produto

produtos_bp = Blueprint("produtos", __name__, url_prefix="/produtos")

POR_PAGINA = 10


@produtos_bp.route("/")
@login_required
def listar():
    termo = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    status = request.args.get("status", "").strip()
    pagina = request.args.get("pagina", 1, type=int)

    consulta = Produto.query

    if termo:
        like = f"%{termo}%"
        consulta = consulta.filter(
            db.or_(
                Produto.nome.ilike(like),
                Produto.codigo_interno.ilike(like),
                Produto.codigo_barras.ilike(like),
            )
        )
    if categoria:
        consulta = consulta.filter(Produto.categoria == categoria)
    if status:
        consulta = consulta.filter(Produto.status == status)

    consulta = consulta.order_by(Produto.nome.asc())
    paginacao = consulta.paginate(page=pagina, per_page=POR_PAGINA, error_out=False)

    categorias = [
        c[0] for c in db.session.query(Produto.categoria).distinct() if c[0]
    ]

    return render_template(
        "produtos/listar.html",
        produtos=paginacao.items,
        paginacao=paginacao,
        termo=termo,
        categoria=categoria,
        status=status,
        categorias=categorias,
    )


def _validar_produto(form, produto_id=None):
    erros = []
    codigo_interno = (form.get("codigo_interno") or "").strip()
    nome = (form.get("nome") or "").strip()
    preco_raw = (form.get("preco") or "0").replace(",", ".").strip()

    if not codigo_interno:
        erros.append("O código interno é obrigatório.")
    else:
        consulta = Produto.query.filter_by(codigo_interno=codigo_interno)
        if produto_id:
            consulta = consulta.filter(Produto.id != produto_id)
        if consulta.first():
            erros.append("Já existe um produto cadastrado com esse código interno.")

    if not nome:
        erros.append("O nome do produto é obrigatório.")

    try:
        preco = float(preco_raw)
        if preco < 0:
            erros.append("O preço não pode ser negativo.")
    except ValueError:
        preco = 0.0
        erros.append("Informe um preço válido.")

    codigo_barras = (form.get("codigo_barras") or "").strip()
    if codigo_barras and not codigo_barras.isdigit():
        erros.append("O código de barras deve conter apenas números.")

    return erros, {
        "codigo_interno": codigo_interno,
        "nome": nome,
        "descricao": (form.get("descricao") or "").strip(),
        "categoria": (form.get("categoria") or "").strip(),
        "marca": (form.get("marca") or "").strip(),
        "codigo_barras": codigo_barras,
        "preco": preco,
        "unidade": (form.get("unidade") or "UN").strip(),
        "lote": (form.get("lote") or "").strip(),
        "validade": (form.get("validade") or "").strip(),
        "status": form.get("status") or "ativo",
    }


@produtos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        erros, dados = _validar_produto(request.form)
        if erros:
            for e in erros:
                flash(e, "danger")
            return render_template("produtos/form.html", produto=dados, modo="novo")

        produto = Produto(**dados)
        db.session.add(produto)
        db.session.commit()
        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for("produtos.listar"))

    return render_template("produtos/form.html", produto=None, modo="novo")


@produtos_bp.route("/<int:produto_id>/editar", methods=["GET", "POST"])
@login_required
def editar(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    if request.method == "POST":
        erros, dados = _validar_produto(request.form, produto_id=produto_id)
        if erros:
            for e in erros:
                flash(e, "danger")
            dados["id"] = produto_id
            return render_template("produtos/form.html", produto=dados, modo="editar")

        for campo, valor in dados.items():
            setattr(produto, campo, valor)
        db.session.commit()
        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for("produtos.listar"))

    return render_template("produtos/form.html", produto=produto, modo="editar")


@produtos_bp.route("/<int:produto_id>")
@login_required
def detalhes(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    return render_template("produtos/detalhes.html", produto=produto)


@produtos_bp.route("/<int:produto_id>/excluir", methods=["POST"])
@login_required
def excluir(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    try:
        db.session.delete(produto)
        db.session.commit()
        flash("Produto excluído com sucesso!", "success")
    except Exception:
        db.session.rollback()
        flash(
            "Não foi possível excluir esse produto pois ele já possui etiquetas geradas. "
            "Desative-o em vez de excluir.",
            "danger",
        )
    return redirect(url_for("produtos.listar"))


@produtos_bp.route("/<int:produto_id>/status", methods=["POST"])
@login_required
def alternar_status(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    produto.status = "inativo" if produto.status == "ativo" else "ativo"
    db.session.commit()
    flash(f"Produto {'ativado' if produto.status == 'ativo' else 'desativado'} com sucesso!", "success")
    return redirect(url_for("produtos.listar"))
