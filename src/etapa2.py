"""Etapa 2: como estimar a matriz e quanto confiar nela?

Para Serra, Vila Velha e o ES agregado:
- matriz de contagens C = (n_ij), contada por dois caminhos independentes;
- estimador de máxima verossimilhança P̂ = n_ij / n_i e erros-padrão;
- suavização de Laplace (alpha = 0,5) e seu efeito na distribuição estacionária.

Executar:  python -m src.etapa2   (depois da Etapa 1)
"""

# [IA] Claude Code (claude-opus-5-5) – 2026-11-24 – implementação da Etapa 2 (contagens, P̂, erros-padrão, Laplace)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import markov as mk
from src.etapa1 import (ESCOLHIDO, NIVEIS, PASTA_FIGURAS, PASTA_RESULTADOS, PASTA_TABELAS, SERRA,
                        carregar_todas_series, transicoes)

ALPHA = 0.5
ROTULOS = [f"nivel_{k}" for k in NIVEIS]      # sem acento: abre bem no Excel


def contagens(trans):
    """Matriz C 4x4: C[i-1, j-1] = nº de transições do nível i para o nível j (laço explícito)."""
    C = np.zeros((4, 4), dtype=int)
    for i, j in zip(trans["de"], trans["para"]):
        C[i - 1, j - 1] += 1
    return C


def contagens_crosstab(trans):
    """Mesma matriz C por um caminho independente: tabela de contingência do pandas."""
    tab = pd.crosstab(trans["de"], trans["para"]).reindex(index=NIVEIS, columns=NIVEIS, fill_value=0)
    return tab.to_numpy()


def estimar_P(C):
    """Máxima verossimilhança: p_ij = n_ij / n_i, com n_i = soma da linha i de C."""
    n_i = C.sum(axis=1, keepdims=True)
    if np.any(n_i == 0):
        raise ValueError("há nível sem nenhuma transição de saída; a linha de P̂ fica indefinida")
    return C / n_i


def erros_padrao(C):
    """Erro-padrão aproximado de cada p_ij: sqrt(p_ij (1 - p_ij) / n_i)."""
    P = estimar_P(C)
    n_i = C.sum(axis=1, keepdims=True)
    return np.sqrt(P * (1 - P) / n_i)


def estimar_P_laplace(C, alpha=ALPHA):
    """Suavização de Laplace: (n_ij + alpha) / (n_i + 4 alpha). Nenhuma entrada fica zero."""
    n_i = C.sum(axis=1, keepdims=True)
    return (C + alpha) / (n_i + C.shape[1] * alpha)


def matrizes_das_tres_series():
    """Dicionário nome -> (C, nº de transições) para Serra, Vila Velha e ES agregado.

    O ES agregado é a SOMA das matrizes de contagens dos 78 municípios.
    """
    series = carregar_todas_series()
    C_por_municipio = {g: contagens(transicoes(df)) for g, df in series.items()}
    return {
        "serra": C_por_municipio[SERRA],
        "vila_velha": C_por_municipio[ESCOLHIDO],
        "es": sum(C_por_municipio.values()),
    }, series


def salvar_matriz(M, nome, casas=6):
    pd.DataFrame(np.round(M, casas), index=ROTULOS, columns=ROTULOS).to_csv(PASTA_TABELAS / nome)


def mapa_calor(Ps, caminho):
    """Mapas de calor de P̂ (escala de cinza, valores escritos nas células)."""
    fig, eixos = plt.subplots(1, 3, figsize=(13, 5))
    titulos = {"serra": "Serra", "vila_velha": "Vila Velha", "es": "ES agregado"}
    for ax, (nome, P) in zip(eixos, Ps.items()):
        ax.imshow(P, cmap="Greys", vmin=0, vmax=1)
        for i in range(4):
            for j in range(4):
                ax.text(j, i, f"{P[i, j]:.3f}", ha="center", va="center", fontsize=9,
                        color="white" if P[i, j] > 0.5 else "black")
        ax.set_xticks(range(4), NIVEIS)
        ax.set_yticks(range(4), NIVEIS)
        ax.set_xlabel("nível na semana seguinte (j)")
        ax.set_ylabel("nível na semana atual (i)")
        ax.set_title(titulos[nome])
    fig.tight_layout()
    fig.savefig(caminho, dpi=300)
    plt.close(fig)


def main():
    print("Etapa 2")
    Cs, series = matrizes_das_tres_series()
    auditoria = pd.read_csv(PASTA_RESULTADOS / "e1_auditoria.csv")
    transicoes_e1 = {
        "serra": int(auditoria.loc[auditoria["geocode"] == SERRA, "transicoes_validas"].iloc[0]),
        "vila_velha": int(auditoria.loc[auditoria["geocode"] == ESCOLHIDO, "transicoes_validas"].iloc[0]),
        "es": int(auditoria["transicoes_validas"].sum()),
    }
    C_crosstab = {
        "serra": contagens_crosstab(transicoes(series[SERRA])),
        "vila_velha": contagens_crosstab(transicoes(series[ESCOLHIDO])),
        "es": sum(contagens_crosstab(transicoes(df)) for df in series.values()),
    }

    verificacoes, resumo_pi, Ps = [], [], {}
    for nome, C in Cs.items():
        P = estimar_P(C)
        P_lap = estimar_P_laplace(C)
        Ps[nome] = P
        salvar_matriz(C, f"e2_C_{nome}.csv", casas=0)
        salvar_matriz(P, f"e2_P_{nome}.csv")
        salvar_matriz(erros_padrao(C), f"e2_EP_{nome}.csv")
        salvar_matriz(P_lap, f"e2_P_laplace_{nome}.csv")

        pi = mk.stationary_linear(P)
        pi_lap = mk.stationary_linear(P_lap)
        resumo_pi.append({"serie": nome, **{f"pi_{k}": pi[k - 1] for k in NIVEIS},
                          **{f"pi_laplace_{k}": pi_lap[k - 1] for k in NIVEIS},
                          "norma1_pi_menos_pi_laplace": np.abs(pi - pi_lap).sum(),
                          "zeros_em_P": int((C == 0).sum())})

        verificacoes += [
            {"serie": nome, "verificacao": "P̂ >= 0 e P̂·1 = 1 (tol 1e-12)", "valor": "", "ok": mk.is_stochastic(P, 1e-12)},
            {"serie": nome, "verificacao": "P̂ Laplace >= 0 e linhas somam 1 (tol 1e-12)", "valor": "",
             "ok": mk.is_stochastic(P_lap, 1e-12)},
            {"serie": nome, "verificacao": "soma de C = transições válidas da Etapa 1",
             "valor": f"{C.sum()} = {transicoes_e1[nome]}", "ok": bool(C.sum() == transicoes_e1[nome])},
            {"serie": nome, "verificacao": "C por laço = C por crosstab (segundo caminho)",
             "valor": f"max |dif| = {np.abs(C - C_crosstab[nome]).max()}",
             "ok": bool(np.array_equal(C, C_crosstab[nome]))},
        ]

    pd.DataFrame(resumo_pi).round(6).to_csv(PASTA_TABELAS / "e2_pi_laplace.csv", index=False)
    v = pd.DataFrame(verificacoes)
    v.to_csv(PASTA_TABELAS / "e2_verificacoes.csv", index=False)
    if not v["ok"].all():
        raise AssertionError(f"Etapa 2: verificação falhou\n{v[~v['ok']]}")
    mapa_calor(Ps, PASTA_FIGURAS / "e2_mapas_P.png")
    print(f"  C, P̂, erros-padrão e Laplace salvos; {len(v)} verificações ok")


if __name__ == "__main__":
    main()
# [/IA]
