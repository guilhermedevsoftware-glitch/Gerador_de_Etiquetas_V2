from datetime import datetime
from extensions import db


class Impressao(db.Model):
    __tablename__ = "impressoes"

    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey("modelos_etiqueta.id"), nullable=False)
    quantidade_total = db.Column(db.Integer, nullable=False, default=0)
    arquivo_pdf = db.Column(db.String(255))  # caminho relativo do PDF gerado

    itens = db.relationship(
        "ItemImpressao", backref="impressao", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Impressao {self.id} - {self.quantidade_total} etiquetas>"


class ItemImpressao(db.Model):
    __tablename__ = "itens_impressao"

    id = db.Column(db.Integer, primary_key=True)
    impressao_id = db.Column(db.Integer, db.ForeignKey("impressoes.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<ItemImpressao produto={self.produto_id} qtd={self.quantidade}>"
