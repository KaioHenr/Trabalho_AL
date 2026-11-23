import argparse
import hashlib
import io
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# [IA] Claude Code (claude-opus-5-5) – 2026-11-18 – download único com manifesto SHA-256
RAIZ = Path(__file__).resolve().parent.parent
PASTA_RAW = RAIZ / "data" / "raw"
MANIFESTO = RAIZ / "data" / "MANIFEST.txt"

URL_MUNICIPIOS = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/32/municipios"
URL_POPULACAO = "https://apisidra.ibge.gov.br/values/t/4709/n6/in%20n3%2032/v/93/p/2022"
URL_DENGUE = ("https://info.dengue.mat.br/api/alertcity?geocode={g}&disease=dengue"
              "&format=csv&ew_start=1&ew_end=53&ey_start=2015&ey_end=2025")

COLUNAS_ESSENCIAIS = {"data_iniSE", "SE", "nivel", "versao_modelo"}
PAUSA_ENTRE_REQUISICOES = 1.0   # segundos, para respeitar o servidor
TENTATIVAS = 4


def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 16), b""):
            h.update(bloco)
    return h.hexdigest()


def baixar(url):
   for tentativa in range(1, TENTATIVAS + 1):
        try:
            resposta = requests.get(url, timeout=60)
            resposta.raise_for_status()
            if not resposta.content.strip():
                raise ValueError("resposta vazia")
            return resposta.content
        except (requests.RequestException, ValueError) as erro:
            if tentativa == TENTATIVAS:
                raise RuntimeError(f"falha ao baixar {url}: {erro}") from erro
            espera = 2 ** tentativa
            print(f"  tentativa {tentativa} falhou ({erro}); nova tentativa em {espera} s")
            time.sleep(espera)


def conferir_csv_dengue(conteudo, geocode):
    df = pd.read_csv(io.BytesIO(conteudo))
    faltando = COLUNAS_ESSENCIAIS - set(df.columns)
    if faltando:
        raise RuntimeError(f"{geocode}: colunas ausentes {sorted(faltando)}")
    return len(df), int(df["SE"].min()), int(df["SE"].max())


def salvar(conteudo, caminho):
    caminho.write_bytes(conteudo)
    return sha256_arquivo(caminho)


def ler_manifesto(caminho=MANIFESTO):
    return pd.read_csv(caminho, comment="#")


def download_completo():
    if MANIFESTO.exists() or any(PASTA_RAW.glob("*.csv")):
        sys.exit("ERRO: data/raw/ já contém dados ou o manifesto já existe. "
                 "O download é feito uma única vez; nada foi alterado.")
    PASTA_RAW.mkdir(parents=True, exist_ok=True)
    inicio = datetime.now(timezone.utc)
    registros = []   # (arquivo, url, linhas, sha256)

    print("Baixando lista de municípios do IBGE...")
    conteudo = baixar(URL_MUNICIPIOS)
    municipios = pd.read_json(io.BytesIO(conteudo))
    if len(municipios) != 78:
        raise RuntimeError(f"esperados 78 municípios, vieram {len(municipios)}")
    registros.append(("municipios_es.json", URL_MUNICIPIOS, len(municipios),
                      salvar(conteudo, PASTA_RAW / "municipios_es.json")))
    time.sleep(PAUSA_ENTRE_REQUISICOES)

    print("Baixando população do Censo 2022 (SIDRA 4709)...")
    conteudo = baixar(URL_POPULACAO)
    n_pop = len(pd.read_json(io.BytesIO(conteudo))) - 1   # 1ª linha do SIDRA é cabeçalho
    registros.append(("populacao_censo2022.json", URL_POPULACAO, n_pop,
                      salvar(conteudo, PASTA_RAW / "populacao_censo2022.json")))
    time.sleep(PAUSA_ENTRE_REQUISICOES)

    for k, geocode in enumerate(municipios["id"], start=1):
        url = URL_DENGUE.format(g=geocode)
        conteudo = baixar(url)
        linhas, se_min, se_max = conferir_csv_dengue(conteudo, geocode)
        arquivo = f"{geocode}.csv"
        registros.append((arquivo, url, linhas, salvar(conteudo, PASTA_RAW / arquivo)))
        print(f"[{k:2d}/78] {geocode}: {linhas} linhas, SE {se_min} a {se_max}")
        time.sleep(PAUSA_ENTRE_REQUISICOES)

    fim = datetime.now(timezone.utc)
    with open(MANIFESTO, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Manifesto dos dados brutos congelados (gerado por src/download.py)\n")
        f.write(f"# inicio_download_utc: {inicio.isoformat(timespec='seconds')}\n")
        f.write(f"# fim_download_utc: {fim.isoformat(timespec='seconds')}\n")
        f.write("# linhas = linhas de dados (sem cabeçalho); sha256 = hash do arquivo em data/raw/\n")
        pd.DataFrame(registros, columns=["arquivo", "url", "linhas", "sha256"]).to_csv(
            f, index=False, lineterminator="\n")
    print(f"\nConcluído: {len(registros)} arquivos em data/raw/ e manifesto em {MANIFESTO}")


def download_teste(geocode, saida):
    """Baixa um único município para `saida` (fora de data/raw/) e mostra as colunas."""
    saida = Path(saida).resolve()
    if saida == PASTA_RAW.resolve():
        sys.exit("ERRO: o modo de teste não grava em data/raw/.")
    saida.mkdir(parents=True, exist_ok=True)
    url = URL_DENGUE.format(g=geocode)
    conteudo = baixar(url)
    linhas, se_min, se_max = conferir_csv_dengue(conteudo, geocode)
    caminho = saida / f"{geocode}.csv"
    sha = salvar(conteudo, caminho)
    colunas = list(pd.read_csv(io.BytesIO(conteudo), nrows=0).columns)
    print(f"{geocode}: {linhas} linhas, SE {se_min} a {se_max}\nsha256: {sha}\ncolunas: {colunas}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--teste", metavar="GEOCODE", help="baixa só este município, sem manifesto")
    parser.add_argument("--saida", default=None, help="pasta de saída do modo de teste")
    args = parser.parse_args()
    if args.teste:
        if not args.saida:
            sys.exit("ERRO: no modo de teste, informe --saida (fora de data/raw/).")
        download_teste(args.teste, args.saida)
    else:
        download_completo()
# [/IA]
