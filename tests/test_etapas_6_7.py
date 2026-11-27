"""Testes das Etapas 6 e 7 com séries pequenas construídas à mão e com a matriz de referência."""

import numpy as np
import pandas as pd

from src import markov as mk
from src.etapa6 import episodios_amarelo, erro_neumann
from src.etapa7 import brier, log_score, pares_de_teste, prever, transicoes_treino

# [IA] Claude Code (claude-opus-5-5) – 2026-11-27 – testes das Etapas 6 e 7
P_REF = np.array([
    [0.90, 0.08, 0.02, 0.00],
    [0.20, 0.65, 0.13, 0.02],
    [0.05, 0.15, 0.65, 0.15],
    [0.00, 0.05, 0.20, 0.75],
])


def serie_semanal(inicio, niveis):
    datas = pd.Timestamp(inicio) + pd.to_timedelta(np.arange(len(niveis)) * 7, unit="D")
    return pd.DataFrame({"data_iniSE": datas, "SE": range(len(niveis)), "nivel": niveis})


# ---------------- Etapa 6

def test_episodios_amarelo():
    # 1→2 abre episódio que termina em 4; 1→2 abre outro que termina em 1; 1→2 final fica censurado.
    # 3→2 não abre episódio (não veio do nível 1).
    finais, cens = episodios_amarelo(np.array([1, 2, 3, 4, 3, 2, 1, 2, 2, 1, 2, 3]))
    assert finais == [4, 1]
    assert cens == 1


def test_B_tabela1_e_linhas_somam_1():
    B = mk.absorbing_analysis(P_REF, [0, 3])["B"]
    assert np.allclose(B, [[0.742718, 0.257282], [0.461165, 0.538835]], atol=1e-6)
    assert np.abs(B.sum(axis=1) - 1).max() < 1e-12


def test_neumann_erro_diminui():
    r = mk.absorbing_analysis(P_REF, [3])
    erros = erro_neumann(r["Q"], r["N"], [10, 100, 2000])
    assert erros[10] > erros[100] > erros[2000]
    assert erros[2000] < 1e-10


# ---------------- Etapa 7

def test_treino_nao_usa_2023():
    # semanas de 18/12/2022 a 08/01/2023: só a transição 18/12 → 25/12 fica no treino
    df = serie_semanal("2022-12-18", [1, 2, 3, 4])
    t = transicoes_treino(df)
    assert len(t) == 1 and (t["de"].iloc[0], t["para"].iloc[0]) == (1, 2)


def test_pares_de_teste():
    df = serie_semanal("2023-01-01", [1, 2, 3, 4, 4])
    assert pares_de_teste(df, 1)[0][1:] == (1, 2)
    assert len(pares_de_teste(df, 4)) == 1           # só a 1ª semana tem a semana t+4 observada


def test_pontuacoes_casos_simples():
    perfeita = np.array([[0, 0, 0, 1.0]])
    assert brier(perfeita, [4]) == 0 and log_score(perfeita, [4]) == 0
    errada = np.array([[1.0, 0, 0, 0]])
    assert brier(errada, [4]) == 2                    # (1-0)^2 + (0-1)^2
    assert np.isclose(log_score(errada, [4]), -np.log(1e-6))    # piso de 1e-6
    uniforme = np.full((1, 4), 0.25)
    assert np.isclose(brier(uniforme, [2]), 0.75)


def test_previsao_markov_e_linha_de_P_h():
    P4 = mk.power_squaring(P_REF, 4)
    prev = prever(P4, None, [1], "markov")
    assert np.allclose(prev[0], [0.728667, 0.172331, 0.077617, 0.021385], atol=1e-6)   # e1 P^4 da Tabela 1
    assert np.allclose(prever(None, None, [3], "persistencia"), [[0, 0, 1, 0]])
# [/IA]
