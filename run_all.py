"""Regenera todos os resultados (results/) a partir dos dados congelados em data/raw/.

Não acessa a internet. Uso:  python run_all.py
"""

# [IA] Claude Code (claude-opus-5-5) – 2026-11-24 – script único de reprodução
import time

from src import etapa1, etapa2

ETAPAS = [etapa1, etapa2]   # as próximas etapas entram aqui, na ordem

if __name__ == "__main__":
    inicio = time.perf_counter()
    for etapa in ETAPAS:
        etapa.main()
    print(f"\nTudo regenerado em {time.perf_counter() - inicio:.1f} s")
# [/IA]
