from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication,QWidget, QLabel,QLineEdit, QHBoxLayout, QPushButton, QMainWindow
import sys
#from discord_bot.bot import aviso

app = QApplication(sys.argv)
botoes = [
    "alertar_inicio_fim",
    "anotacoes"
]
telas=[
    "principal",
    "anotações"
]

class janela_principal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("singularidade rpg controller sessão inativa")
        layout = QHBoxLayout()
        #menus
        alertar_inicio_fim = QPushButton("Iniciar sessão")
        alertar_inicio_fim.setCheckable(True)
        alertar_inicio_fim.clicked.connect(self.sessao)
        anotacoes = QPushButton("trocar_menu_anotacoes")
        #adicionar/mandar aviso especifico
        self.label = QLabel("digite a mensagem a ser enviada pelo bot")
        self.input = QLineEdit()
        mandar_msg_bot = QPushButton("mandar")
        mandar_msg_bot.clicked.connect(self.bot_msg)

        anotacoes.clicked.connect(self.sessao)
        #add na tela
        layout.addWidget(alertar_inicio_fim)
        layout.addWidget(anotacoes)
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(mandar_msg_bot)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)    
    #funções botoes
    #alerta de sessão ao jogadores
    def sessao(self, checked):
        if checked:
            janela_principal.iniciar_sessao(self)
        else:
            janela_principal.finalizar_sessao(self)
    def iniciar_sessao(self):
        print("avisando o inicio da sessão!")
        self.setWindowTitle("singularidade rpg controller sessão iniciada")
        #bot.aviso("inicio")
    def finalizar_sessao(self):
        print("avisando o finalizando da sessão!")
        #bot.aviso("fim")
    #interação bot via app
    def bot_msg(self):
        u_input = self.input.text()
        print(u_input)
        #bot.aviso(u_input)
    #troca de janelas
    def trocar_menu_anotacoes():
        print("indo ao menu de anotações")
class anotacoes():
    def __init__(self):
        super().__init__()
        pass #temp enquanto nn terminar desing da outra tela

#loop do app/janela
window = janela_principal()
window.show()
app.exec()