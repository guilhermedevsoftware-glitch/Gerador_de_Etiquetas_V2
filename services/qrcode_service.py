"""
Serviço responsável por gerar imagens de QR Code (PNG) utilizando a
biblioteca qrcode.
"""
import os
import uuid
import qrcode

GENERATED_DIR = os.path.join("static", "generated")


def _garantir_diretorio():
    os.makedirs(GENERATED_DIR, exist_ok=True)


def montar_conteudo_qrcode(produto):
    """Monta o texto que será codificado no QR Code a partir de um Produto."""
    return (
        f"Produto: {produto.nome}\n"
        f"Codigo: {produto.codigo_interno}\n"
        f"Preco: {produto.preco_formatado()}"
    )


def gerar_qrcode(conteudo):
    """
    Gera uma imagem PNG de QR Code com o conteúdo informado e retorna
    o caminho relativo (dentro de /static).
    """
    _garantir_diretorio()

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(conteudo)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    nome_arquivo = f"qrcode_{uuid.uuid4().hex}.png"
    caminho = os.path.join(GENERATED_DIR, nome_arquivo)
    img.save(caminho)

    return caminho.replace("\\", "/")
