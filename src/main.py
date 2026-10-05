"""Execute com: python src/main.py. Pipeline clássico OpenGL para fins didáticos."""

import argparse
import math
from pathlib import Path

import cv2
import glfw
import numpy as np
from OpenGL import GL as gl
from OpenGL.GLU import gluLookAt, gluPerspective

from geometria import VERTICES, FACES, NORMAIS, cores_faces
from trackball import mapear_mouse, quat_arraste, multiplicar, matriz_rotacao


class Aplicacao:
    def __init__(self):
        self.arrastando = False
        self.anterior = None
        self.reiniciar()

    def reiniciar(self):
        # Pequeno giro inicial permite enxergar duas laterais da pirâmide.
        meio_x = math.radians(20) / 2
        meio_y = math.radians(-25) / 2
        self.orientacao = multiplicar(
            np.array([math.cos(meio_x), math.sin(meio_x), 0, 0]),
            np.array([math.cos(meio_y), 0, math.sin(meio_y), 0]),
        )
        self.posicao = np.zeros(3)
        self.escala = 1.0
        self.distancia = 7.0
        self.paleta = 0
        self.iluminacao = True
        self.cores = cores_faces(self.paleta)
        self.arrastando = False
        self.anterior = None

    def vetor_mouse(self, janela, x, y):
        largura, altura = glfw.get_window_size(janela)
        return mapear_mouse(x, y, largura, altura)

    def clique(self, janela, botao, acao, modificadores):
        if botao == glfw.MOUSE_BUTTON_LEFT:
            self.arrastando = acao == glfw.PRESS
            x, y = glfw.get_cursor_pos(janela)
            self.anterior = self.vetor_mouse(janela, x, y)

    def movimento(self, janela, x, y):
        if self.arrastando:
            atual = self.vetor_mouse(janela, x, y)
            delta = quat_arraste(self.anterior, atual)
            # Delta à esquerda aplica o novo giro nos eixos da tela.
            self.orientacao = multiplicar(delta, self.orientacao)
            self.anterior = atual

    def rolagem(self, janela, dx, dy):
        self.distancia = float(np.clip(self.distancia - dy * 0.4, 3.5, 15))

    def tecla(self, janela, tecla, scancode, acao, modificadores):
        if acao not in (glfw.PRESS, glfw.REPEAT):
            return
        if tecla == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(janela, True)
        elif tecla == glfw.KEY_R:
            self.reiniciar()
        elif tecla == glfw.KEY_C and acao == glfw.PRESS:
            self.paleta = 1 - self.paleta
            self.cores = cores_faces(self.paleta)
        elif tecla == glfw.KEY_L and acao == glfw.PRESS:
            self.iluminacao = not self.iluminacao
        elif tecla in (glfw.KEY_EQUAL, glfw.KEY_KP_ADD):
            self.escala = min(1.5, self.escala + 0.1)
        elif tecla in (glfw.KEY_MINUS, glfw.KEY_KP_SUBTRACT):
            self.escala = max(0.3, self.escala - 0.1)
        elif tecla == glfw.KEY_A:
            self.posicao[0] = max(-2, self.posicao[0] - 0.1)
        elif tecla == glfw.KEY_D:
            self.posicao[0] = min(2, self.posicao[0] + 0.1)
        elif tecla == glfw.KEY_W:
            self.posicao[1] = min(2, self.posicao[1] + 0.1)
        elif tecla == glfw.KEY_S:
            self.posicao[1] = max(-2, self.posicao[1] - 0.1)

    def desenhar(self, largura, altura):
        gl.glViewport(0, 0, largura, altura)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gluPerspective(45, largura / altura, 0.1, 100)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        # Câmera alinhada aos eixos da tela, olhando para a origem.
        gluLookAt(0, 0, self.distancia, 0, 0, 0, 0, 1, 0)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, [3, 4, 5, 1])
        if self.iluminacao:
            gl.glEnable(gl.GL_LIGHTING)
        else:
            gl.glDisable(gl.GL_LIGHTING)

        # Espaço local → mundo: M = T · R · S.
        translacao = np.eye(4)
        translacao[:3, 3] = self.posicao
        rotacao = matriz_rotacao(self.orientacao)
        escala = np.diag([self.escala, self.escala, self.escala, 1])
        modelo = translacao @ rotacao @ escala
        # OpenGL lê matrizes por colunas; transpose adapta o array do NumPy.
        gl.glMultMatrixf(modelo.T.astype(np.float32).copy())

        for face, normal, cor in zip(FACES, NORMAIS, self.cores):
            # Laterais: triângulos. Base: um quadrado com uma cor e normal.
            primitiva = gl.GL_QUADS if len(face) == 4 else gl.GL_TRIANGLES
            gl.glBegin(primitiva)
            gl.glColor3fv(cor)
            gl.glNormal3fv(normal)
            for indice in face:
                gl.glVertex3fv(VERTICES[indice])
            gl.glEnd()


def executar(verificar=False):
    if not glfw.init():
        raise RuntimeError("Não foi possível inicializar o GLFW.")
    janela = None
    try:
        # OpenGL 2.1 mantém o pipeline clássico pedido no enunciado.
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        if verificar:
            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        titulo = "Piramide 3D | Arraste: girar | Scroll: zoom | WASD: mover | +/-: escala | C: cores | L: luz | R: reset"
        janela = glfw.create_window(1000, 720, titulo, None, None)
        if not janela:
            raise RuntimeError("Não foi possível criar um contexto OpenGL 2.1.")
        glfw.make_context_current(janela)
        glfw.swap_interval(1)
        gl.glClearColor(0.08, 0.10, 0.14, 1)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_NORMALIZE)  # Mantém normais unitárias após a escala.
        gl.glShadeModel(gl.GL_FLAT)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, [0.22, 0.22, 0.22, 1])
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, [0.85, 0.85, 0.85, 1])
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)

        app = Aplicacao()
        glfw.set_mouse_button_callback(janela, app.clique)
        glfw.set_cursor_pos_callback(janela, app.movimento)
        glfw.set_scroll_callback(janela, app.rolagem)
        glfw.set_key_callback(janela, app.tecla)
        print(titulo, flush=True)
        while not glfw.window_should_close(janela):
            glfw.poll_events()
            largura, altura = glfw.get_framebuffer_size(janela)
            if largura == 0 or altura == 0:
                glfw.wait_events_timeout(0.1)
                continue
            app.desenhar(largura, altura)
            if verificar:
                gl.glFinish()
                erro = gl.glGetError()
                if erro != gl.GL_NO_ERROR:
                    raise RuntimeError(f"Erro OpenGL: {erro}")
                pixels = gl.glReadPixels(0, 0, largura, altura, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
                rgb = np.frombuffer(pixels, dtype=np.uint8).reshape(altura, largura, 3)
                if np.unique(rgb.reshape(-1, 3), axis=0).shape[0] < 3:
                    raise RuntimeError("A imagem renderizada não contém a pirâmide.")
                destino = Path(__file__).resolve().parent.parent / "demonstracao.png"
                if not cv2.imwrite(str(destino), cv2.cvtColor(np.flipud(rgb), cv2.COLOR_RGB2BGR)):
                    raise RuntimeError("Falha ao salvar a captura de verificação.")
                print(f"Renderização validada. Captura: {destino}")
                break
            glfw.swap_buffers(janela)
    finally:
        if janela:
            glfw.destroy_window(janela)
        glfw.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verificar", action="store_true", help="Renderiza uma captura e encerra.")
    executar(parser.parse_args().verificar)
