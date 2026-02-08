#region libs
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
#program representa o shader e o shader um modulo
from OpenGL.GLU import *
import sys
import os
import numpy as np
#endregion

data_type_color_vertex = np.dtype({
    'names':['x','y','z','color'],
    'formats':[np.float32, np.float32, np.float32, np.uint32],
    'offsets':[0,4,8,12],
    'itemsize':16})
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
class Mesh():
    def __init__(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)#guarda os dados do vertex
        self.vertex_count = 0
    #evitar erro com float32
    #com isso nn precisamos de hard coded em vertex.txt
    def build_color_triangue(self)->"Mesh":
        #preenche com uma lista com 3 zeros para o tipo de dado isso com defaults sensiveis
        vertices = np.zeros(3,dtype=data_type_color_vertex)
        #definimos valores nele(no tutorial esta deste jeito)
        vertices[0]['x'] = -0.75
        vertices[0]['y'] = -0.75
        vertices[0]['z'] = 0.0
        vertices[0]['color'] = 0

        vertices[1]['x'] = 0.75
        vertices[1]['y'] = -0.75
        vertices[1]['z'] = 0.0
        vertices[1]['color'] = 1

        vertices[2]['x'] = 0.35
        vertices[2]['y'] = 0.75
        vertices[2]['z'] = 0.0
        vertices[2]['color'] = 2
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

        attr_index += 1
        size -= 2 #trocar a cor
        offset += 12
        #diff por conta de um I (de integer)
        glVertexAttribIPointer(attr_index,size,GL_UNSIGNED_INT,stride,ctypes.c_void_p(offset))
        glEnableVertexAttribArray(attr_index)
        #mandar para gpu
        #target, num bytes, data enviada, modo de uso(é mandado para vbo)
        
        glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)#nn indica que vai desenhar
        
        #mais sim que os dados vao ser usados para desenhar
        self.vertex_count = 3
        #mesh configurada
        return self
    def draw(self) -> None:
        glBindVertexArray(self.VAO)#binda VAO com dados de vertex
        glDrawArrays(GL_TRIANGLES,0,self.vertex_count)
    def destroy(self)->None:
        glDeleteVertexArrays(1,(self.VAO,))#num de vertex array deletados, colecao de dados
        glDeleteBuffers(1,(self.VBO,))
class OpenGLWidget(QOpenGLWidget):
    #contexto open gl(initializeGL,paintGL)
    def initializeGL(self):
        cor_tela_opgl = (0.1, 0.1, 0.2, 1)
        glClearColor(cor_tela_opgl[0],cor_tela_opgl[1],cor_tela_opgl[2],cor_tela_opgl[3])
        #criar vertex layout(seguindo tutorial(MESMO sendo algo para mac(evitar erros seguindo o tutorial)))
        #vertex layout(describes to the graphics pipeline how to interpret the raw data stored in a Vertex Buffer Object (VBO) on the GPU)
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
        self.mesh = Mesh().build_color_triangue() #chama contructor de mesh pegamos a instancia e fazemos o triangulo
        #achando arquivos necessarios para o shader
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        vertex_path = os.path.join(BASE_DIR, "vertex.txt")
        fragment_path = os.path.join(BASE_DIR, "fragment.txt")
        #garantiu que ache os arquivos
        self.shader = make_shader(vertex_path,fragment_path)

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
        self.mesh.draw()

    #limpar recursos de gpu
    def cleanup(self):
        self.makeCurrent()   # ativa contexto
        glDeleteProgram(self.shader)
        glDeleteProgram(self.shader)#chamar qnd fechar aplicacao (optimizar e jeito correto de liberar espaço)
        glDeleteVertexArrays(1, [self.VAO])
        self.doneCurrent()
        self.mesh.destroy()