from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPalette, QIcon, QSurfaceFormat, QShortcut, QKeySequence
from PySide6.QtWidgets import *#deste jeitop facilita a visualização do que sera importado
from opengl_widget import OpenGLWidget
import sys

#funcionalidades(bot,teclado,etc)
#from discord_bot.bot import aviso

# Configurar OpenGL ANTES de criar QApplication (necessário no PySide6)
fmt = QSurfaceFormat()
fmt.setVersion(3, 3)  # OpenGL 3.3
fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
fmt.setDepthBufferSize(24)
fmt.setStencilBufferSize(8)
fmt.setSamples(4)  # Anti-aliasing
QSurfaceFormat.setDefaultFormat(fmt)

app = QApplication(sys.argv)
#paleta de cor
cores = {
    "fundo": "#060721",
    "botao": "#080d3f",
    "texto": "#ffffff"
}
#iniciando/configurando janelas
class janela_principal(QWidget):
    def __init__(self):
        self.tela_anterior = None
        super().__init__()
        self.stacked = QStackedWidget()
        self.tela_dm = Controller(self.ir_anotacoes,self.ir_configs,self.ir_mapas,self.ir_salas)
        self.salas = Salas(self.voltar,self.entrar_sala)
        self.visitantes = Visitante(self.voltar,self.ir_configs,self.ir_salas,self.ir_anotacoes)
        self.tela_anotacoes = anotacoes(self.voltar)
        self.tela_mapas = Mapas(self.voltar)
        self.tela_configs = configs(self.voltar)

        self.stacked.addWidget(self.tela_dm)
        self.stacked.addWidget(self.tela_anotacoes)
        self.stacked.addWidget(self.salas)
        self.stacked.addWidget(self.visitantes)
        self.stacked.addWidget(self.tela_mapas)
        self.stacked.addWidget(self.tela_configs)

        self.setWindowIcon(QIcon("app/src/ui/imgs/dado-20-lados.png"))
        self.setWindowTitle("singularidade rpg controller sessão inativa")

        layout = QVBoxLayout()
        layout.addWidget(self.stacked)
        self.setLayout(layout)
        
        self.setup_atalhos()
    #atalhos globais
    def setup_atalhos(self):
        # Atalho para sair (Ctrl+Q)
        atalho_sair = QShortcut(QKeySequence("Ctrl+Q"), self)
        atalho_sair.setContext(Qt.ShortcutContext.ApplicationShortcut)
        atalho_sair.activated.connect(QApplication.quit)
    #ir para outras telas
    def ir_para(self, widget):
        self.tela_anterior = self.stacked.currentWidget()
        self.stacked.setCurrentWidget(widget)
    def entrar_sala(self):
        self.ir_para(self.visitantes)
    def ir_salas(self):
        self.ir_para(self.salas)
    def ir_anotacoes(self):
        self.ir_para(self.tela_anotacoes)
    def ir_mapas(self):
        self.ir_para(self.tela_mapas)
    def ir_configs(self):
        self.ir_para(self.tela_configs)
    def voltar(self):
        if self.tela_anterior:
            self.stacked.setCurrentWidget(self.tela_anterior)

        #trocar para voltar para o widget anterior ao invez de voltar para a tela de dm

#telas
class Salas(QWidget):
    def __init__(self, voltar,entrar_sala):
        super().__init__()
        self.voltar = voltar
        self.entrar_sala = entrar_sala
        layout_base = QGridLayout()
        configs_infos = QGridLayout()
        menu_topo = QHBoxLayout()
        menu_fundo = QHBoxLayout()

        mestrar = QPushButton("mestrar")
        mestrar.clicked.connect(voltar)
        menu_topo.addWidget(mestrar)
        entrar_numa_sala = QPushButton("entrar em uma sala")
        entrar_numa_sala.clicked.connect(entrar_sala)
        menu_fundo.addWidget(entrar_numa_sala)
        layout_base.addLayout(menu_topo,1,1)
        layout_base.addLayout(configs_infos,2,1)
        layout_base.addLayout(menu_fundo,3,1)
        self.setLayout(layout_base)
class Visitante(QWidget):
    def __init__(self,voltar,ir_configs,ir_salas,ir_anotacoes):
        super().__init__()
        #configuraççoes iniciais
        self.ir_anotacoes = ir_anotacoes
        self.ir_configs = ir_configs
        self.ir_salas = ir_salas
        self.setAutoFillBackground(True)
        layout_base = QVBoxLayout()
        menu_topo = QHBoxLayout()
        controle = QGridLayout()
        tresD_render = QHBoxLayout()
        open_gl = OpenGLWidget()
        open_gl.setFocus()#
        open_gl.setSizePolicy(QSizePolicy.Policy.Expanding,
                  QSizePolicy.Policy.Expanding)
        tresD_render.addWidget(open_gl)

        meio_tela = QHBoxLayout()
        meio_tela.addLayout(tresD_render)
        meio_tela.addLayout(controle)
        meio_tela.setStretch(0, 8)  # tresD_render
        meio_tela.setStretch(1, 2)  # controle
        #cores
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(cores["fundo"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(cores["texto"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(cores["texto"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(cores["texto"]))
        app.setPalette(palette)
        #stylesheet glonal aos que nn funcionaram
        app.setStyleSheet(f"""
        QPushButton {{background-color: {cores['botao']};}}
        QPushButton:hover {{background-color: #0a1370;}}
        QPushButton:pressed {{background-color: #020426;}}
        QPushButton:checked {{background-color: #1a3dff;}}
        """)
        #menus
        #topo
        anotacoes = QPushButton("Anotações")
        token = QPushButton("Tokens/fichas")
        confs = QPushButton("Configurações")
        sala_id_text = QLabel("ID sala:")
        sair_sala = QPushButton("Sair da sala")
        menu_topo.addWidget(anotacoes)
        menu_topo.addWidget(token)
        menu_topo.addWidget(confs)
        menu_topo.addWidget(sala_id_text)
        menu_topo.addWidget(sair_sala)
        sair_sala.clicked.connect(self.ir_salas)
        anotacoes.clicked.connect(self.ir_anotacoes)
        confs.clicked.connect(self.ir_configs)

        #controle geral
        interacao_chat = QHBoxLayout()
        chat = QLabel("add chat futuramente")
        chat.setStyleSheet(f"background-color:{cores['botao']};")
        chat_dialog = QLineEdit()
        chat_dialog.setStyleSheet(f"background-color:{cores['botao']};")
        chat_dialog_mandar = QPushButton("mandar msg")
        interacao_chat.addWidget(chat_dialog)
        interacao_chat.addWidget(chat_dialog_mandar)

        controle.addWidget(chat, 1, 1)
        controle.addLayout(interacao_chat, 2, 1)

        layout_base.addLayout(menu_topo)
        layout_base.addLayout(meio_tela)
        layout_base.setStretch(0, 1)
        layout_base.setStretch(1, 8)
        layout_base.setStretch(2, 1)
        self.setLayout(layout_base)
        #botoes que tem atalhos

#region dm
class Controller(QWidget):
    def __init__(self, ir_anotacoes,ir_configs,ir_mapas,ir_salas):
        super().__init__()
        #configuraççoes iniciais
        self.ir_anotacoes = ir_anotacoes
        self.ir_configs = ir_configs
        self.ir_mapas = ir_mapas
        self.ir_salas = ir_salas
        self.setAutoFillBackground(True)
        layout_base = QVBoxLayout()
        menu_topo = QHBoxLayout()
        controle = QGridLayout()
        tresD_render = QHBoxLayout()
        open_gl = OpenGLWidget()
        open_gl.setFocus()#
        open_gl.setSizePolicy(QSizePolicy.Policy.Expanding,
                  QSizePolicy.Policy.Expanding)
        tresD_render.addWidget(open_gl)

        meio_tela = QHBoxLayout()
        meio_tela.addLayout(tresD_render)
        meio_tela.addLayout(controle)
        meio_tela.setStretch(0, 8)  # tresD_render
        meio_tela.setStretch(1, 2)  # controle
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
        QPushButton {{background-color: {cores['botao']};}}
        QPushButton:hover {{background-color: #0a1370;}}
        QPushButton:pressed {{background-color: #020426;}}
        QPushButton:checked {{background-color: #1a3dff;}}
        """)
        #menus
        #topo
        alertar_inicio_fim = QPushButton("Iniciar sessão")
        
        alertar_inicio_fim.setCheckable(True)
        alertar_inicio_fim.clicked.connect(self.sessao)
        anotacoes = QPushButton("Anotações")
        mapas = QPushButton("Controle de mapas")
        token = QPushButton("Tokens/fichas")
        gerenciar_pessoas = QPushButton("Gerenciar pessoas")
        confs = QPushButton("Configurações")
        sala_id_text = QLabel("ID sala:")
        sair_sala = QPushButton("Sair da sala")
        menu_topo.addWidget(alertar_inicio_fim)
        menu_topo.addWidget(anotacoes)
        menu_topo.addWidget(token)
        menu_topo.addWidget(mapas)
        menu_topo.addWidget(gerenciar_pessoas)
        menu_topo.addWidget(confs)
        menu_topo.addWidget(sala_id_text)
        menu_topo.addWidget(sair_sala)
        sair_sala.clicked.connect(self.ir_salas)
        mapas.clicked.connect(self.ir_mapas)
        anotacoes.clicked.connect(self.ir_anotacoes)
        confs.clicked.connect(self.ir_configs)

        #controle geral
        #efeitos
        add_efeitos_sonoros = QPushButton("adicionar efeitos sonoros")
        lista_efeitos_sonoros = QComboBox()
        lista_efeitos_sonoros.setStyleSheet(f"background-color:{cores['botao']};")
        lista_efeitos_sonoros.addItem("sem efeito sonoro")
        lista_efeitos_sonoros.addItem("placehoarder 1")
        lista_efeitos_sonoros.addItem("placehoarder 2")
        lista_efeitos_sonoros.addItem("placehoarder 3")
        controle_som = QPushButton("aplicar efeito sonoro")

        add_efeitos_cam = QPushButton("adicionar efeitos de camera")
        lista_efeitos_cam = QComboBox()
        lista_efeitos_cam.setStyleSheet(f"background-color:{cores['botao']};")
        lista_efeitos_cam.addItem("sem efeito na camera")
        lista_efeitos_cam.addItem("placehoarder 1")
        lista_efeitos_cam.addItem("placehoarder 2")
        lista_efeitos_cam.addItem("placehoarder 3")
        controle_cam_button = QPushButton("aplicar efeito na camera")
        controle_cam_button.setCheckable(True)

        #mundo e personagens
        lista_mapa = QComboBox()
        lista_mapa.setStyleSheet(f"background-color:{cores['botao']};")
        lista_mapa.addItem("nenhum mapa")
        lista_mapa.addItem("placehoarder 1")
        lista_mapa.addItem("placehoarder 2")
        lista_mapa.addItem("placehoarder 3")
        controle_mapa_button = QPushButton("trocar mapa")
        controle_mapa_button.setCheckable(True)

        lista_inimigos = QComboBox()
        lista_inimigos.setStyleSheet(f"background-color:{cores['botao']};")
        lista_inimigos.addItem("nenhum inimigo selecionado")
        lista_inimigos.addItem("placehoarder 1")
        lista_inimigos.addItem("placehoarder 2")
        lista_inimigos.addItem("placehoarder 3")
        add_inimigo = QPushButton("adicionar inimigo")

        lista_npcs = QComboBox()
        lista_npcs.setStyleSheet(f"background-color:{cores['botao']};")
        lista_npcs.addItem("nenhum npc selecionado")
        lista_npcs.addItem("placehoarder 1")
        lista_npcs.addItem("placehoarder 2")
        lista_npcs.addItem("placehoarder 3")
        add_npc = QPushButton("adicionar npc")

        interacao_chat = QHBoxLayout()
        chat = QLabel("add chat futuramente")
        chat.setStyleSheet(f"background-color:{cores['botao']};")
        chat_dialog = QLineEdit()
        chat_dialog.setStyleSheet(f"background-color:{cores['botao']};")
        chat_dialog_mandar = QPushButton("mandar msg")
        interacao_chat.addWidget(chat_dialog)
        interacao_chat.addWidget(chat_dialog_mandar)

        #adicionando no layout
        controle.addWidget(add_efeitos_sonoros, 1, 1)
        controle.addWidget(lista_efeitos_sonoros, 2, 1)
        controle.addWidget(controle_som, 3, 1)
        controle.addWidget(add_efeitos_cam, 4, 1)
        controle.addWidget(lista_efeitos_cam, 5, 1)
        controle.addWidget(controle_cam_button, 6, 1)

        controle.addWidget(lista_mapa, 7, 1)
        controle.addWidget(controle_mapa_button, 8, 1)
        controle.addWidget(lista_inimigos, 9, 1)
        controle.addWidget(add_inimigo, 10, 1)
        controle.addWidget(lista_npcs, 11, 1)
        controle.addWidget(add_npc, 12, 1)
        controle.addWidget(chat, 13, 1)
        controle.addLayout(interacao_chat, 14, 1)
        
        #baixo
        #adicionar/mandar aviso especifico
        self.input_bot = QLabel("digite a mensagem a ser enviada pelo bot")
        self.input_bot.setStyleSheet(f"color: {cores['texto']};")
        self.input = QLineEdit()
        self.input.setStyleSheet(f"background-color:{cores['botao']};")
        mandar_msg_bot = QPushButton("mandar")
        mandar_msg_bot.clicked.connect(self.bot_msg)#enviar via botão
        self.input.returnPressed.connect(self.bot_msg)#enviar via enter

        layout_base.addLayout(menu_topo)
        layout_base.addLayout(meio_tela)
        layout_base.addLayout(user_input_baixo)
        layout_base.setStretch(0, 1)
        layout_base.setStretch(1, 8)
        layout_base.setStretch(2, 1)
        user_input_baixo.addWidget(self.input_bot)
        user_input_baixo.addWidget(self.input)
        user_input_baixo.addWidget(mandar_msg_bot)
        self.setLayout(layout_base)
        #botoes que tem atalhos
        self.btn_sessao = alertar_inicio_fim

        self.setup_atalhos()
    #atalhos locais
    def setup_atalhos(self):
        # Atalho para alternar sessão (Esc)
        atalho_sessao = QShortcut(QKeySequence("Esc"), self)
        atalho_sessao.setContext(Qt.ShortcutContext.ApplicationShortcut)
        atalho_sessao.activated.connect(self.toggle_sessao)
    
    def toggle_sessao(self):
        # Encontrar o botão de sessão na tela DM
        btn = self.btn_sessao
        btn.setChecked(not btn.isChecked())
        btn.clicked.emit(btn.isChecked())

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
    #interação bot via app (sendo algo mais especifico)
    def bot_msg(self):
        u_input = self.input.text()
        print(u_input)
#endregion dm
#region mapas
class Mapas(QWidget):
    def __init__(self, voltar):
        super().__init__()
        self.voltar = voltar
        layout_base = QGridLayout()
        mapas = QHBoxLayout()
        controles_anotacoes = QVBoxLayout()
        menu_topo = QHBoxLayout()
        menu_fundo = QHBoxLayout()
        #controles anotações
        nv_pasta = QPushButton("novo mapa")
        apagar_anotacoes = QPushButton("apagar mapa")
        controles_anotacoes.addWidget(nv_pasta)
        controles_anotacoes.addWidget(apagar_anotacoes)
        mapas.addLayout(controles_anotacoes)
        #anotação
        mapas_layout = OpenGLWidget()
        mapas_layout.setFocus()

        mapas_layout.setMinimumSize(500,100)
        mapas_layout.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
            )#so funciona aceitando 2 parametros
        mapas.addWidget(mapas_layout)
        #resto do menu
        salvar_button = QPushButton("salvar")
        menu_fundo.addWidget(salvar_button)
        voltar_button = QPushButton("Voltar")
        voltar_button.clicked.connect(voltar)
        menu_topo.addWidget(voltar_button)
        layout_base.addLayout(menu_topo,1,1)
        layout_base.addLayout(mapas,2,1)
        layout_base.addLayout(menu_fundo,3,1)
        self.setLayout(layout_base)
#endregion mapas
#region anotaçoes
class anotacoes(QWidget):
    def __init__(self, voltar):
        super().__init__()
        self.voltar = voltar
        layout_base = QGridLayout()
        anotacao = QHBoxLayout()
        controles_anotacoes = QVBoxLayout()
        menu_topo = QHBoxLayout()
        menu_fundo = QHBoxLayout()
        #controles anotações
        nv_pasta = QPushButton("nova pasta")
        apagar_anotacoes = QPushButton("apagar anotacoes")
        controles_anotacoes.addWidget(nv_pasta)
        controles_anotacoes.addWidget(apagar_anotacoes)
        anotacao.addLayout(controles_anotacoes)
        #anotação
        anotacao_input = QTextEdit()
        anotacao_input.setStyleSheet(f"color:black;")
        anotacao_input.setMinimumSize(500,100)
        anotacao_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
            )#so funciona aceitando 2 parametros
        anotacao.addWidget(anotacao_input)
        #resto do menu
        salvar_button = QPushButton("salvar")
        menu_fundo.addWidget(salvar_button)
        voltar_button = QPushButton("Voltar")
        voltar_button.clicked.connect(voltar)
        menu_topo.addWidget(voltar_button)
        layout_base.addLayout(menu_topo,1,1)
        layout_base.addLayout(anotacao,2,1)
        layout_base.addLayout(menu_fundo,3,1)
        self.setLayout(layout_base)
#endregion anotaçoes
#region configs
class configs(QWidget):
    def __init__(self, voltar):
        super().__init__()
        self.voltar = voltar
        layout_base = QGridLayout()
        configs_infos = QGridLayout()
        menu_topo = QHBoxLayout()
        menu_fundo = QHBoxLayout()

        voltar_button = QPushButton("Voltar")
        voltar_button.clicked.connect(voltar)
        menu_topo.addWidget(voltar_button)
        apagar_dados = QPushButton("excluir dados salvos")
        apagar_dados.setStyleSheet(f":hover {{background-color: #fc0303;}}")
        menu_fundo.addWidget(apagar_dados)
        layout_base.addLayout(menu_topo,1,1)
        layout_base.addLayout(configs_infos,2,1)
        layout_base.addLayout(menu_fundo,3,1)
        self.setLayout(layout_base)
#endregion configs
#region detalhes finais
#loop do app/janela
window = janela_principal()
window.show()
sys.exit(app.exec())