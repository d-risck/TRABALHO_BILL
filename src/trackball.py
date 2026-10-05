"""Trackball virtual: vetores na esfera → quatérnio → matriz de rotação."""

import numpy as np


def mapear_mouse(x, y, largura, altura):
    """Centraliza o cursor e usa a menor dimensão para manter a esfera circular.

    Dentro do círculo: z = sqrt(1 - x² - y²). Fora: projeta na borda,
    com z = 0. A coordenada y é invertida porque a janela cresce para baixo.
    """
    raio = max(min(largura, altura) / 2.0, 1.0)
    vetor = np.array([(x - largura / 2) / raio,
                      (altura / 2 - y) / raio, 0.0])
    r2 = vetor[0] ** 2 + vetor[1] ** 2
    if r2 <= 1.0:
        vetor[2] = np.sqrt(1.0 - r2)
    else:
        vetor /= np.sqrt(r2)
    return vetor


def quat_arraste(inicio, fim):
    """Eixo pelo produto vetorial e ângulo pelo produto escalar."""
    eixo = np.cross(inicio, fim)
    seno = np.linalg.norm(eixo)
    cosseno = np.clip(np.dot(inicio, fim), -1.0, 1.0)
    if seno < 1e-12:
        if cosseno > 0:
            return np.array([1.0, 0.0, 0.0, 0.0])
        # Vetores opostos: escolhe um eixo perpendicular para girar 180°.
        auxiliar = np.eye(3)[np.argmin(np.abs(inicio))]
        eixo = np.cross(inicio, auxiliar)
        eixo /= np.linalg.norm(eixo)
        return np.array([0.0, *eixo])
    eixo /= seno
    angulo = np.arccos(cosseno)
    return np.array([np.cos(angulo / 2), *(eixo * np.sin(angulo / 2))])


def multiplicar(a, b):
    """Produto de Hamilton a × b; ordem dos componentes: (w, x, y, z)."""
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    resultado = np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
    ])
    return resultado / np.linalg.norm(resultado)


def matriz_rotacao(q):
    """Converte um quatérnio unitário em uma matriz homogênea 4 × 4."""
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w), 0],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w), 0],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y), 0],
        [0, 0, 0, 1],
    ], dtype=float)
