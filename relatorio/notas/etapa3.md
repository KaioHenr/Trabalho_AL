# Notas: Etapa 3 (matéria-prima para o relatório)

> Notas preparadas com o Claude Code (ver IA_REGISTRO, entrada 5). Os números vêm dos arquivos indicados entre parênteses.

## Números principais
- π (`results/tabelas/e3_pi_vs_empirico.csv`):
  - Serra: (0,5375; 0,2234; 0,0681; 0,1710)
  - Vila Velha: (0,4939; 0,2269; 0,0750; 0,2042)
  - ES: (0,7741; 0,0976; 0,0103; 0,1181)
- Em longo prazo, Serra passa cerca de **17%** das semanas em vermelho, Vila Velha **20%** e o ES agregado **12%**.
- Método das potências (`e3_resumo.csv`): 195 a 216 iterações para atingir ‖π^(k+1) − π^(k)‖₁ < 1e-12. A previsão ln(1e-12)/ln|λ₂| dá 215 (Serra), 218 (Vila Velha) e 228 (ES), coerente com o observado.
- Menor k com P̂ᵏ > 0: **k = 2** nas três séries; o limite de Wielandt para n = 4 é (4 − 1)² + 1 = 10. Logo, as três matrizes são primitivas, embora P̂ tenha um zero (4 → 3).

## Verificações (`results/tabelas/e3_verificacoes.csv`, 12 de 12 ok)
- Maior discrepância L1 entre os 5 cálculos de π (linear, potências a partir de e1, e4 e uniforme, autovetor): 1,3e-11 a 1,5e-11 (< 1e-10).
- Resíduo ‖πP̂ − π‖₁ entre 0 e 6e-17.
- Os valores da Tabela 1 são reproduzidos pelos mesmos métodos em `tests/test_etapas_3_4.py`.

## Pontos para a interpretação
- π e a frequência empírica quase coincidem (‖π − freq‖₁ = 0,0027 em Serra e em Vila Velha; 0,0005 no ES). **Isso não prova que a série é estacionária.** Com P̂ estimada da própria série, π fica perto das frequências observadas quase por construção: em uma trajetória, o número de entradas em cada nível difere do número de saídas em no máximo 1. A pergunta do enunciado ("por que não precisam coincidir") se responde assim: π descreve o equilíbrio de uma cadeia **homogênea**, enquanto a série real tem anos epidêmicos e anos calmos (e 2021 vazio). Essa coincidência é uma propriedade do estimador, não um teste da hipótese.
- As iterações acompanham |λ₂|: como o erro cai como |λ₂|ᵏ, o ES (|λ₂| = 0,886) precisa de mais iterações que Serra (0,879).
- Primitividade em k = 2: mesmo sem o salto 4 → 3 direto, o caminho 4 → 4 → 3 não existe, mas 4 → 2 → 3 existe. Ou seja, em duas semanas qualquer nível é atingível a partir de qualquer outro.
