"""Confere os callbacks com posições de mouse simuladas, sem abrir janela."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import glfw
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from main import Aplicacao


class InteracaoTests(unittest.TestCase):
    def test_l_alterna_luz_apenas_ao_pressionar(self):
        app = Aplicacao()
        app.tecla(None, glfw.KEY_L, 0, glfw.PRESS, 0)
        self.assertFalse(app.iluminacao)
        app.tecla(None, glfw.KEY_L, 0, glfw.REPEAT, 0)
        app.tecla(None, glfw.KEY_L, 0, glfw.RELEASE, 0)
        self.assertFalse(app.iluminacao)
        app.tecla(None, glfw.KEY_L, 0, glfw.PRESS, 0)
        self.assertTrue(app.iluminacao)

    def test_clique_arraste_e_soltar(self):
        app = Aplicacao()
        inicial = app.orientacao.copy()
        with patch("main.glfw.get_window_size", return_value=(1000, 720)), \
             patch("main.glfw.get_cursor_pos", return_value=(500, 360)):
            app.movimento(None, 600, 360)
            np.testing.assert_allclose(app.orientacao, inicial)
            app.clique(None, glfw.MOUSE_BUTTON_LEFT, glfw.PRESS, 0)
            app.movimento(None, 600, 360)
            self.assertFalse(np.allclose(app.orientacao, inicial))
            self.assertAlmostEqual(np.linalg.norm(app.orientacao), 1)
            app.clique(None, glfw.MOUSE_BUTTON_LEFT, glfw.RELEASE, 0)
            apos_arraste = app.orientacao.copy()
            app.movimento(None, 700, 360)
            np.testing.assert_allclose(app.orientacao, apos_arraste)

    def test_controles_e_reinicio(self):
        app = Aplicacao()
        inicial = app.orientacao.copy()
        for tecla in (glfw.KEY_C, glfw.KEY_L, glfw.KEY_D, glfw.KEY_W, glfw.KEY_EQUAL):
            app.tecla(None, tecla, 0, glfw.PRESS, 0)
        self.assertEqual(app.paleta, 1)
        self.assertFalse(app.iluminacao)
        np.testing.assert_allclose(app.posicao, [0.1, 0.1, 0])
        self.assertAlmostEqual(app.escala, 1.1)
        app.rolagem(None, 0, 1000)
        self.assertEqual(app.distancia, 3.5)
        app.rolagem(None, 0, -1000)
        self.assertEqual(app.distancia, 15)
        app.tecla(None, glfw.KEY_R, 0, glfw.PRESS, 0)
        np.testing.assert_allclose(app.orientacao, inicial)
        np.testing.assert_allclose(app.posicao, np.zeros(3))
        self.assertEqual(app.escala, 1)
        self.assertEqual(app.distancia, 7)
        self.assertTrue(app.iluminacao)
        self.assertEqual(app.paleta, 0)


if __name__ == "__main__":
    unittest.main()
