#region importacoes
#UI
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QPalette, QIcon, QSurfaceFormat, QShortcut, QKeySequence, QPixmap
from PySide6.QtWidgets import *#dps so importar os que foram utilizado para optimizar
import sys 
import json
from pathlib import Path
# Adiciona o diretório raiz do projeto ao path e permite usar partes/modulos de outras pastas do projeto
root = Path(__file__).parent.parent.parent  # root projeto
sys.path.insert(0, str(root))
#com isso achamos o modulo
from src.ui.opengl.opengl_widget import OpenGLWidget
from src.funcionalidades.comm.server import SocketServer
from src.funcionalidades.comm.client import SocketClient
#funcionalidades 

#endregion importacoes

# region app

# Configurar OpenGL ANTES de criar QApplication (necessário no PySide6)
fmt = QSurfaceFormat()
fmt.setVersion(3, 3)  # OpenGL 3.3
fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
fmt.setDepthBufferSize(24)
fmt.setStencilBufferSize(8)
fmt.setSamples(4)  # Anti-aliasing
QSurfaceFormat.setDefaultFormat(fmt)

#configurando app
app = QApplication(sys.argv)
#paleta de cor base
cores = {
    "fundo": "#060721",
    "botao": "#080d3f",
    "houver":"#0a1370",
    "ativo": "#2636e4",
    "texto": "#ffffff"
}
#Aplicar paleta
palette = QPalette()
palette.setColor(QPalette.ColorRole.Window, QColor(cores["fundo"]))
palette.setColor(QPalette.ColorRole.ButtonText, QColor(cores["texto"]))
palette.setColor(QPalette.ColorRole.WindowText, QColor(cores["texto"]))
palette.setColor(QPalette.ColorRole.Text, QColor(cores["texto"]))
app.setPalette(palette)
#stylesheet glonal/base
app.setStyleSheet(f"""
                  QLineEdit{{color:black;}}
                  QPushButton {{background-color: {cores['botao']};}}
                  QPushButton:hover {{background-color: {cores['houver']};}}
                  QPushButton:pressed {{background-color: {cores['ativo']};}}
                  QPushButton:checked {{background-color: {cores['ativo']};}}
                  QCheckBox {{
                    color: {cores['texto']};
                    spacing: 5px;
                    }}
                  QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {cores['texto']};
                    border-radius: 3px;
                    background-color: {cores['botao']};
                    }}
                  QCheckBox::indicator:checked {{
                    background-color: #1a3dff;
                    border: 2px solid {cores['ativo']};
    }}
""")
#region gerenciador de janelas
class janela_principal(QWidget):
    def __init__(self):
        super().__init__()
        self.historico_navegacao = []
        self.stacked = QStackedWidget()
        self.salas = Salas(self.mestrar,self.entrar_sala)
        self.tela_dm = Controller(self.ir_anotacoes,self.ir_configs,self.ir_mapas,self.ir_salas,self.ir_token_ficha,self.ir_gerir_pessoas)
        self.visitantes = Visitante(self.voltar,self.ir_configs,self.ir_salas,self.ir_anotacoes,self.ir_token_ficha)
        self.tela_anotacoes = anotacoes(self.voltar)
        self.tela_mapas = Mapas(self.voltar)
        self.tela_configs = configs(self.voltar)
        self.token_ficha = Token_ficha(self.voltar)
        self.gerenciar_pessoas = Gerenciar_pessoas(self.voltar)

        self.stacked.addWidget(self.salas)
        self.stacked.addWidget(self.tela_dm)
        self.stacked.addWidget(self.tela_anotacoes)
        self.stacked.addWidget(self.token_ficha)
        self.stacked.addWidget(self.gerenciar_pessoas)
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
        tela_atual = self.stacked.currentWidget()
        if tela_atual != widget:  # Só adiciona se for uma tela diferente
            self.historico_navegacao.append(tela_atual)
        self.stacked.setCurrentWidget(widget)

    def ir_gerir_pessoas(self):
        self.ir_para(self.gerenciar_pessoas)
    def ir_salas(self):
        self.ir_para(self.salas)
    def entrar_sala(self, ip, codigo):
        self.visitantes.conectar(host=ip, room_id=codigo)
        self.ir_para(self.visitantes)
    def ir_token_ficha(self):
        self.ir_para(self.token_ficha)
    def ir_anotacoes(self):
        self.ir_para(self.tela_anotacoes)
    def ir_mapas(self):
        self.ir_para(self.tela_mapas)
    def ir_configs(self):
        self.ir_para(self.tela_configs)
    def mestrar(self):
        self.tela_dm.iniciar_servidor()  # sobe o server
        self.tela_dm.conectar()          # conecta como cliente
        self.ir_para(self.tela_dm)
    def voltar(self):
        if self.historico_navegacao:
            # Volta para a última tela no histórico
            tela_anterior = self.historico_navegacao.pop()
            self.stacked.setCurrentWidget(tela_anterior)
        else:
            # Se não há histórico, volta para DM
            self.stacked.setCurrentWidget(self.tela_dm)

        #patch QThread: Destroyed while thread '' is still running
    def closeEvent(self, event):
        # Para o socket do GM
        if hasattr(self.tela_dm, 'socket') and self.tela_dm.socket:
            self.tela_dm.socket.stop()
            self.tela_dm.socket.wait()
        # Para o servidor
        if hasattr(self.tela_dm, 'servidor'):
            self.tela_dm.servidor.stop()
            self.tela_dm.servidor.wait()
        # Para o socket do jogador
        if hasattr(self.visitantes, 'socket') and self.visitantes.socket:
            self.visitantes.socket.stop()
            self.visitantes.socket.wait()
        event.accept()

class Salas(QWidget):
    #add logica de conferir se sala existe
    def __init__(self, mestrar,entrar_sala):
        super().__init__()
        self.mestrar = mestrar
        self.entrar_sala = entrar_sala
        layout_base = QGridLayout()
        layout_base.setAlignment(Qt.AlignmentFlag.AlignCenter)

        menu_topo = QHBoxLayout()
        menu_topo.setSpacing(50)# em pxx
        mestre = QVBoxLayout()
        player = QVBoxLayout()
        
        label_mestre = QLabel(self)
        mestrar_img = QPixmap('app/src/ui/imgs/dado-20-lados.png')
        label_mestre.setPixmap(mestrar_img)
        mestre.addWidget(label_mestre)
        ir_mestrar = QPushButton("mestrar")
        ir_mestrar.clicked.connect(mestrar)
        mestre.addWidget(ir_mestrar)

        label_player = QLabel(self) 
        player_img = QPixmap('app/src/ui/imgs/dado-20-lados.png')
        label_player.setPixmap(player_img)
        player.addWidget(label_player)
        self.ip_input = QLineEdit("IP do mestre")
        self.codigo_sala = QLineEdit("código da sala")
        player.addWidget(label_player)
        player.addWidget(self.ip_input)
        player.addWidget(self.codigo_sala)
        entrar_numa_sala = QPushButton("entrar em uma sala")
        player.addWidget(entrar_numa_sala)
        entrar_numa_sala.clicked.connect(self._entrar)

        menu_topo.addLayout(mestre)
        menu_topo.addLayout(player)
        layout_base.addLayout(menu_topo,1,1)
        self.setLayout(layout_base)

    def _entrar(self):
        ip = self.ip_input.text().strip()
        codigo = self.codigo_sala.text().strip()
        self.entrar_sala(ip, codigo)
#endregion gerenciador de janelas

#region Player_only
class Visitante(QWidget):
    def __init__(self,voltar,ir_configs,ir_salas,ir_anotacoes,ir_token_ficha):
        super().__init__()
        self.socket = None
        #configuraççoes iniciais
        self.ir_anotacoes = ir_anotacoes
        self.ir_token_ficha = ir_token_ficha
        self.ir_configs = ir_configs
        self.ir_salas = ir_salas
        self.setAutoFillBackground(True)
        layout_base = QVBoxLayout()
        menu_topo = QHBoxLayout()
        char_interaction = QHBoxLayout()
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
        meio_tela.setStretch(0, 6)  # tresD_render
        meio_tela.setStretch(1, 4)  # controle
        #menus
        #topo
        anotacoes = QPushButton("Anotações")
        token = QPushButton("Tokens/fichas")
        confs = QPushButton("Configurações")
        
        sala_id_text = QLabel(f"ID sala:")
        sair_sala = QPushButton("Sair da sala")
        menu_topo.addWidget(anotacoes)
        menu_topo.addWidget(token)
        menu_topo.addWidget(confs)
        menu_topo.addWidget(sala_id_text)
        menu_topo.addWidget(sair_sala)
        sair_sala.clicked.connect(self.ir_salas)
        token.clicked.connect(self.ir_token_ficha)
        anotacoes.clicked.connect(self.ir_anotacoes)
        confs.clicked.connect(self.ir_configs)

        #controle geral
        interacao_chat = QHBoxLayout()
        self.chat_label = QTextEdit()
        self.chat_label.setReadOnly(True)
        self.chat_label.setStyleSheet(f"background-color:{cores['botao']};")

        interacao_chat = QHBoxLayout()
        self.chat_dialog = QLineEdit()
        self.chat_dialog.setStyleSheet(f"background-color:{cores['botao']};")
        chat_dialog_mandar = QPushButton("mandar msg")
        chat_dialog_mandar.clicked.connect(self.enviar_msg)
        interacao_chat.addWidget(self.chat_dialog)
        interacao_chat.addWidget(chat_dialog_mandar)

        controle.addWidget(self.chat_label, 1, 1)   # linha 1: só o chat
        controle.addLayout(interacao_chat, 2, 1)

        char_interaction.addWidget(QLabel("adicionar controle de personagem dps que terminar opengl controle de mapas"))

        layout_base.addLayout(menu_topo)
        layout_base.addLayout(meio_tela)
        layout_base.addLayout(char_interaction)
        layout_base.setStretch(0, 1)
        layout_base.setStretch(1, 8)
        layout_base.setStretch(2, 1)
        self.setLayout(layout_base)
    def conectar(self, host="127.0.0.1", port=8765, room_id=""):
        try:
            self.room_id = room_id
            self.socket = SocketClient(host, port)
            self.socket.message_received.connect(self.processar_msg)
            self.socket.start()            
            QTimer.singleShot(300, self.entrar_sala)
        except Exception as e:
            print(f"Erro ao conectar: {e}")

    def entrar_sala(self):
        self.socket.send_json({
            "action": "JOIN_ROOM",
            "room_id": self.room_id,
            "user": "Player"
            })


    def enviar_msg(self):
        self.socket.send_json({
            "action": "CHAT",
            "user": "Player1",
            "message": self.chat_dialog.text()
        })
        self.chat_dialog.clear()
    def processar_msg(self, data):
        if data.get("action") == "CHAT":
            self.chat_label.append(f'{data["user"]}: {data["message"]}')
        #botoes que tem atalhos
#endregion Player_only

#region dm_only
class Controller(QWidget):
    def __init__(self, ir_anotacoes,ir_configs,ir_mapas,ir_salas,ir_token_ficha,ir_gerir_pessoas):
        super().__init__()
        #configuraççoes iniciais
        #iniciar server client
        #telas
        self.ir_gerir_pessoas = ir_gerir_pessoas
        self.ir_anotacoes = ir_anotacoes
        self.ir_token_ficha = ir_token_ficha
        self.ir_configs = ir_configs
        self.ir_mapas = ir_mapas
        self.ir_salas = ir_salas
        self.setAutoFillBackground(True)
        #layout
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
        self.sala_id_text = QLabel("ID sala: ---")
        sair_sala = QPushButton("Sair da sala")
        menu_topo.addWidget(alertar_inicio_fim)
        menu_topo.addWidget(anotacoes)
        menu_topo.addWidget(token)
        menu_topo.addWidget(mapas)
        menu_topo.addWidget(gerenciar_pessoas)
        menu_topo.addWidget(confs)
        menu_topo.addWidget(self.sala_id_text)
        menu_topo.addWidget(sair_sala)
        sair_sala.clicked.connect(self.ir_salas)
        gerenciar_pessoas.clicked.connect(self.ir_gerir_pessoas)
        token.clicked.connect(self.ir_token_ficha)
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
        self.chat_label = QTextEdit()
        self.chat_label.setReadOnly(True)
        self.chat_label.setStyleSheet(f"background-color:{cores['botao']};")
        self.chat_dialog = QLineEdit()
        self.chat_dialog.setStyleSheet(f"background-color:{cores['botao']};")
        chat_dialog_mandar = QPushButton("mandar msg")
        chat_dialog_mandar.clicked.connect(self.enviar_msg)
        interacao_chat.addWidget(self.chat_dialog)
        controle.addWidget(self.chat_label, 13, 1)
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
        controle.addWidget(self.chat_label, 13, 1)
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
    def iniciar_servidor(self):
        self.servidor = SocketServer()
        self.servidor.cliente_conectado.connect(lambda a: print(f"Player conectou: {a}"))
        self.servidor.start()
    def conectar(self, host="127.0.0.1", port=8765):
        try:
            self.socket = SocketClient(host, port)
            self.socket.message_received.connect(self.processar_msg)
            self.socket.start()
            # cria sala após conectar
            
            import random, string
            self.room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            QTimer.singleShot(300, self.criar_sala)
        except Exception as e:
            print(f"Erro ao conectar: {e}")
    def criar_sala(self):
        self.socket.send_json({"action": "CREATE_ROOM", "room_id": self.room_id})
        self.socket.send_json({"action": "CREATE_ROOM", "room_id": self.room_id})
        self.sala_id_text.setText(f"ID sala: {self.room_id}")

    def enviar_msg(self):
        self.socket.send_json({
            "action": "CHAT",
            "user": "Player1",
            "message": self.chat_dialog.text()
        })
        self.chat_dialog.clear()
    def processar_msg(self, data):
        if data.get("action") == "CHAT":
            self.chat_label.append(f'{data["user"]}: {data["message"]}')
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

#region gerenciar_sessão
class Gerenciar_pessoas(QWidget):
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
        layout_base.addLayout(menu_topo,1,1)
        layout_base.addLayout(configs_infos,2,1)
        layout_base.addLayout(menu_fundo,3,1)
        self.setLayout(layout_base)
#endregion gerenciar_sessão

#endregion dm_only
#region tokens/fichas
class Token_ficha(QWidget):
    def __init__(self, voltar):
        super().__init__()
        self.voltar = voltar
        layout_base = QGridLayout()
        menu_topo = QHBoxLayout()
        menu_fundo = QHBoxLayout()
        lista_tokens_ficha = QVBoxLayout()
        tokens_ficha = QVBoxLayout()

        voltar_button = QPushButton("Voltar")
        voltar_button.clicked.connect(voltar)
        menu_topo.addWidget(voltar_button)

        lista_tokens_ficha.addWidget(QLabel("lista de token/fichas"))
        menu_fundo.addLayout(lista_tokens_ficha)
        tokens_ficha.addWidget(QLabel("token/ficha"))
        tokens_ficha.addWidget(QPushButton("editar"))
        menu_fundo.addLayout(tokens_ficha)

        layout_base.addLayout(menu_topo,1,1)
        layout_base.addLayout(menu_fundo,2,1)
        self.setLayout(layout_base)
#endregion tokens/fichas

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
        #configuracoes aqui
        Modo_performance_checkbox = QCheckBox("ativar modo batata")
        mostrar_id_sala = QCheckBox("mostrar id da sala")
        mostrar_id_sala.setCheckState(Qt.CheckState.Checked)#por padrão vai vir habilitado

        # evento qnd checado
        #Modo_performance_ativas.stateChanged.connect(self.report_state)
        
        configs_infos.addWidget(Modo_performance_checkbox)
        configs_infos.addWidget(mostrar_id_sala)
        #excluir dados do usuario
        apagar_dados = QPushButton("excluir dados salvos")
        apagar_dados.setStyleSheet(f":hover {{background-color: #fc0303;}}")
        menu_fundo.addWidget(apagar_dados)
        layout_base.addLayout(menu_topo,1,1)
        layout_base.addLayout(configs_infos,2,1)
        layout_base.addLayout(menu_fundo,3,1)
        self.setLayout(layout_base)
#endregion configs

#endregion app

#loop do app/janela
window = janela_principal()
window.show()
sys.exit(app.exec())