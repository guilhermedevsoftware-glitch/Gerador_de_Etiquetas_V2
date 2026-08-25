from datetime import datetime
from extensions import db


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    codigo_interno = db.Column(db.String(30), nullable=False, unique=True, index=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.String(300))
    categoria = db.Column(db.String(80))
    marca = db.Column(db.String(80))
    codigo_barras = db.Column(db.String(50))
    preco = db.Column(db.Float, nullable=False, default=0.0)
    unidade = db.Column(db.String(10), default="UN")
    lote = db.Column(db.String(50))
    validade = db.Column(db.String(20))  # armazenado como texto dd/mm/aaaa para simplicidade do MVP
    status = db.Column(db.String(10), nullable=False, default="ativo")  # ativo | inativo
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    itens_impressao = db.relationship("ItemImpressao", backref="produto", lazy=True)

    def preco_formatado(self):
        return f"R$ {self.preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def __repr__(self):
        return f"<Produto {self.codigo_interno} - {self.nome}>"
