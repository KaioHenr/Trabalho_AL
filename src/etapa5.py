"""Etapa 5: quanto tempo se fica e quanto se demora a chegar?

Para Serra, Vila Velha e ES:
- permanência média no nível i pelo modelo, 1/(1 - p_ii) (média da geométrica), contra a
  média das "corridas" observadas, excluindo as censuradas (início, fim da série ou lacuna);
- histograma das durações no nível 4 contra a geométrica Pr(D = d) = p44^(d-1) (1 - p44);
- matriz M de tempos médios de primeira passagem por 4 sistemas 3x3 e pela matriz
  fundamental Z, com conferência da fórmula de Kac m_jj = 1/pi_j;
- tempos empíricos de primeira passagem 1 -> 4 e 4 -> 1 contra m_14 e m_41.

Executar:  python -m src.etapa5
"""

# [IA] Claude Code (claude-opus-5-5) – 2026-11-26 – implementação da Etapa 5 (permanência e primeira passagem)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import markov as mk
from src.etapa1 import ESCOLHIDO, NIVEIS, PASTA_FIGURAS, PASTA_TABELAS, SERRA, UMA_SEMANA
from src.etapa2 import ROTULOS, TITULOS, estimar_tres_P

TOL = 1e-10


# ---------------------------------------------------------------- funções sobre as séries observadas

def blocos(df):
    """Divide a série em blocos de semanas consecutivas com nível registrado.

    Devolve uma lista de arrays de níveis; uma lacuna (ou semana sem nível) separa blocos.
    """
    d = df[df["nivel"].notna()].sort_values("data_iniSE")
    if d.empty:
        return []
    novo_bloco = (d["data_iniSE"].diff() != UMA_SEMANA).cumsum()
    return [g["nivel"].astype(int).to_numpy() for _, g in d.groupby(novo_bloco)]


def corridas(niveis):
    """Corridas (sequências máximas de semanas no mesmo nível) de um bloco.

    Devolve lista de (nível, duração, censurada). A primeira e a última corrida
    de cada bloco são censuradas: não sabemos quando começaram ou terminaram.
    """
    resultado, inicio = [], 0
    for t in range(1, len(niveis) + 1):
        if t == len(niveis) or niveis[t] != niveis[inicio]:
            censurada = inicio == 0 or t == len(niveis)
            resultado.append((int(niveis[inicio]), t - inicio, censurada))
            inicio = t
    return resultado


def tempos_primeira_passagem(niveis, i, j):
    """Para cada semana t no nível i, nº de semanas até a primeira visita a j (dentro do bloco).

    Devolve (lista de tempos observados, nº de casos censurados: j não ocorre antes do fim do bloco).
    Percorre o bloco de trás para frente guardando a próxima posição em que o nível é j.
    """
    tempos, censurados, proximo_j = [], 0, None
    for t in range(len(niveis) - 1, -1, -1):
        if niveis[t] == i:
            if proximo_j is None:
                censurados += 1
            else:
                tempos.append(proximo_j - t)
        if niveis[t] == j:
            proximo_j = t
    return tempos[::-1], censurados


def blocos_por_serie(series):
    return {
        "serra": blocos(series[SERRA]),
        "vila_velha": blocos(series[ESCOLHIDO]),
        "es": [b for df in series.values() for b in blocos(df)],
    }


# ---------------------------------------------------------------- execução

def main():
    print("Etapa 5")
    Ps, series = estimar_tres_P()
    blocos_serie = blocos_por_serie(series)
    linhas_perm, linhas_hist, linhas_pp, verificacoes, duracoes_4 = [], [], [], [], {}

    for nome, P in Ps.items():
        todas = [c for b in blocos_serie[nome] for c in corridas(b)]

        # permanência: modelo x corridas observadas não censuradas
        for k in NIVEIS:
            completas = [dur for (niv, dur, cens) in todas if niv == k and not cens]
            censuradas = sum(1 for (niv, _, cens) in todas if niv == k and cens)
            p_kk = P[k - 1, k - 1]
            linhas_perm.append({
                "serie": nome, "nivel": k, "p_ii": p_kk, "permanencia_modelo": 1 / (1 - p_kk),
                "permanencia_observada_media": np.mean(completas) if completas else np.nan,
                "permanencia_observada_mediana": np.median(completas) if completas else np.nan,
                # a média observada quase coincide com 1/(1-p_ii) por construção do estimador;
                # a forma da distribuição (dispersão, mediana) é que testa a hipótese geométrica
                "desvio_padrao_modelo": np.sqrt(p_kk) / (1 - p_kk),
                "desvio_padrao_observado": np.std(completas, ddof=1) if len(completas) > 1 else np.nan,
                "mediana_modelo": np.ceil(np.log(0.5) / np.log(p_kk)),
                "n_corridas_completas": len(completas), "n_corridas_censuradas": censuradas,
            })

        # histograma das durações no nível 4 x geométrica
        d4 = np.array([dur for (niv, dur, cens) in todas if niv == 4 and not cens])
        duracoes_4[nome] = (d4, P[3, 3])
        for d in range(1, int(d4.max()) + 1 if len(d4) else 1):
            linhas_hist.append({"serie": nome, "duracao": d, "n_observado": int((d4 == d).sum()),
                                "freq_observada": (d4 == d).mean() if len(d4) else np.nan,
                                "prob_geometrica": P[3, 3] ** (d - 1) * (1 - P[3, 3])})

        # matriz M por dois caminhos + Kac
        M_sis = mk.first_passage_systems(P)
        M_fund = mk.first_passage_fundamental(P)
        pi = mk.stationary_linear(P)
        pd.DataFrame(np.round(M_sis, 6), index=ROTULOS, columns=ROTULOS).to_csv(PASTA_TABELAS / f"e5_M_{nome}.csv")
        dif = np.abs(M_sis - M_fund).max()
        kac = np.abs(np.diag(M_sis) - 1 / pi).max()
        verificacoes += [
            {"serie": nome, "verificacao": "Kac: m_jj = 1/pi_j (tol 1e-10)", "valor": f"{kac:.2e}", "ok": bool(kac < TOL)},
            {"serie": nome, "verificacao": "M por 4 sistemas 3x3 = M pela matriz fundamental Z (tol 1e-10)",
             "valor": f"{dif:.2e}", "ok": bool(dif < TOL)},
        ]

        # primeira passagem empírica 1 -> 4 e 4 -> 1
        for i, j in ((1, 4), (4, 1)):
            tempos, cens = [], 0
            for b in blocos_serie[nome]:
                t, c = tempos_primeira_passagem(b, i, j)
                tempos += t
                cens += c
            linhas_pp.append({"serie": nome, "par": f"{i}->{j}", "m_modelo": M_sis[i - 1, j - 1],
                              "media_empirica": np.mean(tempos) if tempos else np.nan,
                              "mediana_empirica": np.median(tempos) if tempos else np.nan,
                              "n_semanas_de_partida": len(tempos), "n_censuradas": cens})

    pd.DataFrame(linhas_perm).round(6).to_csv(PASTA_TABELAS / "e5_permanencia.csv", index=False)
    pd.DataFrame(linhas_hist).round(6).to_csv(PASTA_TABELAS / "e5_duracoes_nivel4.csv", index=False)
    pd.DataFrame(linhas_pp).round(6).to_csv(PASTA_TABELAS / "e5_primeira_passagem.csv", index=False)
    v = pd.DataFrame(verificacoes)
    v.to_csv(PASTA_TABELAS / "e5_verificacoes.csv", index=False)
    if not v["ok"].all():
        raise AssertionError(f"Etapa 5: verificação falhou\n{v[~v['ok']]}")
    grafico_duracoes_nivel4(duracoes_4)
    print(f"  permanência, M, Kac e primeira passagem; {len(v)} verificações ok")


def grafico_duracoes_nivel4(duracoes_4):
    """Histograma das durações completas no nível 4 (barras) contra a geométrica do modelo (linha)."""
    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, (nome, (d4, p44)) in zip(eixos, duracoes_4.items()):
        limite = int(min(d4.max(), 60)) if len(d4) else 1
        x = np.arange(1, limite + 1)
        freq = np.array([(d4 == d).mean() for d in x]) if len(d4) else np.zeros(len(x))
        ax.bar(x, freq, color="0.8", edgecolor="black", linewidth=0.5,
               label=f"observado ({len(d4)} corridas completas)")
        ax.plot(x, p44 ** (x - 1) * (1 - p44), color="black", marker="o", markersize=3, linewidth=1,
                label=fr"geométrica, $\hat p_{{44}}$ = {p44:.3f}")
        ax.set_title(TITULOS[nome])
        ax.set_xlabel("duração no nível 4 (semanas)")
        ax.legend(fontsize=8)
    eixos[0].set_ylabel("frequência relativa / probabilidade")
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / "e5_duracoes_nivel4.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
# [/IA]
