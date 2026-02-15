#region libs
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QImage
from PySide6.QtCore import QTimer, Qt, QPoint

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
#program representa o shader e o shader um modulo
from OpenGL.GLU import *
import sys
import os
import numpy as np
import ctypes

#endregion
sense = 0.2
vel_mov = 0.1
data_type_color_vertex = np.dtype({
    #u v são para texturas
    'names':['x','y','z','color','u','v'],
    'formats':[np.float32, np.float32, np.float32, np.int32, np.float32, np.float32],
    'offsets':[0,4,8,12,16,20],
    'itemsize':24})
uniform_type_model = 0
uniform_type_view = 1
uniform_type_projection = 2
uniform_names = {
    uniform_type_model : "transform",
    uniform_type_view : "view",
    uniform_type_projection: "projecao"
}
#graphic pipeline(vertex -> rasterizer(converter formas geométricas (primitivas) e criando shader na gpu
def make_shader(arquivo_vertex:str,arquivo_frag:str) -> int:
    vertex_module = make_shader_module(arquivo_vertex,GL_VERTEX_SHADER)
    frag_module = make_shader_module(arquivo_frag,GL_FRAGMENT_SHADER)
    return compileProgram(vertex_module,frag_module)

def make_shader_module(arquivo:str,module_type):
    with open(arquivo,'r', encoding="utf-8") as file:
        src_code = file.readlines()#pega o codigo do shader do txt e mandando para a gpu
        return compileShader(src_code,module_type)#compila para gpu
#adaptar centro de widget
#def handle_mouse(self,center_x):
#region shaders
class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.program = make_shader(vertex_path, fragment_path)
        self.location: dict[str,int] = {}

    def use(self):
        glUseProgram(self.program)
    def upload_mat4(self,uniform_type:int,matrix:"Mat4")->None:
        if uniform_type not in self.location:
            name = uniform_names[uniform_type]
            self.location[name] = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(self.location[uniform_type], 1, GL_FALSE, matrix.dados)


    def destroy(self):
        glDeleteProgram(self.program)

#endregion

#outras configurações
fps = 60 #fps(dps vou add fps cap nas confs)
#region texturas
class Material():
    def __init__(self):
        self.textura = None

        #self.textura = glGenTextures(1)#1 textura
    def carregar_textura(self, arquivo: str) -> None:
        self.textura = glGenTextures(1)
        img = QImage(arquivo)
        if img.isNull():
            raise Exception(f"Erro ao carregar a textura: {arquivo}")
        # converte para RGBA
        img = img.convertToFormat(QImage.Format.Format_RGBA8888)
        width = img.width()
        height = img.height()
        
        # Pega dados e cria numpy array (corrigido para PySide6)
        ptr = img.constBits()
        # Criar array diretamente do buffer sem usar setsize
        data = np.frombuffer(ptr, dtype=np.uint8, count=img.sizeInBytes()).reshape(height, width, 4)
        
        # inverte verticalmente (OpenGL espera topo primeiro)
        #data = np.flip(data, axis=0)

        # Bind textura
        glBindTexture(GL_TEXTURE_2D, self.textura)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        # envia dados para GPU
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
        return self


    def use(self)->None:
        glBindTexture(GL_TEXTURE_2D,self.textura)
    def destroy(self)->None:
        glDeleteTextures(1,(self.textura,))
#endregion
#region vetores(vec1/2/3)
class Vec3:
    def __init__(self,x:float = 0,y:float = 0,z:float = 0):
        self.dados = np.array((x,y,z),dtype=np.float32)

    def dot(self,other:"Vec3")->float:
        resp = 0.0
        for i in range(3):
            resp += self.dados[i] * other.dados[i]
        return resp
    def magnitude(self) -> float:
        return np.sqrt(self.dot(self))
    def normalize(self) -> "Vec3":
        magnitude = self.magnitude()
        for i in range(3):
            self.dados[i] = self.dados[i] / magnitude
        return self
    def cross_prod(self,other:"Vec3") -> "Vec3":
        u = self.dados
        v = other.dados
        x = u[1] * v[2] - u[2] * v[1]
        y = u[2] * v[0] - u[0] * v[2]
        z = u[0] * v[1] - u[1] * v[0]
        return Vec3(x,y,z)
    def __mul__(self,coeficiente:float)->"Vec3":
        return Vec3(coeficiente * self.dados[0],coeficiente * self.dados[1],coeficiente * self.dados[2])
    def __add__(self,other:"Vec3")->"Vec3":
        return Vec3(other.dados[0] + self.dados[0], other.dados[1] + self.dados[1], other.dados[2] + self.dados[2])
#endregion vetores(vec1/2/3)
#region matriz
class Mat4():
    #Matriz 4x4
    def __init__(self):
        self.dados = np.zeros((4,4),dtype=np.float32)
        for i in range(4):
            self.dados[i][i] = 1.0
    def translation(self,pos:Vec3)->"Mat4":
        #fazendo individualmente (patch)
        self.dados[0,3] = pos.dados[0]
        self.dados[1,3] = pos.dados[1]
        self.dados[2,3] = pos.dados[2]
        return self
    def rotacao(self,theta:float)->"Mat4":
        theta = np.radians(theta)
        c = np.cos(theta) 
        s = np.sin(theta)
        self.dados[0,0] = c
        self.dados[0,1] = s
        self.dados[1,0] = -s
        self.dados[1,1] = c
        return self
    #projeção perspectiva
    def perspectiva(self,fov_y:float,aspect_ratio:float,perto:float,longe:float)->"Mat4":
        self.dados[:] = 0.0
        #fov_y field of view y
        f = 1.0 / np.tan(np.radians(fov_y) / 2.0)
        self.dados[0,0] = f / aspect_ratio  # Scale X
        self.dados[1,1] = f                 # Scale Y
        self.dados[2,2] = -(longe + perto) / (longe - perto)      # Z mapping
        self.dados[2,3] = -(2.0 * longe * perto) / (longe - perto)  # Z translation
        self.dados[3,2] = -1.0  # Perspective divide (w = -z)
        self.dados[3,3] = 0.0#patch pois este e´definido anteriormente como 1
        return self
    def camera(self,pos:Vec3,direita:Vec3,cima:Vec3,frente:Vec3):
        #orientação em fp(first person)
        self.dados[:] = np.identity(4, dtype=np.float32)
        # Preenche as linhas 0,1,2 com os vetores (direita, cima, -frente)
        self.dados[0, 0:3] = direita.dados
        self.dados[1, 0:3] = cima.dados
        self.dados[2, 0:3] = -frente.dados
        # Translação (linha 3)
        self.dados[3, 0] = -pos.dot(direita)
        self.dados[3, 1] = -pos.dot(cima)
        self.dados[3, 2] =  pos.dot(frente)
        self.dados[3, 3] = 1.0
        return self

    def __mul__(self,other:"Mat4")->"Mat4":
        resp = Mat4()
        resp.dados = self.dados.dot(other.dados)
        return resp
#exemplo/manip dentro agr com perspectiva na formula
class Moving_quad():
    def __init__(self):
        self.t = 0.0
        self.pos = Vec3(0.0,0.0,-2.0)

        self.ang_z = 0.0
    def upt(self,dt:float)->None:
        self.t += 0.001 * dt
        if self.t> 360:
            self.t -= 360
        self.pos.dados[1] = np.sin(20* np.radians(self.t))
        self.ang_z = 10 * self.t
    def get_transform(self)-> np.array:
        return (Mat4().translation(self.pos) * Mat4().rotacao(self.ang_z)).dados



#endregion matriz
#region Cam
class Camera():
    Cima = Vec3(0, 1, 0)
    def __init__(self):
        self.pos = Vec3(0, 0, 5)  # Mais longe para ver melhor

        self.yaw = -90.0  # Olhando direto para -Z
        self.pitch = 0.0

        self.frente = Vec3(0,0,-1)
        self.direita = Vec3(1,0,0)
        self.cima = Vec3(0,1,0)

    #recalcula vetores
    def recalc(self) -> "Vec3":
        yaw_rad = np.radians(self.yaw)
        pitch_rad = np.radians(self.pitch)
    
        c = np.cos(yaw_rad)
        s = np.sin(yaw_rad)
        c2 = np.cos(pitch_rad)
        s2 = np.sin(pitch_rad)
        self.frente.dados[0] = c * c2
        self.frente.dados[1] = s2
        self.frente.dados[2] = s * c2
        self.frente.normalize()
        self.direita = self.frente.cross_prod(Camera.Cima).normalize()
        self.cima = self.direita.cross_prod(self.frente).normalize()
    
    def view_transform(self) -> Mat4:
        return Mat4().camera(self.pos,self.direita,self.cima,self.frente)
    #manip cam
    def giro(self,dx:float,dy:float)->None:
        self.yaw += dx
        if self.yaw < 0 :
            self.yaw += 360
        if self.yaw > 360 :
            self.yaw -= 360
        self.pitch = min(89,max(-89,self.pitch + dy))
    def movimento(self,quanto:Vec3)->None:
        movimento = self.direita * quanto.dados[0] + self.cima * quanto.dados[1] + self.frente * quanto.dados[2]
        self.pos = self.pos + movimento * vel_mov
#endregion Cam
#region vertex buffer(agr é index buffer)
class Mesh():
    def __init__(self):
        self.VAO = glGenVertexArrays(1)
        #EBO element buffer object, guarda indices de vertices que referencia vertices do VBO
        self.VBO, self.EBO = glGenBuffers(2)#guarda os dados do vertex/numeros de buffers
        #troquei de 1 para 2 para criar o EBO junto de VBO
        '''vertex counter vs index counter
        Vertex Buffer (Vertex Count): 
        Contains the actual data for each point in 3D space (position, normal, texture coordinates).
        Index Buffer (Index): 
        Contains integers that act as pointers to the vertex buffer, telling the GPU which vertices to connect to form triangles. 
        '''
        #troquei vertex_count para index_count
        self.index_count = 0
    #evitar erro com float32
    #com isso nn precisamos de hard coded em vertex.txt
    def build_color_forma(self)->"Mesh":
        #preenche com uma lista com 3 zeros para o tipo de dado isso com defaults sensiveis
        vertices = np.zeros(4,dtype=data_type_color_vertex)#cada vertice(comecando por 1 -> n, nn de 0 -> n-1),dtype
        #definimos valores nele(no tutorial esta deste jeito)
        vertices[0]['x'] = -0.75
        vertices[0]['y'] = -0.75
        vertices[0]['z'] = 0.0
        vertices[0]['color'] = 0
        #cordenadas de texturas sao definidas por u(x) v(y) lembrando que coordenadas no opengl
        #vao de 0 a 1 / -1 a 1
        vertices[0]['u'] = 0.0
        vertices[0]['v'] = 0.0

        vertices[1]['x'] = 0.75
        vertices[1]['y'] = -0.75
        vertices[1]['z'] = 0.0
        vertices[1]['color'] = 1
        vertices[1]['u'] = 1.0
        vertices[1]['v'] = 0.0

        vertices[2]['x'] = 0.75
        vertices[2]['y'] = 0.75
        vertices[2]['z'] = 0.0
        vertices[2]['color'] = 2
        vertices[2]['u'] = 1.0
        vertices[2]['v'] = 1.0

        vertices[3]['x'] = -0.75
        vertices[3]['y'] = 0.75
        vertices[3]['z'] = 0.0
        vertices[3]['color'] = 1
        vertices[3]['u'] = 0.0
        vertices[3]['v'] = 1.0
        #bind VAO
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER,self.VBO)#vertex data para desenhar(array buffer)

        glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)#nn indica que vai desenhar
        #especificar e mandar
        attr_index = 0
        size = 3
        offset = 0#espera void pointer(somente o local no pointer) ao invez de int
        stride = data_type_color_vertex.itemsize
        glVertexAttribPointer(attr_index,size,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(offset))
        glEnableVertexAttribArray(attr_index)

        attr_index = 1
        size = 1 #trocar a cor
        offset = 12
        #diff por conta de um I (de integer)
        glVertexAttribIPointer(attr_index,size,GL_INT,stride,ctypes.c_void_p(offset))
        glEnableVertexAttribArray(attr_index)

        attr_index += 1
        size = 2 #trocar a cor
        offset = 16 
        #diff por conta de um I (de integer)
        glVertexAttribPointer(attr_index,size,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(offset))
        glEnableVertexAttribArray(attr_index)
        #mandar para gpu
        #target, num bytes, data enviada, modo de uso(é mandado para vbo)
        
        
        #mais sim que os dados vao ser usados para desenhar
        self.index_count = 6
        indices = np.array([0,1,2,2,3,0], dtype=np.uint32)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,indices.nbytes,indices,GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER,0)

        #mesh configurada
        return self
    def draw(self) -> None:
        glBindVertexArray(self.VAO)#binda VAO com dados de vertex
        glDrawElements(GL_TRIANGLES,self.index_count,GL_UNSIGNED_INT,ctypes.c_void_p(0))
        #bind
    def destroy(self)->None:
        glDeleteVertexArrays(1,(self.VAO,))#num de vertex array deletados, colecao de dados 
        #lembre que vbo e ebo juntos entao precisamos deletar os dois
        glDeleteBuffers(2,(self.VBO,self.EBO))
#endregion

#region widget
class OpenGLWidget(QOpenGLWidget):
    #controle de cam
    def __init__(self, parent=None):
        super().__init__(parent)

        self.shader = None
        self.mesh = None
        self.textura = None
        self.cam = None
        self.quad = None

        # Teclas pressionadas (substituir keyboard)
        self.keys_pressed = set()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

        self.dragging = False
        self.last_mouse_pos = QPoint()
        self.sensibilidade = sense
    
    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        self.keys_pressed.discard(event.key())
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if self.cam is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.position().toPoint()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def mouseMoveEvent(self, event):
        if not self.dragging:
            return
        if not self.dragging:
            return
        pos = event.position().toPoint()
        dx = pos.x() - self.last_mouse_pos.x()
        dy = pos.y() - self.last_mouse_pos.y()
        self.last_mouse_pos = pos
        self.cam.giro(dx * self.sensibilidade,
                  -dy * self.sensibilidade)
        self.cam.recalc()
        self.update()
    #contexto open gl(initializeGL,paintGL)
    def initializeGL(self):
        glDisable(GL_CULL_FACE)
        cor_tela_opgl = (0.1, 0.1, 0.2, 1)
        glClearColor(cor_tela_opgl[0],cor_tela_opgl[1],cor_tela_opgl[2],cor_tela_opgl[3])
        #criar vertex layout
        #vertex layout(describes to the graphics pipeline how to interpret the raw data stored in a Vertex Buffer Object (VBO) on the GPU)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.mesh = Mesh().build_color_forma() #chama contructor de mesh pegamos a instancia e fazemos o triangulo
        
        # Corrigir caminhos dos arquivos
        texture_path = os.path.join(BASE_DIR, "imgs_testes", "dado-20-lados.png")
        
        try:
            self.textura = Material().carregar_textura(texture_path)
        except Exception as e:
            # Criar textura dummy FUNCIONAL se falhar
            import traceback
            traceback.print_exc()
            self.textura = Material()
            self.textura.textura = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.textura.textura)
            # Criar textura branca 2x2
            white_data = np.array([[255, 255, 255, 255] * 2] * 2, dtype=np.uint8)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 2, 2, 0, GL_RGBA, GL_UNSIGNED_BYTE, white_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        
        self.quad = Moving_quad()
        self.cam = Camera()
        
        #achando arquivos necessarios para o shader
        vertex_path = os.path.join(BASE_DIR, "shader", "vertex.txt")
        fragment_path = os.path.join(BASE_DIR, "shader", "fragment.txt")
        
        try:
            self.shader = Shader(vertex_path,fragment_path)
        except Exception as e:
            print(f"ERRO ao compilar shaders: {e}")
            return
        glActiveTexture(GL_TEXTURE0)
        self.shader.use()
        glBindVertexArray(self.mesh.VAO)
        self.tex_loc = glGetUniformLocation(self.shader.program,"my_texture")
        self.proj_loc = glGetUniformLocation(self.shader.program,"projecao")
        self.transform_loc = glGetUniformLocation(self.shader.program,"transform")
        self.view_loc = glGetUniformLocation(self.shader.program,"view")
        glUniform1i(self.tex_loc, 0)
    
        self.cam.recalc()
        fov_y = 60.0
        aspect_ratio = 4.0/3.0
        perto = 0.1  # Near plane mais razoável
        longe = 100.0
        proj_mat = Mat4().perspectiva(fov_y,aspect_ratio,perto,longe)
        #definindo projecao de perspectiva (GL_TRUE = transpor)
        glUniformMatrix4fv(self.proj_loc, 1, GL_TRUE, proj_mat.dados)
        #framerate
        # Verificar matrizes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS (1000ms / 60 ≈ 16ms)
        #outros
        glEnable(GL_DEPTH_TEST)
    
    def animate(self):
        if self.cam is None:
            return
        #movimento de camera
        movimento = Vec3(0,0,0)
        
        #wasd
        if Qt.Key.Key_W in self.keys_pressed:
            movimento.dados[2] -= 1
        if Qt.Key.Key_S in self.keys_pressed:
            movimento.dados[2] += 1
        if Qt.Key.Key_A in self.keys_pressed:
            movimento.dados[0] -= 1
        if Qt.Key.Key_D in self.keys_pressed:
            movimento.dados[0] += 1
        #setas
        if Qt.Key.Key_Up in self.keys_pressed:
            movimento.dados[2] -= 1
        if Qt.Key.Key_Down in self.keys_pressed:
            movimento.dados[2] += 1
        if Qt.Key.Key_Left in self.keys_pressed:
            movimento.dados[0] -= 1
        if Qt.Key.Key_Right in self.keys_pressed:
            movimento.dados[0] += 1
        # subir / descer 
        if Qt.Key.Key_Space in self.keys_pressed:
            movimento.dados[1] += 1
        if Qt.Key.Key_Control in self.keys_pressed:
            movimento.dados[1] -= 1
        # aplica movimento
        if movimento.magnitude() > 0:
            movimento.normalize()
            self.cam.movimento(movimento)
        #atualizar tela
        self.quad.upt(1.0)  # atualiza a posição
        self.cam.recalc()#atualiza a camera e os vetores
        self.update()  # força o paintGL() a ser chamado novamente
    
    def resizeGL(self, w, h):
        if self.shader is None:
            return
        self.shader.use()
        glViewport(0, 0, w, h)
        aspect_ratio = w / h if h else 1.0
        proj_mat = Mat4().perspectiva(60.0, aspect_ratio, 0.1, 100.0)  # Near plane 0.1
        glUniformMatrix4fv(self.proj_loc, 1, GL_TRUE, proj_mat.dados)  # GL_TRUE = transpor



    def paintGL(self):
        if self.shader is None:
            return
        
        # Debug: mostrar a cada 60 frames
        if not hasattr(self, '_frame_count'):
            self._frame_count = 0
        self._frame_count += 1
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        #configurando
        self.shader.use()#usar programa shader
        glUniform1i(self.tex_loc, 0)
        glActiveTexture(GL_TEXTURE0)
        self.textura.use()
        # GL_TRUE = transpor as matrizes de row-major (numpy) para column-major (OpenGL)
        glUniformMatrix4fv(self.transform_loc, 1, GL_TRUE, self.quad.get_transform())
        glUniformMatrix4fv(self.view_loc, 1, GL_TRUE, self.cam.view_transform().dados)

        self.mesh.draw()
        
        # Verificar erros após draw
        if self._frame_count == 60:
            err = glGetError()
            if err != GL_NO_ERROR:
                print(f"ERRO OpenGL após draw: {err}")

    #limpar recursos de gpu
    def cleanup(self):
        #chamar qnd fechar aplicacao (optimizar e jeito correto de liberar espaço)
        self.makeCurrent()   # ativa contexto
        self.mesh.destroy()
        self.shader.destroy()
        self.textura.destroy()
        self.doneCurrent()