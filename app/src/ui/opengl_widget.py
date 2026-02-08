from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
#program representa o shader e o shader um modulo
from OpenGL.GLU import *
import sys
import os

#optimizacoes
import numpy as np
#graphic pipeline(vertex -> rasterizer(converter formas geométricas (primitivas)
#criando shader na gpu
def make_shader(arquivo_vertex:str,arquivo_frag:str) -> int:
    vertex_module = make_shader_module(arquivo_vertex,GL_VERTEX_SHADER)
    frag_module = make_shader_module(arquivo_frag,GL_FRAGMENT_SHADER)
    return compileProgram(vertex_module,frag_module)

def make_shader_module(arquivo:str,module_type):
    with open(arquivo,'r', encoding="utf-8") as file:
        src_code = file.readlines()#pega o codigo do shader do txt e mandando para a gpu
        return compileShader(src_code,module_type)#compila para gpu

#outras configurações
fps = 60 #fps(dps vou add fps cap nas confs)
class OpenGLWidget(QOpenGLWidget):
    #contexto open gl(initializeGL,paintGL)
    def initializeGL(self):
        cor_tela_opgl = (0.1, 0.1, 0.2, 1)
        glClearColor(cor_tela_opgl[0],cor_tela_opgl[1],cor_tela_opgl[2],cor_tela_opgl[3])
        #criar vertex layout(seguindo tutorial(MESMO sendo algo para mac(evitar erros seguindo o tutorial)))
        #vertex layout(describes to the graphics pipeline how to interpret the raw data stored in a Vertex Buffer Object (VBO) on the GPU)
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
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
        glDrawArrays(GL_TRIANGLES,0,3)#modo de desenho , index inicial, qnts vertices

    #limpar recursos de gpu
    def cleanup(self):
        self.makeCurrent()   # ativa contexto
        glDeleteProgram(self.shader)
        glDeleteProgram(self.shader)#chamar qnd fechar aplicacao (optimizar e jeito correto de liberar espaço)
        glDeleteVertexArrays(1, [self.VAO])
        self.doneCurrent()