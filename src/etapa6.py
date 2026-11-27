"""Etapa 6: quando o amarelo acende, o vermelho virá?

Para Serra, Vila Velha e ES:
(a) nível 4 absorvente: N = (I - Q)^-1, t = N 1 e desvio-padrão do tempo até o primeiro vermelho;
(b) transientes {2, 3} e absorventes {1, 4}: B = N R (prob. de chegar ao vermelho antes do verde);
(c) verificação empírica de (b): episódios que começam na entrada em 2 vindo de 1 e terminam na
    primeira visita a 1 ou a 4; proporção terminada em 4 com IC binomial de 95%;
(d) N pela inversa contra as somas parciais da série de Neumann I + Q + ... + Q^K.

Executar:  python -m src.etapa6
"""

# [IA] Claude Code (claude-opus-5-5) – 2026-11-27 – implementação da Etapa 6 (cadeia absorvente)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest

from src import markov as mk
from src.etapa1 import PASTA_FIGURAS, PASTA_TABELAS
from src.etapa2 import TITULOS, estimar_tres_P
from src.etapa5 import blocos_por_serie

TOL = 1e-10
VALORES_K = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
CENARIOS = {"abs4": [3], "abs1e4": [0, 3]}     # índices base 0: nível 4 -> 3, nível 1 -> 0


def episodios_amarelo(niveis):
    """Episódios que começam na entrada no nível 2 vindo do nível 1 e terminam em 1 ou 4.

    Devolve (lista com o nível final de cada episódio completo, nº de episódios censurados:
    o bloco acabou antes de o episódio chegar a 1 ou 4).
    """
    finais, censurados = [], 0
    for t in range(1, len(niveis)):
        if niveis[t - 1] == 1 and niveis[t] == 2:
            fim = next((niveis[s] for s in range(t + 1, len(niveis)) if niveis[s] in (1, 4)), None)
            if fim is None:
                censurados += 1
            else:
                finais.append(int(fim))
    return finais, censurados


def erro_neumann(Q, N, valores_K):
    """Maior erro absoluto entre N e a soma parcial de Neumann, para cada K (soma acumulada em laço)."""
    erros, soma, termo, k_atual = {}, np.eye(len(Q)), np.eye(len(Q)), 0
    for K in valores_K:
        while k_atual < K:
            termo = termo @ Q
            soma = soma + termo
            k_atual += 1
        erros[K] = np.abs(soma - N).max()
    return erros


def main():
    print("Etapa 6")
    Ps, series = estimar_tres_P()
    blocos_serie = blocos_por_serie(series)
    linhas_t, linhas_B, linhas_emp, linhas_neu, verificacoes = [], [], [], [], []
    curvas = {}

    for nome, P in Ps.items():
        # (a) nível 4 absorvente
        r4 = mk.absorbing_analysis(P, CENARIOS["abs4"])
        Q4 = r4["Q"]
        t_solve = np.linalg.solve(np.eye(3) - Q4, np.ones(3))       # segundo caminho para t
        for idx, nivel in enumerate([1, 2, 3]):
            linhas_t.append({"serie": nome, "nivel_inicial": nivel, "t_medio_ate_nivel4": r4["t"][idx],
                             "variancia": r4["var"][idx], "desvio_padrao": np.sqrt(r4["var"][idx])})
        pd.DataFrame(np.round(r4["N"], 6), index=["nivel_1", "nivel_2", "nivel_3"],
                     columns=["nivel_1", "nivel_2", "nivel_3"]).to_csv(PASTA_TABELAS / f"e6_N_abs4_{nome}.csv")

        # (b) transientes {2, 3}, absorventes {1, 4}
        rb = mk.absorbing_analysis(P, CENARIOS["abs1e4"])
        B = rb["B"]
        for idx, nivel in enumerate([2, 3]):
            linhas_B.append({"serie": nome, "nivel_inicial": nivel,
                             "prob_absorver_em_1": B[idx, 0], "prob_absorver_em_4": B[idx, 1]})

        # (c) episódios empíricos
        finais, cens = [], 0
        for b in blocos_serie[nome]:
            f, c = episodios_amarelo(b)
            finais += f
            cens += c
        n_ep = len(finais)
        n_4 = sum(1 for f in finais if f == 4)
        ic = binomtest(n_4, n_ep).proportion_ci(confidence_level=0.95, method="exact") if n_ep else None
        linhas_emp.append({"serie": nome, "B_de_2_para_4_modelo": B[0, 1], "n_episodios": n_ep,
                           "n_terminados_em_4": n_4, "proporcao_empirica": n_4 / n_ep if n_ep else np.nan,
                           "ic95_inf": ic.low if ic else np.nan, "ic95_sup": ic.high if ic else np.nan,
                           "modelo_dentro_do_ic": bool(ic and ic.low <= B[0, 1] <= ic.high),
                           "n_censurados": cens})

        # (d) série de Neumann
        for cenario, r in (("abs4", r4), ("abs1e4", rb)):
            erros = erro_neumann(r["Q"], r["N"], VALORES_K)
            rho = max(abs(np.linalg.eigvals(r["Q"])))
            curvas[(nome, cenario)] = (erros, rho)
            for K, e in erros.items():
                linhas_neu.append({"serie": nome, "cenario": cenario, "K": K, "erro_max": e,
                                   "raio_espectral_Q": rho})

        erro_final_4 = curvas[(nome, "abs4")][0][VALORES_K[-1]]
        erro_final_b = curvas[(nome, "abs1e4")][0][VALORES_K[-1]]
        verificacoes += [
            {"serie": nome, "verificacao": "B·1 = 1 (tol 1e-12)",
             "valor": f"{np.abs(B.sum(axis=1) - 1).max():.2e}", "ok": bool(np.abs(B.sum(axis=1) - 1).max() < 1e-12)},
            {"serie": nome, "verificacao": "t = N·1 igual a solve((I-Q), 1) (tol 1e-10)",
             "valor": f"{np.abs(r4['t'] - t_solve).max():.2e}", "ok": bool(np.abs(r4["t"] - t_solve).max() < TOL)},
            {"serie": nome, "verificacao": f"N inversa = soma de Neumann K={VALORES_K[-1]}, nível 4 absorvente (tol 1e-10)",
             "valor": f"{erro_final_4:.2e}", "ok": bool(erro_final_4 < TOL)},
            {"serie": nome, "verificacao": f"N inversa = soma de Neumann K={VALORES_K[-1]}, 1 e 4 absorventes (tol 1e-10)",
             "valor": f"{erro_final_b:.2e}", "ok": bool(erro_final_b < TOL)},
            {"serie": nome, "verificacao": "variâncias >= 0", "valor": f"{r4['var'].min():.4g}",
             "ok": bool(np.all(r4["var"] >= 0))},
            {"serie": nome, "verificacao": "t saindo de 1 (4 absorvente) = m_14 da Etapa 5 (tol 1e-10)",
             "valor": f"{abs(r4['t'][0] - mk.first_passage_systems(P)[0, 3]):.2e}",
             "ok": bool(abs(r4["t"][0] - mk.first_passage_systems(P)[0, 3]) < TOL)},
        ]

    pd.DataFrame(linhas_t).round(6).to_csv(PASTA_TABELAS / "e6_tempo_ate_vermelho.csv", index=False)
    pd.DataFrame(linhas_B).round(6).to_csv(PASTA_TABELAS / "e6_B_absorcao.csv", index=False)
    pd.DataFrame(linhas_emp).round(6).to_csv(PASTA_TABELAS / "e6_episodios_empiricos.csv", index=False)
    pd.DataFrame(linhas_neu).to_csv(PASTA_TABELAS / "e6_neumann.csv", index=False, float_format="%.6g")
    v = pd.DataFrame(verificacoes)
    v.to_csv(PASTA_TABELAS / "e6_verificacoes.csv", index=False)
    if not v["ok"].all():
        raise AssertionError(f"Etapa 6: verificação falhou\n{v[~v['ok']]}")
    grafico_neumann(curvas)
    print(f"  N, t, desvio-padrão, B, episódios e Neumann; {len(v)} verificações ok")


def grafico_neumann(curvas):
    """Erro de N contra a soma parcial de Neumann, em escala log, com a referência rho(Q)^K."""
    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    estilos = {"abs4": ("-", "o", "nível 4 absorvente"), "abs1e4": ("--", "s", "1 e 4 absorventes")}
    K = np.array(VALORES_K)
    for ax, nome in zip(eixos, TITULOS):
        for cenario, (linha, marcador, rotulo) in estilos.items():
            erros, rho = curvas[(nome, cenario)]
            ax.loglog(K, [max(erros[k], 1e-17) for k in K], linestyle=linha, marker=marcador,
                      color="black", markersize=4, linewidth=1, label=fr"{rotulo} ($\rho(Q)$ = {rho:.4f})")
        ax.set_title(TITULOS[nome])
        ax.set_xlabel("K (nº de termos da soma parcial)")
        ax.grid(color="0.9", linewidth=0.5)
        ax.legend(fontsize=7)
    eixos[0].set_ylabel(r"$\max|N - \sum_{k=0}^{K} Q^k|$")
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / "e6_neumann.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
# [/IA]
