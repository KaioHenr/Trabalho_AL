"""Etapa 4: por quanto tempo o presente informa o futuro?

Para Serra, Vila Velha e ES:
- espectro de P̂, |lambda_2| e meia-vida n_1/2 = ln(1/2)/ln|lambda_2|;
- P̂^52 por quadrados sucessivos (explícito) e por V Lambda^52 V^-1, com ||diferença||_1 e kappa_1(V);
- curvas ||e_i P̂^n - pi||_1 em escala log, com a reta de referência C |lambda_2|^n.
Verificação: soma dos autovalores = traço e produto = determinante (tol 1e-10).

Executar:  python -m src.etapa4
"""

# [IA] Claude Code (claude-opus-5-5) – 2026-11-25 – implementação da Etapa 4 (espectro, P^52, convergência)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import markov as mk
from src.etapa1 import NIVEIS, PASTA_FIGURAS, PASTA_TABELAS
from src.etapa2 import ROTULOS, TITULOS, estimar_tres_P

N_POTENCIA = 52          # um ano de semanas
N_CURVA = 150            # horizonte do gráfico de convergência
N_AJUSTE_REF = 30        # a reta C|lambda_2|^n é ancorada na maior curva em n = 30
TOL = 1e-10
ESTILOS = [("-", "o"), ("--", "s"), ("-.", "^"), (":", "D")]   # distingue as curvas sem usar cor


def main():
    print("Etapa 4")
    Ps, _ = estimar_tres_P()
    linhas_espectro, linhas_resumo, verificacoes, curvas = [], [], [], {}

    for nome, P in Ps.items():
        esp = mk.spectrum(P)
        for k, lam in enumerate(esp, start=1):
            linhas_espectro.append({"serie": nome, "k": k, "real": lam.real, "imag": lam.imag, "modulo": abs(lam)})
        lambda2 = abs(esp[1])
        meia_vida = mk.half_life(P)

        P52_quad = mk.power_squaring(P, N_POTENCIA)
        P52_diag, kappa1 = mk.power_diag(P, N_POTENCIA)
        P52_rep = mk.power_repeated(P, N_POTENCIA)
        dif_diag = np.linalg.norm(P52_quad - P52_diag, 1)
        dif_rep = np.linalg.norm(P52_quad - P52_rep, 1)
        pd.DataFrame(np.round(P52_quad, 6), index=ROTULOS, columns=ROTULOS).to_csv(
            PASTA_TABELAS / f"e4_P52_{nome}.csv")

        pi = mk.stationary_linear(P)
        d = {i: mk.convergence_curve(P, np.eye(4)[i - 1], pi, N_CURVA) for i in NIVEIS}
        curvas[nome] = (d, lambda2)
        pd.DataFrame({"n": range(N_CURVA + 1), **{f"dist_e{i}": d[i] for i in NIVEIS}}).to_csv(
            PASTA_TABELAS / f"e4_convergencia_{nome}.csv", index=False, float_format="%.10g")

        linhas_resumo.append({
            "serie": nome, "modulo_lambda2": lambda2, "meia_vida_semanas": meia_vida,
            "lambda2_complexo": bool(abs(esp[1].imag) > 1e-12),
            "norma1_P52quad_menos_P52diag": dif_diag, "norma1_P52quad_menos_P52rep": dif_rep,
            "kappa1_V": kappa1,
            "dist_e1_n52": d[1][52], "dist_e4_n52": d[4][52],
        })
        soma_ok = abs(esp.sum() - np.trace(P)) < TOL
        prod_ok = abs(np.prod(esp) - np.linalg.det(P)) < TOL
        verificacoes += [
            {"serie": nome, "verificacao": "soma dos autovalores = traço (tol 1e-10)",
             "valor": f"{abs(esp.sum() - np.trace(P)):.2e}", "ok": bool(soma_ok)},
            {"serie": nome, "verificacao": "produto dos autovalores = determinante (tol 1e-10)",
             "valor": f"{abs(np.prod(esp) - np.linalg.det(P)):.2e}", "ok": bool(prod_ok)},
            {"serie": nome, "verificacao": "P̂^52: quadrados sucessivos = diagonalização (||dif||_1 < 1e-10)",
             "valor": f"{dif_diag:.2e}", "ok": bool(dif_diag < TOL)},
            {"serie": nome, "verificacao": "lambda_1 = 1",
             "valor": f"{abs(esp[0] - 1):.2e}", "ok": bool(abs(esp[0] - 1) < TOL)},
        ]

    pd.DataFrame(linhas_espectro).to_csv(PASTA_TABELAS / "e4_espectro.csv", index=False, float_format="%.6f")
    pd.DataFrame(linhas_resumo).to_csv(PASTA_TABELAS / "e4_resumo.csv", index=False, float_format="%.6g")
    v = pd.DataFrame(verificacoes)
    v.to_csv(PASTA_TABELAS / "e4_verificacoes.csv", index=False)
    if not v["ok"].all():
        raise AssertionError(f"Etapa 4: verificação falhou\n{v[~v['ok']]}")
    grafico_convergencia(curvas)
    print(f"  espectro, meia-vida, P^52 e convergência; {len(v)} verificações ok")


def grafico_convergencia(curvas):
    """||e_i P̂^n - pi||_1 em escala log, uma curva por estado inicial, mais a reta C |lambda_2|^n."""
    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.5), sharey=True)
    n = np.arange(N_CURVA + 1)
    for ax, (nome, (d, lambda2)) in zip(eixos, curvas.items()):
        for i, (linha, marcador) in zip(NIVEIS, ESTILOS):
            ax.semilogy(n, d[i], linestyle=linha, marker=marcador, markevery=15, markersize=4,
                        color="black", linewidth=1, label=f"início no nível {i}")
        C = max(d[i][N_AJUSTE_REF] for i in NIVEIS) / lambda2 ** N_AJUSTE_REF
        ax.semilogy(n, C * lambda2 ** n, color="0.55", linewidth=2.5, alpha=0.7,
                    label=fr"$C\,|\lambda_2|^n$, $|\lambda_2|$ = {lambda2:.4f}")
        ax.set_title(TITULOS[nome])
        ax.set_xlabel("n (semanas)")
        ax.set_ylim(1e-10, 3)
        ax.grid(color="0.9", linewidth=0.5)
        ax.legend(fontsize=7)
    eixos[0].set_ylabel(r"$\|e_i \hat P^n - \pi\|_1$")
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / "e4_convergencia.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
# [/IA]
