# Regras de Comunicação

- Comunicar em pt-PT, termos técnicos mantêm-se em inglês
- Modo pair programming: guiar o utilizador, ele escreve o código. Pode escrever/editar ficheiros diretamente para agilizar o desenvolvimento.
- Explicar o raciocínio por trás de cada decisão para que o utilizador possa compreender e discutir

# Projeto: TRP Assignment 1

- Tema: Anonymization of Datasets with Privacy, Utility and Risk Analysis
- Ferramenta: ARX
- Dataset: data/original/reviews.csv (Steam reviews, ~4M linhas, 23 colunas)
- Exemplo de relatório: docs/exemplos/Assignment1_MariaMatilde.pdf
- Enunciado: docs/enunciado/Assignment1-2526.pdf

# Objetivos do Projeto
## Step 1 — Preparar o dataset e definir um objetivo
- Sanitizar o dataset (limpar, escolher colunas relevantes)
- Definir um objetivo de divulgação do dataset anonimizado
- Definir estatísticas sobre o objetivo para comparar dataset original vs. anonimizado

## Step 2 — Classificar atributos e configurar o modelo (ARX)
- Classificar cada coluna como: Identifying, Quasi-identifying, Sensitive ou Insensitive
- Criar hierarchies de generalização para os quasi-identifiers
- Definir attribute weights e coding model

## Step 3 — Aplicar modelos de privacidade e analisar (ARX)
- Aplicar pelo menos 2 modelos de privacidade (ex: k-Anonymity + l-Diversity, k-Anonymity + t-Closeness)
- Analisar trade-off entre privacidade e utilidade
- Iterar parâmetros até encontrar bom equilíbrio
- Análise de risco de re-identificação

## Step 4 — Relatório
- Documentar todas as decisões e raciocínios
- Comparar estatísticas do objetivo no dataset original vs. anonimizado
- Recomendações sobre o processo de anonimização

# Progresso Atual

## Decisões tomadas
- **Objetivo de divulgação**: Analisar como a experiência do utilizador (nº jogos, horas jogadas, nº reviews) influencia o sentimento dos reviews (positivo/negativo), por idioma, sem identificar utilizadores.
- **Estatística de comparação**: Tabela com média de playtime e games_owned por idioma e sentimento (original vs. anonimizado).

## Colunas a REMOVER (e porquê)
- `steam_purchase` — só 1 valor (todos True)
- `created_at`, `updated_at` — 1 valor único cada, metadata da extração
- `review_text` — texto livre, quase identifying, ARX não lida bem
- `timestamp_updated` — redundante com timestamp_created
- `author_playtime_at_review` — ~26% nulls
- `author_playtime_last_two_weeks` — maioria 0, pouca utilidade

## Colunas a MANTER (classificação preliminar)
- `author_steamid` → Identifying
- `appid` → Quasi-identifying
- `author_num_games_owned` → Quasi-identifying
- `author_num_reviews` → Quasi-identifying
- `author_playtime_forever` → Quasi-identifying
- `language` → Quasi-identifying
- `timestamp_created` → Quasi-identifying (converter para ano)
- `author_last_played` → Quasi-identifying (converter para ano, a discutir)
- `voted_up` → Sensitive
- `votes_up` → Insensitive
- `votes_funny` → Insensitive
- `comment_count` → Insensitive
- `received_for_free` → Insensitive
- `written_during_early_access` → Insensitive

## Próximo passo
- Correr análise de distribuições dos atributos a manter (código em scripts/analysis.py)
- Analisar resultados para decidir sanitização final e tamanho da amostra
