# Notas: Etapa 5 (matéria-prima para o relatório)

> Notas preparadas com o Claude Code (ver IA_REGISTRO, entrada 6). Os números vêm dos arquivos indicados entre parênteses.

## Números principais
**Permanência no vermelho (nível 4)** (`results/tabelas/e5_permanencia.csv`):
| Série | p̂₄₄ | Média modelo 1/(1−p̂₄₄) | Média observada | Mediana modelo | Mediana observada | Corridas completas |
|---|---|---|---|---|---|---|
| Serra | 0,918 | 12,25 | 12,25 | 9 | 12,5 | 8 |
| Vila Velha | 0,906 | 10,64 | 10,64 | 8 | 7 | 11 |
| ES | 0,893 | 9,32 | 9,32 | 7 | 6 | 566 |

**Primeira passagem** (`e5_M_*.csv`, `e5_primeira_passagem.csv`):
| Série | m₁₄ modelo | 1→4 empírico (média) | m₄₁ modelo | 4→1 empírico (média) |
|---|---|---|---|---|
| Serra | 60,8 | 65,4 (245 partidas, 63 censuradas) | 14,2 | 11,1 |
| Vila Velha | 45,3 | 55,1 (229; 54 censuradas) | 15,3 | 11,6 |
| ES | 73,9 | 106,7 (30.882; 3.787 censuradas) | 11,4 | 11,1 |

## Verificações (`results/tabelas/e5_verificacoes.csv`, 6 de 6 ok)
- Kac, mⱼⱼ = 1/πⱼ: erro máximo 1,6e-14 a 2,8e-14 (< 1e-10).
- M por 4 sistemas 3×3 = M pela matriz fundamental Z: diferença máxima de até 1,7e-13.
- m₁₄ e m₄₁ da Tabela 1 reproduzidos (`tests/test_etapa5.py`).

## Pontos para a interpretação
- **A média observada das corridas igual a 1/(1−p̂ᵢᵢ) não confirma nada:** é uma identidade do estimador. p̂ᵢᵢ = nᵢᵢ/nᵢ é calculado com as mesmas corridas, e para corridas completas 1/(1−p̂ᵢᵢ) = (soma das durações)/(nº de corridas). As médias só diferem quando há corridas censuradas (ex.: Serra nível 2, cuja série começa e termina no amarelo; ES nível 1). **O teste da hipótese geométrica é a forma da distribuição.**
- **Achado forte, o vermelho "dura pelo menos 2 semanas":** no ES, só 4,1% das corridas completas no nível 4 duram 1 semana (a geométrica prevê 10,7%), e 23,5% duram exatamente 2 semanas (previsto: 9,6%) (`e5_duracoes_nivel4.csv`, figura `e5_duracoes_nivel4.png`). Com 566 corridas, isso não é acaso. A probabilidade de sair do vermelho depende de há quanto tempo se está nele, ou seja, há **memória além de uma semana**, o que contraria a hipótese de Markov de 1ª ordem. Provável causa: as regras do InfoDengue exigem semanas consecutivas para mudar de nível. A Etapa 8(b), com a cadeia de 2ª ordem, testa isso formalmente.
- Nível 3: o desvio-padrão observado é bem menor que o do modelo (ES 0,98 contra 1,86; Serra 1,66 contra 2,70). O laranja é uma passagem curta e regular, menos variável que uma geométrica.
- Serra e Vila Velha têm poucas corridas no vermelho (8 e 11): o histograma é ruidoso e não permite conclusão isolada. O ES dá a evidência estatística.
- **Primeira passagem empírica 1→4 é maior que m₁₄** (Vila Velha 55 contra 45; ES 107 contra 74), mesmo excluindo as censuradas, que puxariam a média ainda mais para cima. O modelo homogêneo **subestima** o tempo até o vermelho; os períodos calmos reais são mais longos (ex.: 2017–2018, 2021–2022) do que uma cadeia homogênea prevê. Para 4→1 o modelo e os dados ficam próximos (ES 11,4 contra 11,1).
- Significado prático de m₁₄: em Serra, saindo do verde, o modelo prevê em média ~61 semanas (pouco mais de 1 ano) até o primeiro vermelho. Isso dá a escala de tempo das ações preventivas entre epidemias, mas com a ressalva acima: é uma média sobre anos muito diferentes.
