"""
Serviço responsável por gerar imagens de código de barras (PNG)
utilizando a biblioteca python-barcode.
"""
import os
import uuid
import barcode
from barcode.writer import ImageWriter

GENERATED_DIR = os.path.join("static", "generated")


def _garantir_diretorio():
    os.makedirs(GENERATED_DIR, exist_ok=True)


def gerar_barcode(codigo, tipo="code128"):
    """
    Gera uma imagem PNG de código de barras e retorna o caminho relativo
    (dentro de /static) para ser usado em <img src="..."> ou no PDF.

    tipo: 'code128' ou 'ean13'
    """
    _garantir_diretorio()
    codigo = str(codigo).strip()

    tipo = tipo.lower()
    if tipo == "ean13":
        # EAN13 exige 12 ou 13 dígitos numéricos; normaliza o valor recebido.
        digitos = "".join([c for c in codigo if c.isdigit()])
        if len(digitos) < 12:
            digitos = digitos.zfill(12)
        digitos = digitos[:12]
        classe_barcode = barcode.get_barcode_class("ean13")
        valor = digitos
    else:
        classe_barcode = barcode.get_barcode_class("code128")
        valor = codigo

    nome_arquivo = f"barcode_{uuid.uuid4().hex}"
    caminho_completo_sem_ext = os.path.join(GENERATED_DIR, nome_arquivo)

    writer_options = {
        "module_height": 12.0,
        "font_size": 8,
        "text_distance": 3,
        "quiet_zone": 2,
    }

    objeto = classe_barcode(valor, writer=ImageWriter())
    caminho_gerado = objeto.save(caminho_completo_sem_ext, options=writer_options)

    # Retorna caminho relativo (usando "/" para uso em templates/PDF)
    return caminho_gerado.replace("\\", "/")
