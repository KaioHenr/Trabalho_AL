# Registro de uso de IA

Registro exigido pela Seção 10 do enunciado. Cada entrada tem uma linha correspondente no Apêndice A do relatório. No código, os trechos gerados com IA estão marcados entre `# [IA] ...` e `# [/IA]`.

**Ferramenta usada em todas as entradas:** Claude Code, modelo `claude-opus-5-5` (Anthropic), em sessões dentro do VS Code.

Em cada entrada, **Pedido** resume a solicitação em linguagem formal, e **Prompt original** reproduz o texto exatamente como foi digitado.

---

## 1. Teste de elegibilidade de Vila Velha (17/11/2026)

| Campo | Registro |
|---|---|
| **Finalidade** | Código (análise exploratória) |
| **Etapa** | Preparação da Etapa 1: escolha do 2º município |

**Pedido:** verificar se Vila Velha (3205200) atende aos critérios de elegibilidade do enunciado: pelo menos 5 semanas em cada nível e pelo menos 400 transições válidas.

**Prompt original:**
> Vila velha, consegue testar a elegibilidade dele para mim?

**O que foi produzido:** um script temporário, fora do repositório. Ele baixou a série de Vila Velha da API do InfoDengue e contou as semanas por nível e as transições válidas, considerando consecutivas as semanas cujas datas `data_iniSE` diferem em 7 dias.
- Resultado: níveis 1/2/3/4 = 283 / 131 / 43 / 117 semanas; 573 transições válidas; sem lacunas nem duplicatas. **Elegível.**

**Aceito / modificado / rejeitado:** resultado aceito como teste preliminar. A elegibilidade oficial será recalculada em `src/etapa1.py` sobre os dados congelados.

**Como foi verificado:** *a preencher pelo aluno* (ex.: conferência de algumas semanas no site do InfoDengue).

---

## 2. Estrutura do repositório, `src/markov.py` e testes da Tabela 1 (18/11/2026)

| Campo | Registro |
|---|---|
| **Finalidade** | Código |
| **Etapa** | Base matemática (Seção 6) e organização do repositório (Seção 11) |

**Pedido:** criar a estrutura de pastas do repositório e implementar as funções de cadeias de Markov (distribuição estacionária, espectro, potências, primeira passagem e cadeia absorvente), validadas contra os valores da Tabela 1 com a matriz de referência P_ref.

**Prompt original** (resposta afirmativa à proposta da IA de montar a estrutura e escrever `markov.py` com os testes da Tabela 1):
> Sim

**O que foi produzido:**
- `src/markov.py`: `is_stochastic`, `stationary_linear`, `stationary_eig`, `stationary_power`, `spectrum`, `half_life`, `min_k_positive`, `power_repeated`, `power_squaring`, `power_diag`, `first_passage_systems`, `first_passage_fundamental`, `absorbing_analysis`, `neumann_partial`.
- `tests/test_markov.py`: 21 testes (valores da Tabela 1, concordância entre métodos, Kac, `B1 = 1`, traço e determinante, série de Neumann).
- `README.md`, `requirements.txt`, `.gitignore`, `pytest.ini` e estrutura de pastas.

**Aceito / modificado / rejeitado:** *a preencher pelo aluno após revisão.*
- Observação: o teste da série de Neumann foi ajustado de K = 1000 para K = 2000. O raio espectral de Q (≈ 0,9766) torna a convergência lenta.

**Como foi verificado:** `pytest` com 21 testes passando; todos os valores da Tabela 1 reproduzidos com erro menor que 1e-6.

---

## 3. Script de download e manifesto (23/11/2026)

| Campo | Registro |
|---|---|
| **Finalidade** | Código |
| **Etapa** | Aquisição e congelamento dos dados (Seção 5) |

**Pedido:** implementar o download único dos dados do InfoDengue para os 78 municípios do ES, com geração de manifesto contendo URL, número de linhas, data/hora e hash SHA-256 de cada arquivo.

**Prompt original** (concordando com a proposta da IA de escrever `src/download.py` com manifesto SHA-256):
> Sim vamos fazer como vc esta sugerindo então

**O que foi produzido:**
- `src/download.py`:
  - download único dos 78 municípios (InfoDengue), da lista de municípios e da população do Censo 2022 (IBGE/SIDRA, tabela 4709);
  - arquivos salvos com os bytes originais da API;
  - geração de `data/MANIFEST.txt` (URL, linhas, SHA-256, data/hora UTC);
  - bloqueio contra um segundo download;
  - modo `--teste`, que grava fora de `data/raw/`.
- `tests/test_download.py`: hash SHA-256 de valor conhecido e leitura do manifesto.

**Aceito / modificado / rejeitado:** *a preencher pelo aluno após revisão.*

**Como foi verificado:** modo de teste com Serra (574 linhas, SE 201501 a 202553, colunas `data_iniSE`, `SE`, `nivel` e `versao_modelo` presentes); `pytest` passando.

---

## 4. Etapas 1 e 2 (24/11/2026)

| Campo | Registro |
|---|---|
| **Finalidade** | Código e preparação de notas para o relatório |
| **Etapa** | Etapa 1 (auditoria dos dados) e Etapa 2 (estimação de P̂) |

**Pedido:** implementar completamente a Etapa 1 e a Etapa 2, a partir do esqueleto de funções de `src/etapa1.py` escrito pelo aluno, para permitir o commit do dia.

**Prompt original:**
> faça a etapa 1 e a etapa 2 para fazer o commit e o push hj pfvr

**O que foi produzido:**
- `src/etapa1.py`: o aluno definiu a estrutura de funções (`ler_serie`, `auditar`, `conferir_hashes`, `auditar_todos`, `sortear_semanas_conferencia`, `grafico_niveis_serra`, `mapa_calor_municipio_ano`, `main`). A IA implementou essas funções e acrescentou `remover_duplicatas`, `transicoes`, `contar_transicoes_por_blocos`, `verificar_auditoria`, `resumir_conferencia_canal2` e `casos_anuais_serra`.
- `src/etapa2.py`: matriz de contagens (laço e `crosstab`), P̂ por máxima verossimilhança, erros-padrão, Laplace (α = 0,5), π e ‖π − π^(α)‖₁, mapas de calor.
- `run_all.py`: executa as etapas em sequência.
- `tests/test_etapas_1_2.py`: 5 testes com séries artificiais (lacuna, nível ausente, duplicata, contagens por dois caminhos, estimadores estocásticos).
- `relatorio/notas/etapa1.md` e `etapa2.md`: resumo dos números e pontos de interpretação.

**Aceito / modificado / rejeitado:** *a preencher pelo aluno após revisão.*

**Como foi verificado:** `python run_all.py` sem erros (≈ 11 s); verificações salvas em `results/tabelas/e1_verificacoes.csv` e `e2_verificacoes.csv`, todas ok; hashes conferem com o manifesto; `pytest` com 28 testes passando.
