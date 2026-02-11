#region libs
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QImage
from PyQt6.QtCore import QTimer
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
#program representa o shader e o shader um modulo
from OpenGL.GLU import *
import sys
import os
import numpy as np
#endregion

data_type_color_vertex = np.dtype({
    #u v são para texturas
    'names':['x','y','z','color','u','v'],
    'formats':[np.float32, np.float32, np.float32, np.uint32, np.float32, np.float32],
    'offsets':[0,4,8,12,16,20],
    'itemsize':24})
#region shaders
#graphic pipeline(vertex -> rasterizer(converter formas geométricas (primitivas) e criando shader na gpu
def make_shader(arquivo_vertex:str,arquivo_frag:str) -> int:
    vertex_module = make_shader_module(arquivo_vertex,GL_VERTEX_SHADER)
    frag_module = make_shader_module(arquivo_frag,GL_FRAGMENT_SHADER)
    return compileProgram(vertex_module,frag_module)

def make_shader_module(arquivo:str,module_type):
    with open(arquivo,'r', encoding="utf-8") as file:
        src_code = file.readlines()#pega o codigo do shader do txt e mandando para a gpu
        return compileShader(src_code,module_type)#compila para gpu
#endregion

#outras configurações
fps = 60 #fps(dps vou add fps cap nas confs)
#region texturas
class Material():
    def __init__(self):
        self.textura = glGenTextures(1)#1 textura
    def carregar_textura(self, arquivo: str) -> None:
        img = QImage(arquivo)
        if img.isNull():
            raise Exception(f"Erro ao carregar a textura: {arquivo}")
        # converte para RGBA
        img = img.convertToFormat(QImage.Format.Format_RGBA8888)
        width = img.width()
        height = img.height()
        # Pega dados e cria numpy array
        ptr = img.bits()
        ptr.setsize(img.sizeInBytes())
        data = np.array(ptr, dtype=np.uint8).reshape(height, width, 4)
        # inverte verticalmente (OpenGL espera topo primeiro)
        data = np.flip(data, axis   =0)

    # Bind textura
        glBindTexture(GL_TEXTURE_2D, self.textura)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

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

#region matriz
class Mat4():
    #Matriz 4x4
    def __init__(self):
        self.dados = np.zeros((4,4),dtype=np.float32)
        for i in range(4):
            self.dados[i][i] = 1.0
    def translation(self,x:float,y:float,z:float)->"Mat4":
        self.dados[0,3] = x
        self.dados[1,3] = y
        self.dados[2,3] = z
        return self
    def rotacao(self,theta:float)->"Mat4":
        theta = np.radians(theta)
        c = np.cos(theta) 
        s = np.sin(theta)
        self.dados[0,0] = c
        self.dados[0,1] = -s
        self.dados[1,0] = s
        self.dados[1,1] = c
        return self
    def __mul__(self,other:"Mat4")->"Mat4":
        resp = Mat4()
        resp.dados = other.dados.dot(self.dados)
        return resp
#exemplo/manip dentro 
class Moving_quad():
    def __init__(self):
        self.t = 0.0
        self.x_offset = 0.0
        self.ang_z = 0.0
    def upt(self,dt:float)->None:
        self.t += 0.001 * dt
        if self.t> 360:
            self.t -= 360
        self.x_offset = np.sin(20* np.radians(self.t))
        self.ang_z = 10 * self.t
    def get_transform(self)-> np.array:
        return (Mat4().rotacao(self.ang_z) * Mat4().translation(self.x_offset,0,0)).dados

#endregion matriz

#region vertex buffe(agr é index buffer)
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
        #especificar e mandar
        attr_index = 0
        size = 3
        offset = 0#espera void pointer(somente o local no pointer) ao invez de int
        stride = data_type_color_vertex.itemsize
        glVertexAttribPointer(attr_index,size,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(offset))
        glEnableVertexAttribArray(attr_index)

        attr_index = 1
        size = 2 #trocar a cor
        offset = 12
        #diff por conta de um I (de integer)
        glVertexAttribIPointer(attr_index,size,GL_UNSIGNED_INT,stride,ctypes.c_void_p(offset))
        glEnableVertexAttribArray(attr_index)

        attr_index += 1
        size = 2 #trocar a cor
        offset = 16 
        #diff por conta de um I (de integer)
        glVertexAttribPointer(attr_index,size,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(offset))
        glEnableVertexAttribArray(attr_index)
        #mandar para gpu
        #target, num bytes, data enviada, modo de uso(é mandado para vbo)
        
        glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)#nn indica que vai desenhar
        
        #mais sim que os dados vao ser usados para desenhar
        self.index_count = 6
        indices = np.array([0,1,2,2,3,0],dtype=np.ubyte)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,indices.nbytes,indices,GL_STATIC_DRAW)
        #mesh configurada
        return self
    def draw(self) -> None:
        glBindVertexArray(self.VAO)#binda VAO com dados de vertex
        glDrawElements(GL_TRIANGLES,self.index_count,GL_UNSIGNED_BYTE,ctypes.c_void_p(0))
        #bind
    def destroy(self)->None:
        glDeleteVertexArrays(2,(self.VAO,))#num de vertex array deletados, colecao de dados 
        #lembre que vbo e ebo juntos entao precisamos deletar os dois
        glDeleteBuffers(1,(self.VBO,self.EBO))
#endregion
#region widget
class OpenGLWidget(QOpenGLWidget):
    #contexto open gl(initializeGL,paintGL)
    def initializeGL(self):
        cor_tela_opgl = (0.1, 0.1, 0.2, 1)
        glClearColor(cor_tela_opgl[0],cor_tela_opgl[1],cor_tela_opgl[2],cor_tela_opgl[3])
        #criar vertex layout
        #vertex layout(describes to the graphics pipeline how to interpret the raw data stored in a Vertex Buffer Object (VBO) on the GPU)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.mesh = Mesh().build_color_forma() #chama contructor de mesh pegamos a instancia e fazemos o triangulo
        self.textura = Material().carregar_textura(BASE_DIR+"\\imgs\\dado-20-lados.png")
        self.quad = Moving_quad()
        #achando arquivos necessarios para o shader
        vertex_path = os.path.join(BASE_DIR+"\\shader\\", "vertex.txt")
        fragment_path = os.path.join(BASE_DIR+"\\shader\\", "fragment.txt")
        #garantiu que ache os arquivos
        self.shader = make_shader(vertex_path,fragment_path)
        #framerate
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS (1000ms / 60 ≈ 16ms)
    def animate(self):
        self.quad.upt(1.0)  # atualiza a posição
        self.update()  # força o paintGL() a ser chamado novamente
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h else 1, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #configurando
        glUseProgram(self.shader)#usar programa shader
        tex_loc = glGetUniformLocation(self.shader, "tex")
        glUniform1i(tex_loc, 0)
        self.textura.use()
        location = glGetUniformLocation(self.shader,"transform")
        glUniformMatrix4fv(location,1,GL_FALSE,self.quad.get_transform())
        self.mesh.draw()

    #limpar recursos de gpu
    def cleanup(self):
        self.makeCurrent()   # ativa contexto
        glDeleteProgram(self.shader)#chamar qnd fechar aplicacao (optimizar e jeito correto de liberar espaço)
        glDeleteVertexArrays(1, [self.VAO])
        self.doneCurrent()
        self.mesh.destroy()
        self.textura.destroy()