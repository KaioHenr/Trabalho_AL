"""Testes da Etapa 5 com séries pequenas construídas à mão e com a matriz de referência."""

import numpy as np
import pandas as pd

from src import markov as mk
from src.etapa5 import blocos, corridas, tempos_primeira_passagem

# [IA] Claude Code (claude-opus-5-5) – 2026-11-26 – testes da Etapa 5
P_REF = np.array([
    [0.90, 0.08, 0.02, 0.00],
    [0.20, 0.65, 0.13, 0.02],
    [0.05, 0.15, 0.65, 0.15],
    [0.00, 0.05, 0.20, 0.75],
])


def test_corridas_censura_inicio_e_fim():
    # 1 1 | 2 2 2 | 1 | 4 4   -> primeira (1,2) e última (4,2) são censuradas
    c = corridas(np.array([1, 1, 2, 2, 2, 1, 4, 4]))
    assert c == [(1, 2, True), (2, 3, False), (1, 1, False), (4, 2, True)]


def test_bloco_unico_e_todo_censurado():
    assert corridas(np.array([3, 3, 3])) == [(3, 3, True)]


def test_lacuna_separa_blocos():
    datas = pd.Timestamp("2015-01-04") + pd.to_timedelta(np.array([0, 1, 2, 4, 5]) * 7, unit="D")
    df = pd.DataFrame({"data_iniSE": datas, "nivel": [1, 1, 2, 2, 2]})
    b = blocos(df)
    assert [list(x) for x in b] == [[1, 1, 2], [2, 2]]
    # a corrida de nível 2 que atravessaria a lacuna vira duas corridas censuradas
    assert corridas(b[0])[-1] == (2, 1, True) and corridas(b[1]) == [(2, 2, True)]


def test_tempos_primeira_passagem():
    # posições: 0:1 1:1 2:2 3:4 4:1 5:3
    tempos, cens = tempos_primeira_passagem(np.array([1, 1, 2, 4, 1, 3]), 1, 4)
    assert tempos == [3, 2]        # da posição 0 leva 3 semanas, da 1 leva 2
    assert cens == 1               # da posição 4 o nível 4 não aparece mais no bloco


def test_tabela1_primeira_passagem_e_kac():
    M = mk.first_passage_systems(P_REF)
    assert abs(M[0, 3] - 46.873065) < 1e-6 and abs(M[3, 0] - 17.035647) < 1e-6
    assert np.abs(np.diag(M) - 1 / mk.stationary_linear(P_REF)).max() < 1e-10
    assert np.abs(M - mk.first_passage_fundamental(P_REF)).max() < 1e-10
# [/IA]
