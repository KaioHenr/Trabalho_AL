"""Testes de src/markov.py contra a Tabela 1 do enunciado e propriedades gerais.

Critério de tolerância (Tabela 1): |calculado - tabelado| < 1e-6.
Como a tabela traz 6 casas decimais, o erro de arredondamento dela é no máximo
5e-7, que já cabe dentro de 1e-6; por isso a comparação é feita diretamente.
"""

import numpy as np
import pytest

from src import markov as mk

# [IA] Claude Code (claude-opus-5-5) – 2026-11-18 – dados da Tabela 1 e testes de conferência
P_REF = np.array([
    [0.90, 0.08, 0.02, 0.00],
    [0.20, 0.65, 0.13, 0.02],
    [0.05, 0.15, 0.65, 0.15],
    [0.00, 0.05, 0.20, 0.75],
])

TOL = 1e-6

PI_REF = [0.498970, 0.205954, 0.174125, 0.120951]


def perto(calculado, esperado, tol=TOL):
    """True se todas as entradas diferem menos que tol."""
    return np.all(np.abs(np.asarray(calculado) - np.asarray(esperado)) < tol)


# ---------------- Tabela 1 ----------------

def test_tabela1_pi():
    assert perto(mk.stationary_linear(P_REF), PI_REF)


def test_tabela1_espectro():
    esp = mk.spectrum(P_REF)
    assert np.all(np.abs(esp.imag) < 1e-12)          # P_ref tem espectro real
    assert perto(esp.real, [1.0, 0.869971, 0.618816, 0.461213])


def test_tabela1_meia_vida():
    assert abs(mk.half_life(P_REF) - 4.976086) < TOL


def test_tabela1_menor_k_primitiva():
    assert mk.min_k_positive(P_REF) == 2


def test_tabela1_e1_P4():
    e1 = np.array([1.0, 0, 0, 0])
    assert perto(e1 @ mk.power_squaring(P_REF, 4), [0.728667, 0.172331, 0.077617, 0.021385])


def test_tabela1_norma_e1_P20_menos_pi():
    e1 = np.array([1.0, 0, 0, 0])
    dist = np.sum(np.abs(e1 @ mk.power_squaring(P_REF, 20) - mk.stationary_linear(P_REF)))
    assert abs(dist - 0.045556) < TOL


@pytest.mark.parametrize("funcao", [mk.first_passage_systems, mk.first_passage_fundamental])
def test_tabela1_primeira_passagem(funcao):
    M = funcao(P_REF)
    assert abs(M[0, 3] - 46.873065) < TOL   # m_14
    assert abs(M[3, 0] - 17.035647) < TOL   # m_41
    assert perto(np.diag(M), [2.004128, 4.855455, 5.743011, 8.267802])


def test_tabela1_absorcao_no_4():
    r = mk.absorbing_analysis(P_REF, absorventes=[3])
    assert perto(r["t"], [46.873065, 39.473684, 26.470588])
    assert perto(r["var"], [1788.363542, 1732.320352, 1427.271899])


def test_tabela1_B_transientes_2_3():
    r = mk.absorbing_analysis(P_REF, absorventes=[0, 3])
    assert r["transientes"] == [1, 2]
    assert perto(r["B"][0], [0.742718, 0.257282])   # saindo do nível 2
    assert perto(r["B"][1], [0.461165, 0.538835])   # saindo do nível 3


# ---------------- Propriedades e caminhos independentes ----------------

def matriz_estocastica_aleatoria(rng, n=4):
    A = rng.random((n, n))
    return A / A.sum(axis=1, keepdims=True)


def test_produto_de_estocasticas_e_estocastica():
    rng = np.random.default_rng(2026)
    for _ in range(50):
        A = matriz_estocastica_aleatoria(rng)
        B = matriz_estocastica_aleatoria(rng)
        assert mk.is_stochastic(A @ B)


def test_is_stochastic_rejeita_invalidas():
    assert mk.is_stochastic(P_REF)
    assert not mk.is_stochastic(P_REF * 1.01)              # linhas não somam 1
    negativa = P_REF.copy()
    negativa[0, 0], negativa[0, 3] = 0.92, -0.02
    assert not mk.is_stochastic(negativa)                  # entrada negativa


def test_pi_tres_metodos_concordam():
    pi_lin = mk.stationary_linear(P_REF)
    pi_eig = mk.stationary_eig(P_REF)
    assert np.sum(np.abs(pi_lin - pi_eig)) < 1e-10
    for pi0 in ([1.0, 0, 0, 0], [0, 0, 0, 1.0], [0.25] * 4):   # e1, e4, uniforme
        pi_pot, iteracoes = mk.stationary_power(P_REF, pi0, tol=1e-12)
        assert np.sum(np.abs(pi_pot - pi_lin)) < 1e-10
        assert iteracoes > 0
    assert np.sum(np.abs(pi_lin @ P_REF - pi_lin)) < 1e-12   # resíduo ||pi P - pi||_1


def test_autovalores_traco_e_determinante():
    esp = mk.spectrum(P_REF)
    assert abs(np.sum(esp) - np.trace(P_REF)) < 1e-10
    assert abs(np.prod(esp) - np.linalg.det(P_REF)) < 1e-10


def test_potencias_tres_caminhos_concordam():
    P52_quad = mk.power_squaring(P_REF, 52)
    P52_rep = mk.power_repeated(P_REF, 52)
    P52_diag, kappa = mk.power_diag(P_REF, 52)
    assert np.abs(P52_quad - P52_rep).sum() < 1e-10
    assert np.abs(P52_quad - P52_diag).sum() < 1e-10
    assert kappa >= 1.0
    assert mk.is_stochastic(P52_quad)


def test_kac():
    M = mk.first_passage_systems(P_REF)
    assert np.all(np.abs(np.diag(M) - 1.0 / mk.stationary_linear(P_REF)) < 1e-10)


def test_primeira_passagem_dois_caminhos_concordam():
    assert np.abs(mk.first_passage_systems(P_REF) - mk.first_passage_fundamental(P_REF)).max() < 1e-10


@pytest.mark.parametrize("absorventes", [[3], [0, 3]])
def test_B_linhas_somam_1(absorventes):
    B = mk.absorbing_analysis(P_REF, absorventes)["B"]
    assert np.all(np.abs(B.sum(axis=1) - 1.0) < 1e-12)


def test_neumann_converge_para_N():
    # Com o nível 4 absorvente, o raio espectral de Q é ~0,9766: o erro da soma
    # parcial cai como 0,9766^K, devagar. Com K = 1000 o erro ainda é ~1,5e-9;
    # com K = 2000 fica no nível do arredondamento (~5e-14).
    r = mk.absorbing_analysis(P_REF, absorventes=[3])
    erros = [np.abs(mk.neumann_partial(r["Q"], K) - r["N"]).max() for K in (10, 100, 2000)]
    assert erros[0] > erros[1] > erros[2]    # erro cai quando K cresce
    assert erros[2] < 1e-10


def test_nao_primitiva_devolve_none():
    periodica = np.array([[0.0, 1.0], [1.0, 0.0]])        # alterna 1,2,1,2: período 2
    assert mk.min_k_positive(periodica) is None
# [/IA]
