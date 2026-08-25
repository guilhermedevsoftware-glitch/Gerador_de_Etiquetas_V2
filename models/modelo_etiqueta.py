from extensions import db


class ModeloEtiqueta(db.Model):
    __tablename__ = "modelos_etiqueta"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    # tipo define quais elementos aparecem na etiqueta:
    # simples  -> nome da empresa, produto, preço, código
    # barcode  -> produto, preço, código, código de barras
    # qrcode   -> produto, preço, código, qr code
    tipo = db.Column(db.String(20), nullable=False, default="simples")
    largura = db.Column(db.Float, nullable=False, default=60.0)  # em mm
    altura = db.Column(db.Float, nullable=False, default=40.0)   # em mm
    status = db.Column(db.String(10), nullable=False, default="ativo")

    impressoes = db.relationship("Impressao", backref="modelo", lazy=True)

    def __repr__(self):
        return f"<ModeloEtiqueta {self.nome}>"
