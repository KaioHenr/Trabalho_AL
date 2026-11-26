"""Etapa 3: para onde a cadeia vai no longo prazo?

Distribuição estacionária pi de P̂ (Serra, Vila Velha, ES) por três métodos:
  1. sistema linear (P^T - I) pi^T = 0 com uma equação trocada pela normalização;
  2. método das potências explícito, a partir de e1, e4 e da uniforme, até ||pi^(k+1) - pi^(k)||_1 < 1e-12;
  3. autovetor à esquerda de lambda = 1 (autovetor de P̂^T).
Também: menor k com P̂^k > 0 contra o limite de Wielandt, e pi contra a frequência empírica.

Executar:  python -m src.etapa3
"""

# [IA] Claude Code (claude-opus-5-5) – 2026-11-25 – implementação da Etapa 3 (pi por três métodos)
import numpy as np
import pandas as pd

from src import markov as mk
from src.etapa1 import ESCOLHIDO, NIVEIS, PASTA_TABELAS, SERRA
from src.etapa2 import estimar_tres_P

TOL_POTENCIAS = 1e-12
TOL_CONCORDANCIA = 1e-10
PONTOS_DE_PARTIDA = {
    "e1": np.array([1.0, 0, 0, 0]),
    "e4": np.array([0, 0, 0, 1.0]),
    "uniforme": np.full(4, 0.25),
}


def frequencia_empirica(niveis):
    """Fração das semanas observadas em cada nível 1..4."""
    contagem = pd.Series(niveis).dropna().astype(int).value_counts()
    total = contagem.sum()
    return np.array([contagem.get(k, 0) / total for k in NIVEIS])


def pi_por_tres_metodos(P):
    """Devolve lista de (método, pi, nº de iterações ou None)."""
    resultados = [("sistema_linear", mk.stationary_linear(P), None)]
    for nome, pi0 in PONTOS_DE_PARTIDA.items():
        pi, iteracoes = mk.stationary_power(P, pi0, tol=TOL_POTENCIAS)
        resultados.append((f"potencias_{nome}", pi, iteracoes))
    resultados.append(("autovetor_esquerda", mk.stationary_eig(P), None))
    return resultados


def main():
    print("Etapa 3")
    Ps, series = estimar_tres_P()
    niveis_por_serie = {
        "serra": series[SERRA]["nivel"],
        "vila_velha": series[ESCOLHIDO]["nivel"],
        "es": pd.concat([df["nivel"] for df in series.values()]),
    }
    n = 4
    wielandt = (n - 1) ** 2 + 1

    linhas_metodos, linhas_resumo, linhas_empirico, verificacoes = [], [], [], []
    for nome, P in Ps.items():
        resultados = pi_por_tres_metodos(P)
        for metodo, pi, it in resultados:
            linhas_metodos.append({"serie": nome, "metodo": metodo, "iteracoes": it,
                                   **{f"pi_{k}": pi[k - 1] for k in NIVEIS}})

        vetores = [pi for _, pi, _ in resultados]
        discrepancia = max(np.abs(a - b).sum() for a in vetores for b in vetores)
        pi = resultados[0][1]
        residuo = np.abs(pi @ P - pi).sum()
        lambda2 = np.abs(mk.spectrum(P)[1])
        iter_previstas = np.log(TOL_POTENCIAS) / np.log(lambda2)
        k_min = mk.min_k_positive(P)
        linhas_resumo.append({
            "serie": nome,
            "maior_discrepancia_L1_entre_metodos": discrepancia,
            "residuo_L1_piP_menos_pi": residuo,
            "modulo_lambda2": lambda2,
            "iteracoes_e1": resultados[1][2], "iteracoes_e4": resultados[2][2],
            "iteracoes_uniforme": resultados[3][2],
            "iteracoes_previstas_ln(tol)/ln|lambda2|": iter_previstas,
            "menor_k_Pk_positiva": k_min, "limite_wielandt": wielandt,
        })

        freq = frequencia_empirica(niveis_por_serie[nome])
        linhas_empirico.append({"serie": nome,
                                **{f"pi_{k}": pi[k - 1] for k in NIVEIS},
                                **{f"freq_{k}": freq[k - 1] for k in NIVEIS},
                                "norma1_pi_menos_freq": np.abs(pi - freq).sum()})

        verificacoes += [
            {"serie": nome, "verificacao": "três métodos concordam (L1 < 1e-10)",
             "valor": f"{discrepancia:.2e}", "ok": bool(discrepancia < TOL_CONCORDANCIA)},
            {"serie": nome, "verificacao": "resíduo ||pi P̂ - pi||_1 (registrado; < 1e-12)",
             "valor": f"{residuo:.2e}", "ok": bool(residuo < 1e-12)},
            {"serie": nome, "verificacao": "P̂ primitiva (P̂^k > 0 para algum k <= Wielandt)",
             "valor": str(k_min), "ok": k_min is not None},
            {"serie": nome, "verificacao": "pi >= 0 e soma 1",
             "valor": f"{pi.sum():.15f}", "ok": bool(np.all(pi >= 0) and abs(pi.sum() - 1) < 1e-12)},
        ]

    pd.DataFrame(linhas_metodos).to_csv(PASTA_TABELAS / "e3_pi_metodos.csv", index=False, float_format="%.10f")
    pd.DataFrame(linhas_resumo).to_csv(PASTA_TABELAS / "e3_resumo.csv", index=False, float_format="%.6g")
    pd.DataFrame(linhas_empirico).round(6).to_csv(PASTA_TABELAS / "e3_pi_vs_empirico.csv", index=False)
    v = pd.DataFrame(verificacoes)
    v.to_csv(PASTA_TABELAS / "e3_verificacoes.csv", index=False)
    if not v["ok"].all():
        raise AssertionError(f"Etapa 3: verificação falhou\n{v[~v['ok']]}")
    print(f"  pi por 3 métodos nas 3 séries; {len(v)} verificações ok")


if __name__ == "__main__":
    main()
# [/IA]
