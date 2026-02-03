from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QStackedWidget,QApplication,QWidget,QComboBox,QVBoxLayout, QLabel,QLineEdit,QGridLayout, QHBoxLayout, QPushButton, QMainWindow
import sys
#from discord_bot.bot import aviso

app = QApplication(sys.argv)

#paleta de cor
cores = {
    "fundo": "#060721",
    "botao": "#080d3f",
    "texto": "#ffffff"
}
class janela_principal(QWidget):
    def __init__(self):
        super().__init__()

        self.stacked = QStackedWidget()
# 
        self.tela_controller = Controller(self.ir_anotacoes,self.ir_configs)
        self.tela_anotacoes = anotacoes(self.voltar)
        self.tela_configs = configs(self.voltar)

        self.stacked.addWidget(self.tela_controller)
        self.stacked.addWidget(self.tela_anotacoes)
        self.stacked.addWidget(self.tela_configs)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked)
        self.setLayout(layout)

    def ir_anotacoes(self):
        self.stacked.setCurrentWidget(self.tela_anotacoes)
    def ir_configs(self):
        self.stacked.setCurrentWidget(self.tela_configs)

    def voltar(self):
        self.stacked.setCurrentWidget(self.tela_controller)


#telas
class Controller(QWidget):
    #telas
    def __init__(self, ir_anotacoes,ir_configs):
        super().__init__()
        self.ir_anotacoes = ir_anotacoes
        self.ir_configs = ir_configs
        self.setAutoFillBackground(True)
        layout_base = QGridLayout()
        menu_topo = QHBoxLayout()
        controle_cam = QGridLayout()
        user_input_baixo = QHBoxLayout()
        #cores
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(cores["fundo"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(cores["texto"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(cores["texto"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(cores["texto"]))

        app.setPalette(palette)
        #stylesheet glonal aos que nn funcionaram
        app.setStyleSheet(f"""
        QPushButton {{
            background-color: {cores['botao']};
        }}
        QPushButton:hover {{
            background-color: #0a1370;
        }}
        QPushButton:pressed {{
            background-color: #020426;
        }}
        QPushButton:checked {{
            background-color: #1a3dff;
        }}
                          """)

        #menus
        
        #topo
        alertar_inicio_fim = QPushButton("Iniciar sessão")
        alertar_inicio_fim.setCheckable(True)
        alertar_inicio_fim.clicked.connect(self.sessao)
        anotacoes = QPushButton("Anotações")
        confs = QPushButton("Configurações")
        menu_topo.addWidget(alertar_inicio_fim)
        menu_topo.addWidget(anotacoes)
        menu_topo.addWidget(confs)
        anotacoes.clicked.connect(self.ir_anotacoes)
        confs.clicked.connect(self.ir_configs)
        #anotacoes.clicked.connect(self.menu_confs)
        
        #controle geral
        lista_efeitos_sonoros = QComboBox()
        lista_efeitos_sonoros.setStyleSheet(f"background-color:{cores['botao']};")
        lista_efeitos_sonoros.addItem("sem efeito sonoro")
        lista_efeitos_sonoros.addItem("placehoarder 1")
        lista_efeitos_sonoros.addItem("placehoarder 2")
        lista_efeitos_sonoros.addItem("placehoarder 3")
        controle_som = QPushButton("aplicar efeito sonoro")

        lista_efeitos_cam = QComboBox()
        lista_efeitos_cam.setStyleSheet(f"background-color:{cores['botao']};")
        #criar arquivo de efeitos de camera e carregar + efeitos padrão 
        lista_efeitos_cam.addItem("sem efeito na camera")
        lista_efeitos_cam.addItem("placehoarder 1")
        lista_efeitos_cam.addItem("placehoarder 2")
        lista_efeitos_cam.addItem("placehoarder 3")
        controle_cam_button = QPushButton("aplicar efeito na camera")
        controle_cam_button.setCheckable(True)
        
        controle_cam.addWidget(lista_efeitos_sonoros, 1, 1)
        controle_cam.addWidget(controle_som, 2, 1)
        controle_cam.addWidget(lista_efeitos_cam, 3, 1)
        controle_cam.addWidget(controle_cam_button, 4, 1)
        
        #baixo
        #adicionar/mandar aviso especifico
        self.input_bot = QLabel("digite a mensagem a ser enviada pelo bot")
        self.input_bot.setStyleSheet(f"color: {cores['texto']};")
        self.input = QLineEdit()
        self.input.setStyleSheet(f"background-color:{cores['botao']};")
        mandar_msg_bot = QPushButton("mandar")
        mandar_msg_bot.clicked.connect(self.bot_msg)#enviar via botão
        self.input.returnPressed.connect(self.bot_msg)#enviar via enter

        #o layout linha e coluna
        layout_base.addLayout(menu_topo, 1, 1)
        layout_base.addLayout(controle_cam, 2, 3)
        layout_base.addLayout(user_input_baixo, 3, 1)
        user_input_baixo.addWidget(self.input_bot)
        user_input_baixo.addWidget(self.input)
        user_input_baixo.addWidget(mandar_msg_bot)
        self.setLayout(layout_base)
    #funções botoes
    #alerta de sessão ao jogadores
    def sessao(self, checked):
        if checked:
            Controller.iniciar_sessao(self)
        else:
            Controller.finalizar_sessao(self)
    def iniciar_sessao(self):
        print("avisando o inicio da sessão!")
        self.setWindowTitle("singularidade rpg controller sessão iniciada")
        #bot.aviso("inicio")
    def finalizar_sessao(self):
        print("avisando o finalizando da sessão!")
        self.setWindowTitle("singularidade rpg controller sessão finalizada")
        #bot.aviso("fim")
    #interação bot via app
    def bot_msg(self):
        u_input = self.input.text()
        print(u_input)
class anotacoes(QWidget):
    def __init__(self, voltar):
        super().__init__()
        self.voltar = voltar
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Anotações"))
        btn = QPushButton("Voltar")
        btn.clicked.connect(voltar)
        layout.addWidget(btn)
        self.setLayout(layout)

class configs(QWidget):
    def __init__(self, voltar):
        super().__init__()
        self.voltar = voltar
        layout = QVBoxLayout()

        layout.addWidget(QLabel("configurações"))
        btn = QPushButton("Voltar")
        btn.clicked.connect(voltar)
        layout.addWidget(btn)
        self.setLayout(layout)
#loop do app/janela
window = janela_principal()
window.show()
app.exec()