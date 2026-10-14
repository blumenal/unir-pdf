# -*- coding: utf-8 -*-
"""Gera PDFs de amostra, testa a união e renderiza a janela (offscreen)."""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QMarginsF
from PySide6.QtGui import QPdfWriter, QPainter, QFont, QPageSize, QPageLayout
from PySide6.QtWidgets import QApplication

import unir_pdf
from unir_pdf import unir_pdfs, Janela, QSS

BASE = os.path.dirname(os.path.abspath(__file__))
AMOSTRAS = os.path.join(BASE, "amostras")
os.makedirs(AMOSTRAS, exist_ok=True)


def criar_pdf(caminho, texto):
    w = QPdfWriter(caminho)
    w.setPageSize(QPageSize(QPageSize.A4))
    w.setResolution(300)
    w.setPageMargins(QMarginsF(0, 0, 0, 0))
    p = QPainter(w)
    p.setFont(QFont("Arial", 60, QFont.Bold))
    p.drawText(600, 1600, texto)
    p.end()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)

    # 1) amostras
    nomes = ["Documento A", "Documento B", "Documento C"]
    arquivos = []
    for i, nome in enumerate(nomes):
        c = os.path.join(AMOSTRAS, f"{i+1}-{nome.replace(' ', '_')}.pdf")
        criar_pdf(c, nome)
        arquivos.append(c)
        print("criado:", os.path.basename(c))

    # 2) uniao
    saida = os.path.join(AMOSTRAS, "unido.pdf")
    unir_pdfs(arquivos, saida)
    from pypdf import PdfReader
    r = PdfReader(saida)
    print("unido.pdf paginas:", len(r.pages), "(esperado 3)")
    for i, pg in enumerate(r.pages):
        t = (pg.extract_text() or "").strip().replace("\n", " ")
        print(f"  pagina {i+1}: {t!r}")

    # 3) render da janela
    j = Janela()
    j.resize(760, 640)
    j.adicionar_arquivos(arquivos)
    j.show()
    app.processEvents()
    j.grab().save(os.path.join(BASE, "preview_janela.png"))
    print("preview_janela.png salvo")
    # estado vazio tambem
    j.limpar_sem_confirmar() if hasattr(j, "limpar_sem_confirmar") else None


if __name__ == "__main__":
    main()
