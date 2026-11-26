"""Testes das Etapas 3 e 4 com a matriz de referência P_ref (Tabela 1) e séries pequenas."""

import numpy as np

from src import markov as mk
from src.etapa3 import frequencia_empirica, pi_por_tres_metodos

# [IA] Claude Code (claude-opus-5-5) – 2026-11-25 – testes das Etapas 3 e 4
P_REF = np.array([
    [0.90, 0.08, 0.02, 0.00],
    [0.20, 0.65, 0.13, 0.02],
    [0.05, 0.15, 0.65, 0.15],
    [0.00, 0.05, 0.20, 0.75],
])
PI_REF = [0.498970, 0.205954, 0.174125, 0.120951]


def test_tres_metodos_reproduzem_tabela1_e_concordam():
    resultados = pi_por_tres_metodos(P_REF)
    assert len(resultados) == 5                      # linear, 3 pontos de partida, autovetor
    for _, pi, _ in resultados:
        assert np.all(np.abs(pi - PI_REF) < 1e-6)
    vetores = [pi for _, pi, _ in resultados]
    assert max(np.abs(a - b).sum() for a in vetores for b in vetores) < 1e-10


def test_iteracoes_coerentes_com_lambda2():
    # o erro cai como |lambda_2|^k: o nº de iterações deve ser da ordem de ln(1e-12)/ln|lambda_2|
    lambda2 = abs(mk.spectrum(P_REF)[1])
    previstas = np.log(1e-12) / np.log(lambda2)
    for _, _, it in pi_por_tres_metodos(P_REF)[1:4]:
        assert 0.5 * previstas < it < 1.5 * previstas


def test_frequencia_empirica():
    f = frequencia_empirica([1, 1, 2, 4, np.nan, 4, 4, 1])
    assert np.allclose(f, [3 / 7, 1 / 7, 0, 3 / 7])


def test_curva_de_convergencia_tabela1():
    pi = mk.stationary_linear(P_REF)
    d = mk.convergence_curve(P_REF, [1.0, 0, 0, 0], pi, 20)
    assert abs(d[20] - 0.045556) < 1e-6            # ||e1 P^20 - pi||_1 da Tabela 1
    assert np.all(np.diff(d) < 0)                    # a distância só diminui neste caso


def test_curva_bate_com_potencia_explicita():
    pi = mk.stationary_linear(P_REF)
    d = mk.convergence_curve(P_REF, [0, 0, 0, 1.0], pi, 52)
    direto = np.abs(np.array([0, 0, 0, 1.0]) @ mk.power_squaring(P_REF, 52) - pi).sum()
    assert abs(d[52] - direto) < 1e-12
# [/IA]
