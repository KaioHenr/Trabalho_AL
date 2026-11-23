"""Testes das funções auxiliares de src/download.py (sem acesso à internet)."""

from src import download as dl


# [IA] Claude Code (claude-opus-5-5) – 2026-11-23 – teste do hash SHA-256 e leitura do manifesto
def test_sha256_valor_conhecido(tmp_path):
    arquivo = tmp_path / "abc.txt"
    arquivo.write_bytes(b"abc")
    # valor oficial do SHA-256 de "abc" (exemplo do padrão FIPS 180-2)
    assert dl.sha256_arquivo(arquivo) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_ler_manifesto_ignora_metadados(tmp_path):
    manifesto = tmp_path / "MANIFEST.txt"
    manifesto.write_text("# inicio_download_utc: x\narquivo,url,linhas,sha256\n"
                         "3205002.csv,http://exemplo,574,abc123\n", encoding="utf-8")
    df = dl.ler_manifesto(manifesto)
    assert list(df.columns) == ["arquivo", "url", "linhas", "sha256"]
    assert df.loc[0, "linhas"] == 574
# [/IA]
