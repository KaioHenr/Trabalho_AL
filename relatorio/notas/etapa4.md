# Notas: Etapa 4 (matéria-prima para o relatório)

> Notas preparadas com o Claude Code (ver IA_REGISTRO, entrada 5). Os números vêm dos arquivos indicados entre parênteses.

## Números principais (`results/tabelas/e4_espectro.csv`, `e4_resumo.csv`)
| Série | Espectro | \|λ₂\| | Meia-vida (semanas) | κ₁(V) |
|---|---|---|---|---|
| Serra | 1; **0,8791 ± 0,0229i**; 0,6488 | 0,8794 | 5,39 | 6,08 |
| Vila Velha | 1; 0,8811; 0,7922; 0,5949 | 0,8811 | 5,47 | 4,50 |
| ES | 1; 0,8858; 0,7587; 0,5740 | 0,8858 | 5,72 | 6,40 |

- P̂⁵² por quadrados sucessivos contra diagonalização: ‖diferença‖₁ = 6,6e-15 (Serra), 6,3e-15 (Vila Velha), 1,3e-13 (ES). Contra multiplicação repetida: ~1e-15.
- Distância a π após um ano (n = 52), partindo do verde: 0,0021 (Serra), 0,0012 (Vila Velha), 0,0006 (ES). Partindo do vermelho: 0,0028, 0,0022, 0,0031.

## Verificações (`results/tabelas/e4_verificacoes.csv`, 12 de 12 ok)
- Soma dos autovalores = traço e produto = determinante, com tolerância 1e-10.
- P̂⁵² pelos dois caminhos concordam (< 1e-10). λ₁ = 1.

## Pontos para a interpretação
- **"Memória epidemiológica" de cerca de 5,5 semanas:** a cada ~5,5 semanas, a influência do nível atual sobre a previsão cai pela metade. Em ~4 meias-vidas (≈ 22 semanas) restam ~6%; depois de um ano, o nível atual quase não informa mais (distâncias ≈ 0,001–0,003).
- Serra, Vila Velha e ES têm memória muito parecida (5,4 a 5,7 semanas), apesar de π bem diferentes. A velocidade de "esquecer" é semelhante; o lugar para onde a cadeia vai (π) é que muda.
- **Serra tem um par de autovalores complexos** (0,8791 ± 0,0229i). A parte imaginária é pequena: a convergência ganha uma oscilação muito lenta (período 2π/arg(λ) ≈ 241 semanas), praticamente invisível no gráfico. Como |λ₂| = |λ₃|, as duas componentes decaem juntas. A diagonalização continua válida, com V complexa; a parte imaginária de P̂⁵² se cancela (erro ~1e-15).
- κ₁(V) entre 4,5 e 6,4: V é bem condicionada, a diagonalização numérica é confiável, e a concordância de 1e-13 a 1e-15 com os quadrados sucessivos confirma isso. κ₁(V) alto (autovetores quase paralelos, perto de uma matriz não diagonalizável) amplificaria os erros de arredondamento em V Λⁿ V⁻¹.
- Gráfico `e4_convergencia.png`: as curvas são paralelas à reta C|λ₂|ⁿ em escala log, como prevê a Proposição 3. Ligação com a Etapa 7: em h = 8 (≈ 1,5 meia-vida) a previsão ainda carrega ~35% da informação do estado atual.
