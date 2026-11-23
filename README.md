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
python run_all.py      # regenera todos os resultados a partir de data/raw/, sem internet (em construção)
```

Tempo aproximado de execução de `run_all.py`: *a medir.*

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
| *a preencher conforme as etapas forem concluídas* | | |

## Uso de IA

Declarado em [`IA_REGISTRO.md`](IA_REGISTRO.md) e no Apêndice A do relatório. No código, trechos gerados com IA estão entre `# [IA] ...` e `# [/IA]`.
