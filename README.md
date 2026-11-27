# Vigilância em estados: cadeias de Markov e alertas de dengue no Espírito Santo

Trabalho prático de Álgebra Linear, Tema A, IFES Serra, 2026/2.

## Integrante

| Nome | Matrícula |
|---|---|
| Kaio Henrique Arantes André Nheri | 20221bsi0021 |

Modalidade: **individual**.

## Objetivo

Estimar matrizes de transição dos níveis de alerta semanais do InfoDengue (2015–2025) e usar Álgebra Linear para descrever a dinâmica dos alertas: distribuição estacionária, espectro, tempos de primeira passagem, cadeias absorventes, previsão e testes de hipótese.

## Municípios

- **Serra** (3205002): município comum a todas as equipes.
- **Vila Velha** (3205200): município escolhido. *Justificativa: a completar.*
- **ES agregado**: soma das matrizes de contagens dos 78 municípios.

## Ambiente

- Python 3.14.7. O enunciado exige Python 3.10 ou mais novo.
- As dependências estão com versão fixada em `requirements.txt`.

```bash
pip install -r requirements.txt
pytest                 # testes (Tabela 1 do enunciado e propriedades)
python run_all.py      # regenera todos os resultados a partir de data/raw/, sem internet
```

Tempo aproximado de execução de `run_all.py`: cerca de 12 s com as Etapas 1 a 5.

## Organização

```
data/raw/        dados congelados do InfoDengue (somente leitura)
data/MANIFEST.txt  SHA-256, URL, data/hora e nº de linhas de cada arquivo
src/markov.py    funções genéricas de cadeias de Markov
src/etapaN.py    um script por etapa (carrega dados, chama markov.py, salva resultados)
tests/           testes pytest
results/         tabelas (CSV) e figuras geradas
relatorio/       fonte e PDF do relatório
```

## Figuras e tabelas do relatório → arquivo que as gera

| Item do relatório | Arquivo gerado | Script |
|---|---|---|
| Auditoria dos 78 municípios (E1) | `results/e1_auditoria.csv` | `src/etapa1.py` |
| Verificações e hashes (E1) | `results/tabelas/e1_verificacoes.csv`, `e1_hashes.csv` | `src/etapa1.py` |
| Semanas sorteadas para o Canal 2 (E1) | `results/tabelas/e1_canal2_sorteio.csv` | `src/etapa1.py` |
| Casos anuais de Serra para o Canal 3 (E1) | `results/tabelas/e1_serra_casos_anuais.csv` | `src/etapa1.py` |
| Níveis de Serra no tempo (E1) | `results/figuras/e1_niveis_serra.png` | `src/etapa1.py` |
| Mapa de calor município × ano (E1) | `results/figuras/e1_mapa_calor_nivel3mais.png` | `src/etapa1.py` |
| Matrizes C, P̂, erros-padrão e Laplace (E2) | `results/tabelas/e2_C_*.csv`, `e2_P_*.csv`, `e2_EP_*.csv`, `e2_P_laplace_*.csv` | `src/etapa2.py` |
| π e efeito de Laplace (E2) | `results/tabelas/e2_pi_laplace.csv` | `src/etapa2.py` |
| Mapas de calor de P̂ (E2) | `results/figuras/e2_mapas_P.png` | `src/etapa2.py` |
| π por três métodos e iterações (E3) | `results/tabelas/e3_pi_metodos.csv`, `e3_resumo.csv` | `src/etapa3.py` |
| π contra frequência empírica (E3) | `results/tabelas/e3_pi_vs_empirico.csv` | `src/etapa3.py` |
| Espectro, meia-vida, κ₁(V) (E4) | `results/tabelas/e4_espectro.csv`, `e4_resumo.csv` | `src/etapa4.py` |
| P̂⁵² (E4) | `results/tabelas/e4_P52_*.csv` | `src/etapa4.py` |
| Convergência para π, escala log (E4) | `results/figuras/e4_convergencia.png`, `results/tabelas/e4_convergencia_*.csv` | `src/etapa4.py` |
| Permanência modelo × observada (E5) | `results/tabelas/e5_permanencia.csv` | `src/etapa5.py` |
| Durações no nível 4 × geométrica (E5) | `results/figuras/e5_duracoes_nivel4.png`, `results/tabelas/e5_duracoes_nivel4.csv` | `src/etapa5.py` |
| Matriz M de primeira passagem (E5) | `results/tabelas/e5_M_*.csv` | `src/etapa5.py` |
| Primeira passagem empírica 1→4 e 4→1 (E5) | `results/tabelas/e5_primeira_passagem.csv` | `src/etapa5.py` |

## Uso de IA

Declarado em [`IA_REGISTRO.md`](IA_REGISTRO.md) e no Apêndice A do relatório. No código, trechos gerados com IA estão entre `# [IA] ...` e `# [/IA]`.
