# Notas: Etapa 6 (matéria-prima para o relatório)

> Notas preparadas com o Claude Code (ver IA_REGISTRO, entrada 7). Os números vêm dos arquivos indicados entre parênteses.

## Números principais
**(a) Tempo até o primeiro vermelho** (nível 4 absorvente) (`results/tabelas/e6_tempo_ate_vermelho.csv`):
| Série | Saindo de 1 | Saindo de 2 | Saindo de 3 |
|---|---|---|---|
| Serra | 60,8 ± 54,4 | 49,2 ± 52,6 | 28,8 ± 45,5 |
| Vila Velha | 45,3 ± 41,0 | 34,7 ± 39,4 | 34,2 ± 39,5 |
| ES | 73,9 ± 71,4 | 57,1 ± 68,9 | 39,5 ± 62,3 |
(média ± desvio-padrão, em semanas)

**(b) e (c) Do amarelo, chega-se ao vermelho antes de voltar ao verde?** (`e6_B_absorcao.csv`, `e6_episodios_empiricos.csv`)
| Série | B (modelo), de 2 → 4 | Episódios | Terminados em 4 | Proporção | IC 95% (exato) |
|---|---|---|---|---|---|
| Serra | 0,361 | 12 | 4 | 0,333 | [0,099; 0,651] |
| Vila Velha | 0,386 | 15 | 7 | 0,467 | [0,213; 0,734] |
| ES | 0,293 | 783 | 208 | 0,266 | [0,235; 0,298] |

Saindo do laranja (nível 3), a probabilidade de chegar ao vermelho antes do verde é 0,650 (Serra), 0,380 (Vila Velha) e 0,518 (ES).

## Verificações (`results/tabelas/e6_verificacoes.csv`, 18 de 18 ok)
- B·1 = 1 (erro ≤ 2,2e-16).
- t = N·1 igual a resolver (I − Q)t = 1 diretamente (segundo caminho; erro ≤ 2,8e-14).
- N pela inversa = soma de Neumann com K = 5000, nos dois cenários (erro ≤ 2e-13).
- t saindo de 1 = m₁₄ da Etapa 5 (o mesmo número por dois métodos diferentes).
- Valores de t, variância e B da Tabela 1 reproduzidos (`tests/test_markov.py`, `tests/test_etapas_6_7.py`).

## Pontos para a interpretação
- **Coerência entre modelo e dados:** nas três séries, B está dentro do IC de 95% da proporção empírica. No ES, com 783 episódios, o IC é estreito (±0,03) e ainda contém o modelo: essa é a conclusão estatisticamente mais forte. Em Serra e Vila Velha, com 12 e 15 episódios, os ICs são largos demais para distinguir qualquer coisa.
- **Uso pelo gestor:** "quando o alerta sobe do verde para o amarelo, em cerca de 1 a cada 3 vezes (Serra: 36%) chega ao vermelho antes de voltar ao verde". É um número de priorização (quanto investir na resposta ao amarelo), não uma previsão para o episódio atual: não usa casos, clima nem a época do ano. A Etapa 8 mostra que a sazonalidade importa.
- **Desvios-padrão do tamanho da média** (Serra: 61 ± 54 semanas): é típico de tempos de absorção quase geométricos. O tempo até o vermelho é muito imprevisível; a média sozinha engana.
- **Série de Neumann (d), figura `e6_neumann.png`:** a velocidade depende do raio espectral de Q. Com só o 4 absorvente, ρ(Q) ≈ 0,976–0,986 e são precisos ~2000 termos. Com 1 e 4 absorventes, ρ(Q) ≈ 0,79–0,90 e bastam ~200 a 500. Ligação com a Proposição 4: ‖Qᵐ‖ < 1 garante a convergência, mas não que ela seja rápida. N = Σ Qᵏ interpretada como número esperado de visitas: N[1,1] grande significa muitas semanas no verde antes do primeiro vermelho.
