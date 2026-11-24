"""Testes das Etapas 1 e 2 com séries pequenas construídas à mão (sem usar data/raw/)."""

import numpy as np
import pandas as pd

from src.etapa1 import contar_transicoes_por_blocos, remover_duplicatas, transicoes
from src.etapa2 import contagens, contagens_crosstab, estimar_P, estimar_P_laplace
from src import markov as mk


# [IA] Claude Code (claude-opus-5-5) – 2026-11-24 – testes com série pequena com lacuna (Seção 11)
def serie(semanas, niveis, versoes=None):
    """Série artificial: `semanas` = números de semana a partir de 04/01/2015 (0, 1, 2...)."""
    datas = pd.Timestamp("2015-01-04") + pd.to_timedelta(np.array(semanas) * 7, unit="D")
    return pd.DataFrame({
        "data_iniSE": datas,
        "SE": [201501 + s for s in semanas],
        "nivel": niveis,
        "versao_modelo": versoes or ["2026-01-01"] * len(semanas),
    })


def test_lacuna_interrompe_transicoes():
    # semanas 0,1,2,_,4,5 (falta a 3):  transições válidas = (0→1), (1→2), (4→5) = 3
    df = serie([0, 1, 2, 4, 5], [1, 2, 2, 3, 4])
    t = transicoes(df)
    assert len(t) == 3
    assert list(zip(t["de"], t["para"])) == [(1, 2), (2, 2), (3, 4)]   # 2→3 atravessaria a lacuna
    assert contar_transicoes_por_blocos(df) == 3


def test_nivel_ausente_interrompe_transicoes():
    # semana 2 sem nível: não há transição 1→? nem ?→3
    df = serie([0, 1, 2, 3, 4], [1, 1, np.nan, 3, 3])
    assert len(transicoes(df)) == 2          # (0→1) e (3→4)
    assert contar_transicoes_por_blocos(df) == 2


def test_duplicata_mantem_versao_mais_recente():
    df = serie([0, 1, 1, 2], [1, 2, 4, 4], versoes=["2026-01-01", "2025-01-01", "2026-06-01", "2026-01-01"])
    limpo, removidas = remover_duplicatas(df)
    assert removidas == 1
    assert list(limpo["nivel"]) == [1, 4, 4]   # semana 1 ficou com a versão de 2026-06-01 (nível 4)


def test_contagens_dois_caminhos_e_soma():
    df = serie([0, 1, 2, 4, 5, 6, 7], [1, 1, 2, 2, 3, 4, 4])
    t = transicoes(df)
    C = contagens(t)
    assert np.array_equal(C, contagens_crosstab(t))
    assert C.sum() == len(t) == 5
    assert C[0, 0] == 1 and C[0, 1] == 1 and C[1, 2] == 1 and C[2, 3] == 1 and C[3, 3] == 1


def test_estimadores_sao_estocasticos():
    C = np.array([[8, 2, 0, 0], [1, 5, 4, 0], [0, 3, 3, 4], [1, 0, 0, 9]])
    P = estimar_P(C)
    assert mk.is_stochastic(P, 1e-12)
    assert np.isclose(P[0, 1], 0.2)
    P_lap = estimar_P_laplace(C, alpha=0.5)
    assert mk.is_stochastic(P_lap, 1e-12)
    assert np.all(P_lap > 0)                    # Laplace elimina os zeros
    assert np.isclose(P_lap[0, 2], 0.5 / 12)    # (0 + 0,5) / (10 + 4·0,5)
# [/IA]
