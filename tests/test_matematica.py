"""Testes dos conceitos matemáticos, sem precisar abrir uma janela."""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from geometria import VERTICES, FACES, NORMAIS, cores_faces, normal_face
from trackball import mapear_mouse, quat_arraste, multiplicar, matriz_rotacao


class MatematicaTests(unittest.TestCase):
    def test_normais_unitarias_perpendiculares_e_externas(self):
        centro = VERTICES.mean(axis=0)
        for face, normal in zip(FACES, NORMAIS):
            pontos = VERTICES[list(face)]
            self.assertAlmostEqual(np.linalg.norm(normal), 1)
            self.assertAlmostEqual(np.dot(normal, pontos[1] - pontos[0]), 0)
            self.assertAlmostEqual(np.dot(normal, pontos[2] - pontos[0]), 0)
            self.assertGreater(np.dot(normal, pontos.mean(axis=0) - centro), 0)

    def test_face_degenerada(self):
        with self.assertRaises(ValueError):
            normal_face(np.zeros(3), np.zeros(3), np.zeros(3))

    def test_base_quadrada_plana(self):
        bases = [face for face in FACES if len(face) == 4]
        self.assertEqual(len(bases), 1)
        pontos = VERTICES[list(bases[0])]
        arestas = np.roll(pontos, -1, axis=0) - pontos
        np.testing.assert_allclose(np.linalg.norm(arestas, axis=1), [2, 2, 2, 2])
        for i in range(4):
            self.assertAlmostEqual(np.dot(arestas[i], arestas[(i + 1) % 4]), 0)
        np.testing.assert_allclose(pontos[:, 1], [-1, -1, -1, -1])
        np.testing.assert_allclose(NORMAIS[FACES.index(bases[0])], [0, -1, 0])

    def test_mapeamento_hemisferio(self):
        np.testing.assert_allclose(mapear_mouse(500, 360, 1000, 720), [0, 0, 1])
        for x, y in [(0, 0), (1000, 720), (650, 300)]:
            vetor = mapear_mouse(x, y, 1000, 720)
            self.assertAlmostEqual(np.linalg.norm(vetor), 1)
            self.assertGreaterEqual(vetor[2], 0)

    def test_rotacao_entre_vetores(self):
        inicio = np.array([0., 0., 1.])
        for fim in [np.array([1., 0., 0.]), inicio, -inicio]:
            q = quat_arraste(inicio, fim)
            self.assertAlmostEqual(np.linalg.norm(q), 1)
            np.testing.assert_allclose(matriz_rotacao(q)[:3, :3] @ inicio, fim, atol=1e-12)

    def test_composicao_e_estabilidade(self):
        q = quat_arraste(np.array([0., 0., 1.]), np.array([1., 0., 0.]))
        acumulado = np.array([1., 0., 0., 0.])
        for _ in range(1000):
            acumulado = multiplicar(q, acumulado)
        self.assertAlmostEqual(np.linalg.norm(acumulado), 1)
        r = matriz_rotacao(acumulado)[:3, :3]
        np.testing.assert_allclose(r.T @ r, np.eye(3), atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(r), 1)
        np.testing.assert_allclose(matriz_rotacao(multiplicar(q, q)),
                                   matriz_rotacao(q) @ matriz_rotacao(q), atol=1e-12)

    def test_cor_hsv_convertida_para_rgb(self):
        cores = cores_faces()
        self.assertEqual(cores.shape, (len(FACES), 3))
        self.assertTrue(np.all((cores >= 0) & (cores <= 1)))
        self.assertFalse(np.allclose(cores, cores_faces(1)))


if __name__ == "__main__":
    unittest.main()
