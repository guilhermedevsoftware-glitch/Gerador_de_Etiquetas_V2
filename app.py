"""
Gerador de Etiquetas - MVP
Aplicação principal Flask.

Execução:
    python app.py
"""
import os
from datetime import date, timedelta

from flask import Flask, render_template
from flask_login import LoginManager

from extensions import db, login_manager

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def criar_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-dev-gerador-etiquetas")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

    db.init_app(app)
    login_manager.init_app(app)

    # Garante que a pasta de arquivos gerados (barcodes/qrcodes/pdfs) existe
    os.makedirs(os.path.join(BASE_DIR, "static", "generated"), exist_ok=True)

    from models.usuario import Usuario

    @login_manager.user_loader
    def carregar_usuario(usuario_id):
        return Usuario.query.get(int(usuario_id))

    # ---- Blueprints ----
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.produtos import produtos_bp
    from routes.etiquetas import etiquetas_bp
    from routes.modelos import modelos_bp
    from routes.usuarios import usuarios_bp
    from routes.historico import historico_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(etiquetas_bp)
    app.register_blueprint(modelos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(historico_bp)

    # ---- Tratadores de erro ----
    @app.errorhandler(403)
    def acesso_negado(_e):
        return render_template("erro.html", codigo=403, mensagem="Você não tem permissão para acessar essa página."), 403

    @app.errorhandler(404)
    def nao_encontrado(_e):
        return render_template("erro.html", codigo=404, mensagem="Página não encontrada."), 404

    @app.errorhandler(500)
    def erro_interno(_e):
        return render_template("erro.html", codigo=500, mensagem="Ocorreu um erro interno no servidor."), 500

    with app.app_context():
        db.create_all()
        _seed_dados_iniciais()

    return app


def _seed_dados_iniciais():
    """Cria usuário administrador, modelos e produtos de exemplo na primeira execução."""
    from models.usuario import Usuario
    from models.produto import Produto
    from models.modelo_etiqueta import ModeloEtiqueta

    if not Usuario.query.filter_by(email="admin@admin.com").first():
        admin = Usuario(
            nome="Administrador",
            email="admin@admin.com",
            perfil="administrador",
            status="ativo",
        )
        admin.set_senha("Admin@123")
        db.session.add(admin)

    if ModeloEtiqueta.query.count() == 0:
        db.session.add_all([
            ModeloEtiqueta(nome="Etiqueta Simples", tipo="simples", largura=60, altura=40, status="ativo"),
            ModeloEtiqueta(nome="Etiqueta com Código de Barras", tipo="barcode", largura=70, altura=40, status="ativo"),
            ModeloEtiqueta(nome="Etiqueta com QR Code", tipo="qrcode", largura=50, altura=50, status="ativo"),
        ])

    if Produto.query.count() == 0:
        validade = (date.today() + timedelta(days=365)).strftime("%d/%m/%Y")
        produtos_exemplo = [
            ("001", "Arroz 5KG", "Alimentos", "Exemplo", "7891234567890", 29.90, "L001"),
            ("002", "Feijão 1KG", "Alimentos", "Exemplo", "7891234567891", 8.50, "L002"),
            ("003", "Café 500G", "Alimentos", "Exemplo", "7891234567892", 14.90, "L003"),
            ("004", "Açúcar 1KG", "Alimentos", "Exemplo", "7891234567893", 5.30, "L004"),
            ("005", "Macarrão 500G", "Alimentos", "Exemplo", "7891234567894", 4.20, "L005"),
        ]
        for codigo, nome, categoria, marca, cod_barras, preco, lote in produtos_exemplo:
            db.session.add(Produto(
                codigo_interno=codigo,
                nome=nome,
                descricao=f"Produto de exemplo - {nome}",
                categoria=categoria,
                marca=marca,
                codigo_barras=cod_barras,
                preco=preco,
                unidade="UN",
                lote=lote,
                validade=validade,
                status="ativo",
            ))

    db.session.commit()


app = criar_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
