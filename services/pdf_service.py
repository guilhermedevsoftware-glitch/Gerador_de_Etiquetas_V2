"""
Serviço responsável por montar o PDF com as etiquetas, utilizando ReportLab.
As etiquetas são desenhadas em grade dentro de uma página A4, respeitando
(aproximadamente) a largura/altura configurada no modelo escolhido.
"""
import os
import uuid

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from services.barcode_service import gerar_barcode
from services.qrcode_service import gerar_qrcode, montar_conteudo_qrcode

GENERATED_DIR = os.path.join("static", "generated")
NOME_EMPRESA = "MINHA EMPRESA"

MARGEM = 10 * mm
ESPACAMENTO = 3 * mm


def _garantir_diretorio():
    os.makedirs(GENERATED_DIR, exist_ok=True)


def _desenhar_etiqueta(c, x, y, largura, altura, produto, modelo, imagem_extra=None):
    """Desenha uma única etiqueta no canvas, na posição (x, y) = canto inferior esquerdo."""
    # Moldura da etiqueta
    c.setLineWidth(0.5)
    c.rect(x, y, largura, altura)

    centro_x = x + largura / 2
    topo = y + altura - 4 * mm

    if modelo.tipo == "simples":
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(centro_x, topo, NOME_EMPRESA)
        c.setFont("Helvetica", 8)
        c.drawCentredString(centro_x, topo - 6 * mm, produto.nome[:28])
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(centro_x, topo - 13 * mm, produto.preco_formatado())
        c.setFont("Helvetica", 7)
        c.drawCentredString(centro_x, y + 3 * mm, produto.codigo_interno)

    elif modelo.tipo == "barcode":
        c.setFont("Helvetica", 8)
        c.drawCentredString(centro_x, topo, produto.nome[:28])
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(centro_x, topo - 6 * mm, produto.preco_formatado())
        if imagem_extra and os.path.exists(imagem_extra):
            img_largura = largura - 8 * mm
            img_altura = 10 * mm
            c.drawImage(
                imagem_extra,
                x + (largura - img_largura) / 2,
                y + 5 * mm,
                width=img_largura,
                height=img_altura,
                preserveAspectRatio=True,
                mask="auto",
            )
        c.setFont("Helvetica", 6)
        c.drawCentredString(centro_x, y + 2 * mm, produto.codigo_interno)

    elif modelo.tipo == "qrcode":
        c.setFont("Helvetica", 8)
        c.drawCentredString(centro_x, topo, produto.nome[:24])
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(centro_x, topo - 6 * mm, produto.preco_formatado())
        if imagem_extra and os.path.exists(imagem_extra):
            lado = min(largura, altura) * 0.45
            c.drawImage(
                imagem_extra,
                centro_x - lado / 2,
                y + 3 * mm,
                width=lado,
                height=lado,
                preserveAspectRatio=True,
                mask="auto",
            )
        c.setFont("Helvetica", 6)
        c.drawCentredString(centro_x, y + 1.5 * mm, produto.codigo_interno)


def gerar_pdf_etiquetas(itens, modelo):
    """
    itens: lista de tuplas (produto, quantidade)
    modelo: instância de ModeloEtiqueta

    Retorna o caminho relativo (dentro de /static) do arquivo PDF gerado.
    """
    _garantir_diretorio()

    largura_etq = max(modelo.largura, 25) * mm
    altura_etq = max(modelo.altura, 15) * mm

    largura_pagina, altura_pagina = A4

    colunas = max(1, int((largura_pagina - 2 * MARGEM + ESPACAMENTO) // (largura_etq + ESPACAMENTO)))
    linhas = max(1, int((altura_pagina - 2 * MARGEM + ESPACAMENTO) // (altura_etq + ESPACAMENTO)))
    por_pagina = colunas * linhas

    nome_arquivo = f"etiquetas_{uuid.uuid4().hex}.pdf"
    caminho = os.path.join(GENERATED_DIR, nome_arquivo)

    c = canvas.Canvas(caminho, pagesize=A4)

    # Pré-gera as imagens auxiliares (barcode/qrcode) uma única vez por produto
    imagens_cache = {}
    for produto, _qtd in itens:
        if modelo.tipo == "barcode" and produto.id not in imagens_cache:
            codigo = produto.codigo_barras or produto.codigo_interno
            imagens_cache[produto.id] = gerar_barcode(codigo, tipo="code128")
        elif modelo.tipo == "qrcode" and produto.id not in imagens_cache:
            conteudo = montar_conteudo_qrcode(produto)
            imagens_cache[produto.id] = gerar_qrcode(conteudo)

    posicao_atual = 0
    for produto, quantidade in itens:
        imagem_extra = imagens_cache.get(produto.id)
        for _ in range(int(quantidade)):
            indice_na_pagina = posicao_atual % por_pagina
            if posicao_atual > 0 and indice_na_pagina == 0:
                c.showPage()

            col = indice_na_pagina % colunas
            lin = indice_na_pagina // colunas

            x = MARGEM + col * (largura_etq + ESPACAMENTO)
            # desenha de cima para baixo
            y = altura_pagina - MARGEM - altura_etq - lin * (altura_etq + ESPACAMENTO)

            _desenhar_etiqueta(c, x, y, largura_etq, altura_etq, produto, modelo, imagem_extra)
            posicao_atual += 1

    c.save()
    return caminho.replace("\\", "/")
