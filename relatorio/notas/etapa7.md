# Notas: Etapa 7 (matéria-prima para o relatório)

> Notas preparadas com o Claude Code (ver IA_REGISTRO, entrada 7). Os números vêm dos arquivos indicados entre parênteses.

## Números principais (`results/tabelas/e7_pontuacoes.csv`; menor = melhor)
**Brier multicategoria**
| Série | h | Markov | Persistência | Climatologia |
|---|---|---|---|---|
| Serra | 1 | **0,167** | 0,179 | 0,679 |
| Serra | 4 | **0,382** | 0,536 | 0,667 |
| Serra | 8 | **0,526** | 0,886 | 0,656 |
| Vila Velha | 1 | **0,227** | 0,256 | 0,751 |
| Vila Velha | 4 | **0,467** | 0,641 | 0,741 |
| Vila Velha | 8 | **0,619** | 0,913 | 0,734 |

**Logarítmica**
| Série | h | Markov | Persistência | Climatologia |
|---|---|---|---|---|
| Serra | 1 | **0,438** | 1,240 | 1,308 |
| Serra | 4 | **0,733** | 3,702 | 1,274 |
| Serra | 8 | **0,990** | 6,120 | 1,258 |
| Vila Velha | 1 | **0,493** | 1,771 | 1,393 |
| Vila Velha | 4 | **0,914** | 4,425 | 1,366 |
| Vila Velha | 8 | **1,138** | 6,305 | 1,356 |

T = 156, 153 e 149 semanas de teste para h = 1, 4 e 8.

## Verificações (`results/tabelas/e7_verificacoes.csv`, 26 de 26 ok)
- Todas as previsões somam 1 (erro < 1e-12), nos 3 métodos e 3 horizontes.
- Nenhuma informação do teste no treino: a última semana usada na estimação é 25/12/2022.
- P_treinoʰ por quadrados sucessivos = por diagonalização (erro ≤ 1,4e-15).

## Pontos para a interpretação
- **A cadeia supera as duas referências em todos os horizontes**, nas duas pontuações, nos dois municípios.
- **A vantagem cai com o horizonte, como prevê a meia-vida (Etapa 4, ~5,4 semanas).** Ganho de Brier sobre a climatologia em Serra: 75% em h = 1, 43% em h = 4 e 20% em h = 8. Com h = 8 (≈ 1,5 meia-vida), resta ~36% da informação do estado atual, e a previsão já se aproxima de π.
- **Persistência:** em h = 1 o Brier é quase igual ao da cadeia (0,179 contra 0,167), porque os níveis mudam pouco de uma semana para outra. Mas a pontuação log é péssima (1,24 contra 0,44): a persistência dá probabilidade 0 a qualquer mudança, e cada mudança custa −ln(1e-6) ≈ 13,8. **Uma previsão "certeza absoluta" é punida quando erra.**
- **Climatologia é ruim porque o teste é atípico:** π_treino vem de 2015–2022 (com 2021 vazio e muito verde), e o teste inclui as epidemias de 2023 e 2024. É a falha da hipótese de homogeneidade no tempo.
- **2024 (`e7_previsao_2024.png`):** a cadeia **não antecipa** a epidemia. A probabilidade prevista de vermelho com h = 4 só sobe (~0,4, depois ~0,65) depois que o alerta já está em 3 ou 4, e continua alta ~4 semanas depois do fim do vermelho. A previsão é o nível de 4 semanas atrás "suavizado" por P⁴: reage, não antecipa. Para o gestor, a cadeia é útil para dizer "dado que estamos em laranja, a chance de vermelho em 1 mês é X", mas não substitui indicadores antecedentes (clima, Rt, casos).
- Nunca há p(4) próximo de 1: o máximo é ~0,65 (Serra) e ~0,56 (Vila Velha), igual a (P⁴)₄₄ de treino. É o teto que a cadeia homogênea consegue dar.
