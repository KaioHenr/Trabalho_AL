"""Etapa 7: a matriz prevê bem o que não viu?

Para Serra e Vila Velha:
- P̂_treino estimada só com transições inteiramente em 2015–2022 (as duas semanas antes de 2023);
- para cada semana t de 2023–2025 e horizonte h em {1, 4, 8}: previsão p = e_{X_t} P̂_treino^h;
- pontuação de Brier multicategoria (1/T) sum ||p_t - e_{X_{t+h}}||_2^2 e pontuação logarítmica
  -(1/T) sum ln p_t(X_{t+h}), com piso de 1e-6;
- referências: persistência (p = e_{X_t}) e climatologia (p = pi_treino);
- gráfico de 2024: probabilidade prevista de nível 4 com h = 4 e o nível observado.

Executar:  python -m src.etapa7
"""

# [IA] Claude Code (claude-opus-5-5) – 2026-11-27 – implementação da Etapa 7 (previsão fora da amostra)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import markov as mk
from src.etapa1 import ESCOLHIDO, NIVEIS, PASTA_FIGURAS, PASTA_TABELAS, SERRA, UMA_SEMANA, transicoes
from src.etapa2 import ROTULOS, contagens, estimar_P
from src.etapa1 import carregar_todas_series

INICIO_TESTE = pd.Timestamp("2023-01-01")      # início da SE 1 de 2023
HORIZONTES = [1, 4, 8]
PISO_LOG = 1e-6
MUNICIPIOS = {"serra": SERRA, "vila_velha": ESCOLHIDO}
TITULOS = {"serra": "Serra", "vila_velha": "Vila Velha"}


def transicoes_treino(df):
    """Transições cujas DUAS semanas são anteriores a 2023 (nenhuma informação do teste)."""
    t = transicoes(df)
    destino = pd.to_datetime(t["data_de"]) + UMA_SEMANA
    return t[destino < INICIO_TESTE].reset_index(drop=True)


def pares_de_teste(df, h):
    """Pares (data de origem, X_t, X_{t+h}) com origem em 2023–2025 e semana t+h observada."""
    nivel_por_data = df.dropna(subset=["nivel"]).set_index("data_iniSE")["nivel"].astype(int)
    origens = nivel_por_data[nivel_por_data.index >= INICIO_TESTE]
    pares = []
    for data, x in origens.items():
        alvo = data + h * UMA_SEMANA
        if alvo in nivel_por_data.index:
            pares.append((data, x, int(nivel_por_data[alvo])))
    return pares


def brier(previsoes, observados):
    """Brier multicategoria: média de ||p - e_obs||_2^2."""
    E = np.eye(4)[np.asarray(observados) - 1]
    return float(np.mean(np.sum((previsoes - E) ** 2, axis=1)))


def log_score(previsoes, observados):
    """Pontuação logarítmica: média de -ln p(observado), com piso de 1e-6."""
    p_obs = previsoes[np.arange(len(observados)), np.asarray(observados) - 1]
    return float(np.mean(-np.log(np.maximum(p_obs, PISO_LOG))))


def prever(P_h, pi_treino, origens, metodo):
    """Matriz T x 4 com as previsões de cada semana de teste pelo método indicado."""
    if metodo == "markov":
        return P_h[np.asarray(origens) - 1]                 # linha X_t de P^h = e_{X_t} P^h
    if metodo == "persistencia":
        return np.eye(4)[np.asarray(origens) - 1]
    if metodo == "climatologia":
        return np.tile(pi_treino, (len(origens), 1))
    raise ValueError(metodo)


def main():
    print("Etapa 7")
    series = carregar_todas_series()
    linhas, verificacoes, dados_2024 = [], [], {}

    for nome, geocode in MUNICIPIOS.items():
        df = series[geocode]
        treino = transicoes_treino(df)
        P_treino = estimar_P(contagens(treino))
        pi_treino = mk.stationary_linear(P_treino)
        pd.DataFrame(np.round(P_treino, 6), index=ROTULOS, columns=ROTULOS).to_csv(
            PASTA_TABELAS / f"e7_P_treino_{nome}.csv")
        ultimo_destino = (pd.to_datetime(treino["data_de"]) + UMA_SEMANA).max()
        verificacoes.append({"serie": nome, "verificacao": "nenhuma transição de treino toca 2023 ou depois",
                             "valor": f"última semana usada: {ultimo_destino.date()}",
                             "ok": bool(ultimo_destino < INICIO_TESTE)})

        for h in HORIZONTES:
            P_h = mk.power_squaring(P_treino, h)
            P_h_diag, _ = mk.power_diag(P_treino, h)
            pares = pares_de_teste(df, h)
            datas, origens, alvos = zip(*pares)
            for metodo in ("markov", "persistencia", "climatologia"):
                prev = prever(P_h, pi_treino, origens, metodo)
                linhas.append({"serie": nome, "h": h, "metodo": metodo, "T": len(pares),
                               "brier": brier(prev, alvos), "log": log_score(prev, alvos)})
                soma = np.abs(prev.sum(axis=1) - 1).max()
                verificacoes.append({"serie": nome, "verificacao": f"previsões somam 1 ({metodo}, h={h})",
                                     "valor": f"{soma:.2e}", "ok": bool(soma < 1e-12)})
            dif = np.abs(P_h - P_h_diag).max()
            verificacoes.append({"serie": nome, "verificacao": f"P_treino^{h}: quadrados sucessivos = diagonalização",
                                 "valor": f"{dif:.2e}", "ok": bool(dif < 1e-10)})
            if h == 4:
                alvo_datas = [d + 4 * UMA_SEMANA for d in datas]
                p4 = prever(P_h, pi_treino, origens, "markov")[:, 3]
                dados_2024[nome] = pd.DataFrame({"data_alvo": alvo_datas, "prob_nivel4_h4": p4,
                                                 "nivel_observado": alvos})

    tabela = pd.DataFrame(linhas)
    tabela.round(6).to_csv(PASTA_TABELAS / "e7_pontuacoes.csv", index=False)
    for nome, d in dados_2024.items():
        d.to_csv(PASTA_TABELAS / f"e7_previsao_h4_{nome}.csv", index=False, float_format="%.6f")
    v = pd.DataFrame(verificacoes)
    v.to_csv(PASTA_TABELAS / "e7_verificacoes.csv", index=False)
    if not v["ok"].all():
        raise AssertionError(f"Etapa 7: verificação falhou\n{v[~v['ok']]}")
    grafico_2024(dados_2024)
    print(f"  pontuações de Brier e log para h = 1, 4, 8; {len(v)} verificações ok")


def grafico_2024(dados_2024):
    """2024: probabilidade prevista de nível 4 (h = 4) e o nível observado, por município."""
    fig, eixos = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for ax, (nome, d) in zip(eixos, dados_2024.items()):
        d = d[(d["data_alvo"] >= "2024-01-01") & (d["data_alvo"] < "2025-01-01")]
        ax.fill_between(d["data_alvo"], 0, (d["nivel_observado"] == 4).astype(float), step="mid",
                        color="0.85", label="semanas observadas em nível 4")
        ax.plot(d["data_alvo"], d["prob_nivel4_h4"], color="black", marker="o", markersize=3,
                linewidth=1, label="prob. prevista de nível 4 (h = 4)")
        ax.set_ylim(0, 1.02)
        ax.set_ylabel("probabilidade")
        ax2 = ax.twinx()
        ax2.step(d["data_alvo"], d["nivel_observado"], where="mid", color="black", linestyle="--",
                 linewidth=0.8, label="nível observado")
        ax2.set_ylim(0.5, 4.5)
        ax2.set_yticks(NIVEIS)
        ax2.set_ylabel("nível observado")
        ax.set_title(TITULOS[nome])
        linhas1, rot1 = ax.get_legend_handles_labels()
        linhas2, rot2 = ax2.get_legend_handles_labels()
        ax.legend(linhas1 + linhas2, rot1 + rot2, fontsize=7, loc="upper right")
    eixos[-1].set_xlabel("semana prevista (2024)")
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / "e7_previsao_2024.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
# [/IA]
