from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required

from extensions import db
from models.produto import Produto
from models.modelo_etiqueta import ModeloEtiqueta
from models.impressao import Impressao

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    total_produtos = Produto.query.count()
    total_modelos = ModeloEtiqueta.query.count()
    total_etiquetas = db.session.query(
        db.func.coalesce(db.func.sum(Impressao.quantidade_total), 0)
    ).scalar()

    hoje_inicio = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    hoje_fim = hoje_inicio + timedelta(days=1)
    total_hoje = db.session.query(
        db.func.coalesce(db.func.sum(Impressao.quantidade_total), 0)
    ).filter(Impressao.data_hora >= hoje_inicio, Impressao.data_hora < hoje_fim).scalar()

    ultimas = (
        Impressao.query.order_by(Impressao.data_hora.desc()).limit(8).all()
    )

    return render_template(
        "dashboard.html",
        total_produtos=total_produtos,
        total_modelos=total_modelos,
        total_etiquetas=total_etiquetas,
        total_hoje=total_hoje,
        ultimas=ultimas,
    )
