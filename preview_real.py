# -*- coding: utf-8 -*-
"""Renderiza a janela real (plataforma windows) e salva previews."""
import os, sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from unir_pdf import Janela, QSS

BASE = os.path.dirname(os.path.abspath(__file__))
AMOSTRAS = os.path.join(BASE, "amostras")
arqs = [os.path.join(AMOSTRAS, f) for f in sorted(os.listdir(AMOSTRAS))
        if f.lower().endswith(".pdf") and "unido" not in f]

app = QApplication(sys.argv)
app.setStyleSheet(QSS)
j = Janela()
j.resize(760, 640)
j.adicionar_arquivos(arqs)
j.show()


def shot():
    j.grab().save(os.path.join(BASE, "preview_real.png"))
    j.lista.setCurrentRow(1)
    app.processEvents()
    j.grab().save(os.path.join(BASE, "preview_real_sel.png"))
    print("previews salvos")
    app.quit()


QTimer.singleShot(1600, shot)
app.exec()
