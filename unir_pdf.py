# -*- coding: utf-8 -*-
"""
Unir PDF - junta vários PDFs na ordem que você definir.

- Arraste e solte PDFs na janela (ou use "Adicionar").
- Reordene arrastando na lista, ou com os botões Subir / Descer.
- Remover / Limpar.
- "Unir e Salvar..." gera o PDF final na ordem exibida.
"""
import os
import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QFileDialog,
    QMessageBox, QAbstractItemView, QFrame, QSizePolicy,
)

from pypdf import PdfWriter

APP_TITULO = "Unir PDF"

QSS = """
QWidget { background: #f5f6f8; color: #1b1f24;
          font-family: "Segoe UI", Roboto, Arial, sans-serif; font-size: 13px; }
QLabel#Titulo { font-size: 19px; font-weight: 700; color: #0C447C; }
QLabel#Sub { color: #5c6672; }
QLabel#Rodape { color: #5c6672; }
QLabel#Credito { color: #97a1ac; font-size: 12px; padding-top: 2px; }
QFrame#Card { background: #ffffff; border: 1px solid #e2e6ea; border-radius: 12px; }
QListWidget {
    background: #ffffff; border: 1px dashed #cfd6dd; border-radius: 10px;
    padding: 6px; outline: 0;
}
QListWidget::item { padding: 8px 10px; border-radius: 6px; margin: 1px 2px; }
QListWidget::item:selected { background: #E6F1FB; color: #0a4a80; }
QListWidget[vazio="true"] { color: #97a1ac; }
QPushButton {
    background: #ffffff; border: 1px solid #cfd6dd; border-radius: 8px;
    padding: 7px 14px; color: #1b1f24;
}
QPushButton:hover { background: #eef2f6; }
QPushButton:pressed { background: #e2e8ee; }
QPushButton:disabled { color: #b6bec7; border-color: #e6eaee; }
QPushButton#Primario {
    background: #185FA5; border: 1px solid #185FA5; color: #ffffff;
    font-weight: 600; padding: 9px 20px;
}
QPushButton#Primario:hover { background: #14538f; }
QPushButton#Primario:pressed { background: #0C447C; }
QPushButton#Perigo { color: #A32D2D; }
QPushButton#Perigo:hover { background: #FCEBEB; }
"""


def unir_pdfs(caminhos, saida):
    """Une os PDFs na ordem dada e grava em `saida`."""
    w = PdfWriter()
    for c in caminhos:
        w.append(c)
    with open(saida, "wb") as f:
        w.write(f)
    return saida


class ListaPdfs(QListWidget):
    """Lista que aceita arquivos soltos do Explorer e reordenação interna."""

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(False)
        self.setUniformItemSizes(True)
        self.setToolTip("Arraste PDFs para cá.\nArraste um item para reordenar, ou use Subir/Descer.")

    # --- drop de arquivos externos -------------------------------------
    def _tem_arquivos(self, e):
        return e.mimeData().hasUrls() and any(
            u.isLocalFile() for u in e.mimeData().urls()
        )

    def dragEnterEvent(self, e):
        if self._tem_arquivos(e):
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if self._tem_arquivos(e):
            e.acceptProposedAction()
        else:
            super().dragMoveEvent(e)

    def dropEvent(self, e):
        if self._tem_arquivos(e):
            e.acceptProposedAction()
            caminhos = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
            self.window().adicionar_arquivos(caminhos)
        else:
            super().dropEvent(e)
            self.window().atualizar_estado()


class Janela(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITULO)
        self.setMinimumSize(640, 520)
        self.resize(720, 600)

        self.lista = ListaPdfs()

        raiz = QWidget()
        self.setCentralWidget(raiz)
        v = QVBoxLayout(raiz)
        v.setContentsMargins(20, 18, 20, 16)
        v.setSpacing(12)

        # cabeçalho
        titulo = QLabel("Unir PDF")
        titulo.setObjectName("Titulo")
        sub = QLabel("Arraste os PDFs, ajuste a ordem e una em um só arquivo.")
        sub.setObjectName("Sub")
        v.addWidget(titulo)
        v.addWidget(sub)

        # card com a lista + dica
        card = QFrame()
        card.setObjectName("Card")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(10, 10, 10, 10)
        cv.setSpacing(0)
        self.lista.setMinimumHeight(240)
        cv.addWidget(self.lista)
        self.dica = QLabel("Solte arquivos PDF aqui")
        self.dica.setAlignment(Qt.AlignCenter)
        self.dica.setStyleSheet("color:#97a1ac; padding:26px;")
        cv.addWidget(self.dica)
        v.addWidget(card, 1)

        # linha de ações
        acoes = QHBoxLayout()
        acoes.setSpacing(8)
        self.btn_add = QPushButton("Adicionar…")
        self.btn_add.clicked.connect(self.abrir_dialogo)
        self.btn_subir = QPushButton("Subir")
        self.btn_subir.clicked.connect(lambda: self.mover(-1))
        self.btn_descer = QPushButton("Descer")
        self.btn_descer.clicked.connect(lambda: self.mover(1))
        self.btn_remover = QPushButton("Remover")
        self.btn_remover.setObjectName("Perigo")
        self.btn_remover.clicked.connect(self.remover)
        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.clicked.connect(self.limpar)

        acoes.addWidget(self.btn_add)
        acoes.addSpacing(6)
        acoes.addWidget(self.btn_subir)
        acoes.addWidget(self.btn_descer)
        acoes.addSpacing(6)
        acoes.addWidget(self.btn_remover)
        acoes.addWidget(self.btn_limpar)
        acoes.addStretch(1)
        self.btn_unir = QPushButton("Unir e Salvar…")
        self.btn_unir.setObjectName("Primario")
        self.btn_unir.clicked.connect(self.unir)
        acoes.addWidget(self.btn_unir)
        v.addLayout(acoes)

        self.rodape = QLabel("Nenhum arquivo")
        self.rodape.setObjectName("Rodape")
        v.addWidget(self.rodape)

        credito = QLabel("Criado pelo CB César  ·  Licença MIT")
        credito.setObjectName("Credito")
        v.addWidget(credito)

        # atalhos
        QAction("Adicionar", self, shortcut=QKeySequence.Open, triggered=self.abrir_dialogo).setParent(self)
        QAction("Remover", self, shortcut=QKeySequence.Delete, triggered=self.remover).setParent(self)
        QAction("Subir", self, shortcut=QKeySequence("Ctrl+Up"), triggered=lambda: self.mover(-1)).setParent(self)
        QAction("Descer", self, shortcut=QKeySequence("Ctrl+Down"), triggered=lambda: self.mover(1)).setParent(self)

        self.lista.itemSelectionChanged.connect(self.atualizar_estado)
        self.atualizar_estado()

    # --- dados ---------------------------------------------------------
    def caminhos(self):
        return [self.lista.item(i).data(Qt.UserRole) for i in range(self.lista.count())]

    def adicionar_arquivos(self, caminhos):
        pdfs, ignorados = [], []
        for c in caminhos:
            if os.path.isdir(c):
                for f in sorted(os.listdir(c)):
                    if f.lower().endswith(".pdf"):
                        pdfs.append(os.path.join(c, f))
            elif c.lower().endswith(".pdf"):
                pdfs.append(c)
            else:
                ignorados.append(os.path.basename(c))
        for c in pdfs:
            it = QListWidgetItem(os.path.basename(c))
            it.setData(Qt.UserRole, c)
            it.setToolTip(c)
            self.lista.addItem(it)
        self.atualizar_estado()
        if ignorados:
            QMessageBox.information(
                self, APP_TITULO,
                "Ignorados (não são PDF):\n• " + "\n• ".join(ignorados[:10])
            )

    def abrir_dialogo(self):
        arqs, _ = QFileDialog.getOpenFileNames(
            self, "Selecione os PDFs", "", "Arquivos PDF (*.pdf)"
        )
        if arqs:
            self.adicionar_arquivos(arqs)

    def remover(self):
        for it in self.lista.selectedItems():
            self.lista.takeItem(self.lista.row(it))
        self.atualizar_estado()

    def limpar(self):
        if self.lista.count() and QMessageBox.question(
            self, APP_TITULO, "Remover todos os arquivos da lista?"
        ) != QMessageBox.Yes:
            return
        self.lista.clear()
        self.atualizar_estado()

    def mover(self, delta):
        itens = self.lista.selectedItems()
        if not itens:
            return
        linhas = sorted(self.lista.row(it) for it in itens)
        if delta < 0:
            if linhas[0] == 0:
                return
            alvo = [l - 1 for l in linhas]
        else:
            if linhas[-1] == self.lista.count() - 1:
                return
            alvo = [l + 1 for l in linhas]
        for it, novo in zip(itens, alvo):
            atual = self.lista.row(it)
            self.lista.takeItem(atual)
            self.lista.insertItem(novo, it)
            it.setSelected(True)
        self.atualizar_estado()

    # --- estado da UI --------------------------------------------------
    def atualizar_estado(self):
        n = self.lista.count()
        self.dica.setVisible(n == 0)
        self.lista.setVisible(True)
        sel = self.lista.selectedItems()
        tem = bool(sel)
        linhas = sorted(self.lista.row(it) for it in sel) if sel else []
        self.btn_subir.setEnabled(tem and linhas[0] > 0)
        self.btn_descer.setEnabled(tem and linhas[-1] < n - 1)
        self.btn_remover.setEnabled(tem)
        self.btn_limpar.setEnabled(n > 0)
        self.btn_unir.setEnabled(n >= 2)
        if n == 0:
            self.rodape.setText("Nenhum arquivo")
        elif n == 1:
            self.rodape.setText("1 arquivo — adicione mais um para unir")
        else:
            self.rodape.setText(f"{n} arquivos — serão unidos nesta ordem")

    # --- unir ----------------------------------------------------------
    def unir(self):
        caminhos = self.caminhos()
        if len(caminhos) < 2:
            return
        sugestao = os.path.join(
            os.path.dirname(caminhos[0]), "unido.pdf"
        )
        saida, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF unido", sugestao, "Arquivo PDF (*.pdf)"
        )
        if not saida:
            return
        if not saida.lower().endswith(".pdf"):
            saida += ".pdf"
        try:
            unir_pdfs(caminhos, saida)
        except Exception as e:
            QMessageBox.critical(self, APP_TITULO, f"Falha ao unir:\n\n{e}")
            return
        QMessageBox.information(
            self, APP_TITULO,
            f"Pronto!\n\n{len(caminhos)} arquivos unidos em:\n{saida}"
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITULO)
    app.setStyleSheet(QSS)
    janela = Janela()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
