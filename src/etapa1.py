"""Etapa 1: os dados contam a história que pensamos?

Auditoria dos dados congelados em data/raw/: semanas esperadas e observadas,
lacunas, duplicatas, transições válidas, semanas por nível e versões do modelo.
Também confere os hashes com o manifesto, sorteia as semanas da conferência
com o Canal 2 e gera as figuras da etapa.

Estrutura de funções definida pelo aluno; implementação conforme o bloco [IA] abaixo.

Executar:  python -m src.etapa1
"""

# [IA] Claude Code (claude-opus-5-5) – 2026-11-24 – implementação da Etapa 1 (auditoria, hashes, figuras)
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")            # gera figuras sem abrir janela
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.download import ler_manifesto, sha256_arquivo

RAIZ = Path(__file__).resolve().parent.parent
PASTA_RAW = RAIZ / "data" / "raw"
PASTA_CONFERENCIA = RAIZ / "data" / "conferencia"     # preenchida à mão pelo aluno
PASTA_RESULTADOS = RAIZ / "results"
PASTA_TABELAS = PASTA_RESULTADOS / "tabelas"
PASTA_FIGURAS = PASTA_RESULTADOS / "figuras"

SERRA = 3205002
ESCOLHIDO = 3205200               # Vila Velha
NIVEIS = [1, 2, 3, 4]

# Período do enunciado: SE 1 de 2015 (começa em 04/01/2015) até SE 53 de 2025 (começa em 28/12/2025)
PRIMEIRA_SEMANA = pd.Timestamp("2015-01-04")
ULTIMA_SEMANA = pd.Timestamp("2025-12-28")
UMA_SEMANA = pd.Timedelta(days=7)

# Critérios de elegibilidade do 2º município (Seção 5)
MIN_SEMANAS_POR_NIVEL = 5
MIN_TRANSICOES = 400


# ---------------------------------------------------------------- leitura

def ler_serie(caminho):
    """Lê o CSV bruto de um município e devolve as linhas ordenadas da semana mais antiga para a mais recente."""
    df = pd.read_csv(caminho, parse_dates=["data_iniSE"], dtype={"versao_modelo": str})
    return df.sort_values(["data_iniSE", "versao_modelo"]).reset_index(drop=True)


def remover_duplicatas(df):
    """Remove semanas repetidas (mesma SE), mantendo a linha de versao_modelo mais recente.

    Critério: se o InfoDengue publicou a mesma semana mais de uma vez, a versão
    mais recente do modelo incorpora as revisões posteriores dos dados.
    Devolve (df_sem_duplicatas, número de linhas removidas).
    """
    ordenado = df.sort_values(["SE", "versao_modelo"])
    limpo = ordenado.drop_duplicates(subset="SE", keep="last")
    limpo = limpo.sort_values("data_iniSE").reset_index(drop=True)
    return limpo, len(df) - len(limpo)


def transicoes(df):
    """Lista de transições válidas (X_t, X_{t+1}) de uma série SEM duplicatas.

    Válida = as duas semanas são consecutivas no calendário (datas de início
    separadas por exatamente 7 dias) e ambas têm nível registrado. Assim,
    nenhuma transição atravessa uma semana ausente; e a SE 53 não precisa de
    regra especial, porque a comparação é feita pelas datas.
    Devolve DataFrame com colunas: de, para, data_de, SE_de.
    """
    d = df.sort_values("data_iniSE").reset_index(drop=True)
    datas = d["data_iniSE"]
    niveis = d["nivel"]
    consecutiva = (datas.shift(-1) - datas) == UMA_SEMANA
    ambas_com_nivel = niveis.notna() & niveis.shift(-1).notna()
    ok = consecutiva & ambas_com_nivel
    return pd.DataFrame({
        "de": niveis[ok].astype(int).to_numpy(),
        "para": niveis.shift(-1)[ok].astype(int).to_numpy(),
        "data_de": datas[ok].to_numpy(),
        "SE_de": d.loc[ok, "SE"].to_numpy(),
    })


def contar_transicoes_por_blocos(df):
    """Segundo caminho para o nº de transições válidas (conferência independente).

    Considera só as semanas com nível e as divide em blocos de semanas
    consecutivas. Um bloco com k semanas gera k - 1 transições; então o total
    é (nº de semanas com nível) - (nº de blocos).
    """
    d = df[df["nivel"].notna()].sort_values("data_iniSE")
    if d.empty:
        return 0
    quebras = (d["data_iniSE"].diff() != UMA_SEMANA).sum()   # a 1ª linha também conta (diff = NaT)
    return len(d) - int(quebras)


# ---------------------------------------------------------------- auditoria

def auditar(df_bruto):
    """Auditoria de um município a partir do DataFrame bruto (como lido do CSV)."""
    df, n_duplicatas = remover_duplicatas(df_bruto)
    esperadas = pd.date_range(PRIMEIRA_SEMANA, ULTIMA_SEMANA, freq="7D")
    observadas = set(df["data_iniSE"])
    contagem = df["nivel"].value_counts()
    n_validas = len(transicoes(df))
    r = {
        "semanas_esperadas": len(esperadas),
        "semanas_observadas": len(df),
        "lacunas": len(set(esperadas) - observadas),
        "semanas_fora_do_periodo": len(observadas - set(esperadas)),
        "duplicatas": n_duplicatas,
        "nivel_ausente": int(df["nivel"].isna().sum()),
        "transicoes_validas": n_validas,
        "transicoes_por_blocos": contar_transicoes_por_blocos(df),
    }
    for k in NIVEIS:
        r[f"n_nivel_{k}"] = int(contagem.get(k, 0))
    versoes = df["versao_modelo"].dropna()
    r["n_versoes_modelo"] = versoes.nunique()
    r["versao_modelo_min"] = versoes.min()
    r["versao_modelo_max"] = versoes.max()
    r["elegivel"] = (all(r[f"n_nivel_{k}"] >= MIN_SEMANAS_POR_NIVEL for k in NIVEIS)
                     and n_validas >= MIN_TRANSICOES)
    return r


def carregar_municipios():
    """Tabela geocode -> nome dos 78 municípios (arquivo congelado do IBGE)."""
    with open(PASTA_RAW / "municipios_es.json", encoding="utf-8") as f:
        dados = json.load(f)
    return pd.DataFrame({"geocode": [m["id"] for m in dados], "municipio": [m["nome"] for m in dados]})


def carregar_todas_series():
    """Dicionário geocode -> série sem duplicatas, para os 78 municípios."""
    series = {}
    for g in carregar_municipios()["geocode"]:
        df, _ = remover_duplicatas(ler_serie(PASTA_RAW / f"{g}.csv"))
        series[g] = df
    return series


def auditar_todos():
    """Roda auditar() nos 78 municípios e salva results/e1_auditoria.csv."""
    municipios = carregar_municipios()
    linhas = []
    for g, nome in zip(municipios["geocode"], municipios["municipio"]):
        r = auditar(ler_serie(PASTA_RAW / f"{g}.csv"))
        linhas.append({"geocode": g, "municipio": nome, **r})
    tabela = pd.DataFrame(linhas)
    tabela.to_csv(PASTA_RESULTADOS / "e1_auditoria.csv", index=False)
    return tabela


def verificar_auditoria(tabela):
    """Verificações obrigatórias da Etapa 1. Salva o resultado e interrompe se alguma falhar."""
    soma_niveis = tabela[[f"n_nivel_{k}" for k in NIVEIS]].sum(axis=1)
    checagens = {
        "soma das semanas por nível = semanas observadas com nível":
            bool((soma_niveis == tabela["semanas_observadas"] - tabela["nivel_ausente"]).all()),
        "transições: contagem direta = contagem por blocos (nenhuma atravessa lacuna)":
            bool((tabela["transicoes_validas"] == tabela["transicoes_por_blocos"]).all()),
        "só níveis 1 a 4 nos dados":
            bool(all(set(s["nivel"].dropna().unique()) <= set(NIVEIS) for s in carregar_todas_series().values())),
    }
    resultado = pd.DataFrame({"verificacao": list(checagens), "ok": list(checagens.values())})
    resultado.to_csv(PASTA_TABELAS / "e1_verificacoes.csv", index=False)
    if not resultado["ok"].all():
        raise AssertionError(f"Etapa 1: verificação falhou\n{resultado}")
    return resultado


def conferir_hashes():
    """Compara o SHA-256 atual de cada arquivo de data/raw/ com o do manifesto."""
    m = ler_manifesto()
    m["sha256_atual"] = [sha256_arquivo(PASTA_RAW / a) for a in m["arquivo"]]
    m["confere"] = m["sha256"] == m["sha256_atual"]
    m[["arquivo", "sha256", "sha256_atual", "confere"]].to_csv(PASTA_TABELAS / "e1_hashes.csv", index=False)
    if not m["confere"].all():
        raise AssertionError(f"hash diferente do manifesto: {list(m.loc[~m['confere'], 'arquivo'])}")
    return m


# ---------------------------------------------------------------- conferências externas (Canais 2 e 3)

def sortear_semanas_conferencia(n=10):
    """Sorteia n semanas de Serra e n do escolhido (semente 2026) para conferir no site do InfoDengue.

    Gera results/tabelas/e1_canal2_sorteio.csv com o nível da API e uma coluna
    'nivel_site' vazia. O aluno copia esse arquivo para
    data/conferencia/e1_canal2_preenchido.csv e preenche à mão o nível visto no site.
    """
    rng = np.random.default_rng(2026)
    partes = []
    for g in (SERRA, ESCOLHIDO):
        df, _ = remover_duplicatas(ler_serie(PASTA_RAW / f"{g}.csv"))
        idx = np.sort(rng.choice(len(df), size=n, replace=False))
        s = df.iloc[idx][["SE", "data_iniSE", "nivel", "versao_modelo"]].copy()
        s.insert(0, "geocode", g)
        s = s.rename(columns={"nivel": "nivel_api"})
        s["nivel_site"] = ""
        s["observacao"] = ""
        partes.append(s)
    sorteio = pd.concat(partes, ignore_index=True)
    sorteio.to_csv(PASTA_TABELAS / "e1_canal2_sorteio.csv", index=False)
    return sorteio


def resumir_conferencia_canal2():
    """Se o aluno já preencheu a conferência, calcula a concordância API x site."""
    caminho = PASTA_CONFERENCIA / "e1_canal2_preenchido.csv"
    if not caminho.exists():
        print("  (conferência do Canal 2 ainda não preenchida: data/conferencia/e1_canal2_preenchido.csv)")
        return None
    c = pd.read_csv(caminho)
    c = c[c["nivel_site"].notna()]
    c["concorda"] = c["nivel_api"] == c["nivel_site"]
    resumo = c.groupby("geocode")["concorda"].agg(semanas_conferidas="size", concordantes="sum").reset_index()
    resumo.to_csv(PASTA_TABELAS / "e1_canal2_resumo.csv", index=False)
    return resumo


def casos_anuais_serra():
    """Totais anuais de Serra na API (para comparar com o boletim da Sesa, Canal 3).

    casos   = casos notificados na semana;  casprov = casos prováveis.
    A comparação com o boletim é de ordem de grandeza, não de igualdade.
    """
    df, _ = remover_duplicatas(ler_serie(PASTA_RAW / f"{SERRA}.csv"))
    df["ano"] = df["SE"] // 100
    anual = df.groupby("ano")[["casos", "casprov"]].sum(min_count=1).reset_index()
    anual.to_csv(PASTA_TABELAS / "e1_serra_casos_anuais.csv", index=False)
    return anual


# ---------------------------------------------------------------- figuras (legíveis em preto e branco)

def grafico_niveis_serra():
    """Sequência semanal dos níveis de alerta de Serra, 2015–2025."""
    df, _ = remover_duplicatas(ler_serie(PASTA_RAW / f"{SERRA}.csv"))
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.step(df["data_iniSE"], df["nivel"], where="post", color="black", linewidth=0.8)
    ax.set_yticks(NIVEIS, ["1 verde", "2 amarelo", "3 laranja", "4 vermelho"])
    ax.set_ylim(0.5, 4.5)
    ax.set_xlabel("Semana epidemiológica (data de início)")
    ax.set_ylabel("Nível de alerta")
    ax.grid(axis="y", color="0.85", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / "e1_niveis_serra.png", dpi=300)
    plt.close(fig)


def mapa_calor_municipio_ano():
    """Fração de semanas com nível >= 3, por município (linhas) e ano (colunas), em escala de cinza."""
    municipios = carregar_municipios().set_index("geocode")["municipio"]
    linhas = {}
    for g, df in carregar_todas_series().items():
        d = df[df["nivel"].notna()]
        linhas[municipios[g]] = (d["nivel"] >= 3).groupby(d["SE"] // 100).mean()
    tabela = pd.DataFrame(linhas).T.sort_index(axis=1)
    tabela = tabela.loc[tabela.mean(axis=1).sort_values(ascending=False).index]   # mais alertas no topo
    tabela.to_csv(PASTA_TABELAS / "e1_fracao_nivel3mais_municipio_ano.csv")

    fig, ax = plt.subplots(figsize=(7, 13))
    im = ax.imshow(tabela.to_numpy(), cmap="Greys", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(tabela.shape[1]), tabela.columns, fontsize=7)
    ax.set_yticks(range(tabela.shape[0]), tabela.index, fontsize=5)
    for rotulo in ax.get_yticklabels():
        if rotulo.get_text() in (municipios[SERRA], municipios[ESCOLHIDO]):
            rotulo.set_fontweight("bold")
            rotulo.set_fontsize(7)
    ax.set_xlabel("Ano")
    fig.colorbar(im, ax=ax, fraction=0.04, label="Fração de semanas com nível ≥ 3")
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / "e1_mapa_calor_nivel3mais.png", dpi=300)
    plt.close(fig)


# ---------------------------------------------------------------- execução

def main():
    for pasta in (PASTA_TABELAS, PASTA_FIGURAS):
        pasta.mkdir(parents=True, exist_ok=True)
    print("Etapa 1")
    conferir_hashes()
    print("  hashes conferem com o manifesto")
    tabela = auditar_todos()
    verificar_auditoria(tabela)
    print(f"  auditoria de {len(tabela)} municípios; verificações ok; elegíveis: {int(tabela['elegivel'].sum())}")
    escolhido = tabela.loc[tabela["geocode"] == ESCOLHIDO].iloc[0]
    print(f"  {escolhido['municipio']}: elegível = {escolhido['elegivel']}, "
          f"transições = {escolhido['transicoes_validas']}")
    sortear_semanas_conferencia()
    resumir_conferencia_canal2()
    casos_anuais_serra()
    grafico_niveis_serra()
    mapa_calor_municipio_ano()
    print("  tabelas e figuras salvas em results/")


if __name__ == "__main__":
    main()
# [/IA]
