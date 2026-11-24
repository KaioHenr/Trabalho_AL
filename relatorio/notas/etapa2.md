# Notas: Etapa 2 (matéria-prima para o relatório)

> Notas preparadas com o Claude Code (ver IA_REGISTRO, entrada 4). Os números vêm dos arquivos indicados entre parênteses.

## Números principais (`results/tabelas/e2_P_*.csv`, `e2_C_*.csv`, `e2_EP_*.csv`)
- Diagonais de P̂ (probabilidade de permanecer no nível):
  - Serra: 0,945 / 0,852 / 0,692 / 0,918
  - Vila Velha: 0,919 / 0,792 / 0,651 / 0,906
  - ES: 0,967 / 0,771 / 0,587 / 0,893
- O nível 3 é o mais "instável" nas três séries; os níveis 1 e 4 são os mais persistentes.
- Distribuição estacionária π de P̂ (`e2_pi_laplace.csv`):
  - Serra: (0,5375; 0,2234; 0,0681; 0,1710)
  - Vila Velha: (0,4939; 0,2269; 0,0750; 0,2042)
  - ES: (0,7741; 0,0976; 0,0103; 0,1181)
- Efeito de Laplace (α = 0,5) em π, medido por ‖π − π^(α)‖₁: Serra 0,0079; Vila Velha 0,0067; ES 0,0002.

## Verificações (`results/tabelas/e2_verificacoes.csv`, 12 de 12 ok)
- P̂ ≥ 0 e P̂·1 = 1 (tol 1e-12), também para a versão de Laplace.
- Soma de C = transições válidas da Etapa 1 (573, 573 e 44.694).
- C contada por dois caminhos independentes (laço explícito e `pandas.crosstab`): idênticas.

## Pontos para a interpretação
- **A transição 4 → 3 nunca ocorre** (0 em Serra, Vila Velha e ES, mesmo com 5.276 saídas do nível 4 no ES). O alerta vermelho cai direto para 1 ou 2. É um zero "estrutural" que vem das regras do InfoDengue, não de falta de dados. Bom ponto para a Etapa 8 e para "modelo de um modelo".
- Saltos grandes existem: 1 → 4 aparece (1 vez em Serra e em Vila Velha; 245 no ES), ao contrário da matriz fictícia P_ref, que tinha zero ali.
- Assimetria: subir de 3 para 4 é mais provável que descer de 3 para 2 em Serra (0,154 contra 0,128) e no ES (0,177 contra 0,127); em Vila Velha é o contrário (0,070 contra 0,163).
- Laplace: com dezenas ou milhares de transições por linha, o efeito em π é pequeno. Mas a suavização **inventa** a transição 4 → 3, que os dados mostram ser estruturalmente impossível. Aqui ela não é defensável para essa entrada.
- O ES agregado passa muito mais tempo no nível 1 (π₁ = 0,77) que Serra e Vila Velha, porque soma muitos municípios pequenos que quase nunca saem do verde. A hipótese de "dinâmica comum" será examinada na Etapa 8.
