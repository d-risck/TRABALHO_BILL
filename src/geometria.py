"""Pirâmide com quatro laterais triangulares e uma base quadrada."""

import cv2
import numpy as np


# Base no plano y = -1; topo em y = 1. Os índices seguem ordem
# anti-horária quando cada face é vista pelo lado de fora.
VERTICES = np.array([
    [-1, -1, -1], [1, -1, -1], [1, -1, 1], [-1, -1, 1],
    [0, 1, 0],
], dtype=float)

FACES = [
    (0, 4, 1), (1, 4, 2), (2, 4, 3), (3, 4, 0),
    (0, 1, 2, 3),  # Uma única face quadrada para a base.
]


def normal_face(v0, v1, v2):
    """N = (V1 - V0) × (V2 - V0), normalizada para ter comprimento 1."""
    normal = np.cross(v1 - v0, v2 - v0)
    comprimento = np.linalg.norm(normal)
    if comprimento < 1e-12:
        raise ValueError("Uma face degenerada não possui normal definida.")
    return normal / comprimento


# Três vértices definem o plano e a normal, inclusive para a base quadrada.
NORMAIS = np.array([normal_face(*VERTICES[list(face[:3])]) for face in FACES])


def cores_faces(paleta=0):
    """HSV separa matiz, saturação e brilho; OpenGL recebe RGB entre 0 e 1.

    No OpenCV com uint8, H vai de 0 a 179 e S/V de 0 a 255.
    A segunda paleta altera apenas a matiz, preservando S e V.
    """
    matizes = (np.array([10, 40, 85, 115, 145]) + 35 * paleta) % 180
    hsv = np.zeros((1, len(FACES), 3), dtype=np.uint8)
    hsv[0, :, 0] = matizes
    hsv[0, :, 1] = 190
    hsv[0, :, 2] = 235
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return rgb[0].astype(float) / 255.0
