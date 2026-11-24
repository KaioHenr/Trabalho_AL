# Notas: Etapa 1 (matéria-prima para o relatório)

> Notas preparadas com o Claude Code (ver IA_REGISTRO, entrada 4). Os números vêm dos arquivos indicados entre parênteses.

## Números principais
- 78 municípios com 574 semanas cada (SE 2015/01 a 2025/53, de 04/01/2015 a 28/12/2025); **0 lacunas, 0 duplicatas, 0 semanas sem nível** (`results/e1_auditoria.csv`).
- 573 transições válidas por município; 44.694 no ES agregado (78 × 573).
- Anos com SE 53 no período: 2020 e 2025, tratados sem regra especial porque a consecutividade é verificada pelas datas.
- Serra: semanas por nível 308 / 129 / 39 / 98. Vila Velha: 283 / 131 / 43 / 117. **Vila Velha é elegível** (≥ 5 semanas em cada nível e 573 ≥ 400 transições).
- 26 dos 78 municípios são elegíveis pelo mesmo critério (útil na Etapa 8c).
- `versao_modelo` tem 148 valores distintos, de 2023-08-20 a 2026-11-17. **É uma data de processamento, não um número de versão**: as semanas antigas foram recalculadas depois de 2023, o que mostra a revisão retroativa e justifica o congelamento.

## Verificações (`results/tabelas/e1_verificacoes.csv`, `e1_hashes.csv`)
- Soma das semanas por nível = semanas observadas: ok nos 78.
- Nenhuma transição atravessa lacuna: a contagem direta é igual à contagem por blocos (segundo caminho) nos 78. Há também os testes com série artificial com lacuna (`tests/test_etapas_1_2.py`).
- SHA-256 dos 80 arquivos = manifesto.
- Canal 2: 10 semanas sorteadas de Serra e 10 de Vila Velha (`default_rng(2026)`) em `results/tabelas/e1_canal2_sorteio.csv`. **Pendente: conferir no site.**
- Canal 3: totais anuais de Serra em `results/tabelas/e1_serra_casos_anuais.csv`. **Pendente: comparar um ano com o boletim da Sesa.**

## Pontos para a interpretação
- **2021 está vazio em todo o estado** (figura `e1_mapa_calor_nivel3mais.png`): Serra teve 8 casos notificados em 2021, contra 4.534 em 2020. Hipótese a investigar: falha ou mudança no fluxo de notificação, e não ausência de transmissão. Isso afeta a estimação (um ano inteiro em nível 1) e deve ser discutido em "modelo de um modelo" e nos limites. Os dados **não** foram alterados.
- Em 2022, Serra tem `casos` = 1.380, mas `casprov` = 122: outra inconsistência a comentar ao comparar com o boletim (definições de notificado, provável e confirmado).
- Epidemias visíveis: 2016, 2019, 2020, 2023 e 2024 (`e1_niveis_serra.png`). 2023–2024 tem nível ≥ 3 em quase todo o estado.
- Nível de alerta é uma variável construída: sai de regras do InfoDengue que combinam clima, Rt e incidência; não é contagem.
