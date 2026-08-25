from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default="usuario")  # administrador | usuario
    status = db.Column(db.String(10), nullable=False, default="ativo")   # ativo | inativo
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    impressoes = db.relationship("Impressao", backref="usuario", lazy=True)

    def set_senha(self, senha_pura):
        self.senha_hash = generate_password_hash(senha_pura)

    def checar_senha(self, senha_pura):
        return check_password_hash(self.senha_hash, senha_pura)

    @property
    def is_admin(self):
        return self.perfil == "administrador"

    @property
    def is_active(self):  # sobrescreve UserMixin: usuário inativo não consegue logar
        return self.status == "ativo"

    def __repr__(self):
        return f"<Usuario {self.email}>"
