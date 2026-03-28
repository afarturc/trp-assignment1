# Regras de Comunicação

- Comunicar em pt-PT, termos técnicos mantêm-se em inglês
- Modo pair programming: guiar o utilizador, ele escreve o código. Pode escrever/editar ficheiros diretamente para agilizar o desenvolvimento.
- Explicar o raciocínio por trás de cada decisão para que o utilizador possa compreender e discutir
- Nunca usar o caractere "—" (em dash). Usar alternativas como ":", "-", parênteses ou reformular a frase

# Projeto: TRP Assignment 1

- Tema: Anonymization of Datasets with Privacy, Utility and Risk Analysis
- Ferramenta: ARX
- Dataset: data/original/compas-scores-raw.csv (COMPAS Recidivism -ProPublica, ~60K linhas → ~18.6K após pivotar, 28 colunas)
- Exemplo de relatório: docs/exemplos/Assignment1_MariaMatilde.pdf
- Enunciado: docs/enunciado/Assignment1-2526.pdf

# Plano de Trabalho

## Prazos
- **Entrega:** 2 de abril de 2025
- **Defesas:** 21 de abril de 2025

## Critérios de Avaliação
| Componente | Peso |
|---|---|
| Seleção e caracterização do dataset | 20% |
| Coding Model (hierarchies, configuração) | 20% |
| Privacy models: utilidade, privacidade e risk assessment | 40% |
| Defesa do assignment | 20% |

## FASE 1 -Preparação e Exploração (Python) ← FASE ATUAL
**Objetivo:** Dataset limpo e pronto para importar no ARX.

- [x] 1.1 Definir objetivo de divulgação
- [x] 1.2 Definir estatística de comparação
- [x] 1.3 Decidir colunas a manter/remover (dataset COMPAS)
- [x] 1.4 Expandir `scripts/analysis.py` -distribuições dos atributos (histogramas, min/max/média, percentis, nulls)
- [x] 1.5 Analisar resultados e decidir sanitização final
- [x] 1.6 Criar `scripts/sanitize.py` -produz CSV final (18574 linhas, 16 colunas em `data/sanitized/compas_sanitized.csv`)
- [x] 1.7 Calcular estatística do objetivo no dataset original (tabela média DecileScore_Recidivism por Ethnic_Code_Text × Sex_Code_Text)

## FASE 2 -Configuração no ARX
**Objetivo:** Importar, classificar atributos e criar hierarchies.

- [ ] 2.1 Importar CSV limpo no ARX
- [x] 2.2 Classificar atributos:
  - Identifying: `Person_ID`, `FirstName`, `LastName`, `MiddleName`, `Case_ID`, `DateOfBirth`
  - Quasi-identifying: `Age`, `Sex_Code_Text`, `Ethnic_Code_Text`, `MaritalStatus`, `LegalStatus`, `CustodyStatus`, `Language`, `Screening_Year`
  - Sensitive: `RawScore_Recidivism`, `RawScore_Violence`, `RawScore_FTA`, `DecileScore_Recidivism`, `DecileScore_Violence`, `DecileScore_FTA`, `RecSupervisionLevelText`
  - Insensitive: `Agency_Text`
- [x] 2.3 Analisar riscos do dataset original no ARX (attacker models: Prosecutor, Journalist, Marketer)
- [x] 2.4 Usar análise de distinction/separation do ARX para validar/refinar QIDs
- [x] 2.5 Criar generalization hierarchies para cada QID (ficheiros em `data/hierarchies/`)
  - `Age`: valor → 5 anos → 10 anos → 20 anos → *
  - `Ethnic_Code_Text`: valor → Black/Caucasian/Hispanic/Other Minority → *
  - `MaritalStatus`: valor → Single/In Relationship/Former/Unknown → *
  - `LegalStatus`: valor → Pretrial/Sentenced/Other → *
  - `CustodyStatus`: valor → Incarcerated/Community/Pretrial → *
  - `Sex_Code_Text`: Male/Female → *
  - `Language`: English/Spanish → *
  - `Screening_Year`: 2013/2014 → *
- [x] 2.6 Attribute weights: Ethnic_Code_Text=1.0, Age=0.8, Sex_Code_Text=0.8, MaritalStatus/LegalStatus/CustodyStatus=0.5, Language/Screening_Year=0.3
- [x] 2.7 Suppression limit=5%, coding model=generalização, utility measure=Loss

## FASE 3 -Modelos de Privacidade (ARX)
**Objetivo:** Aplicar ≥2 modelos, analisar trade-offs, encontrar bons parâmetros.

- [ ] 3.1 **Modelo 1: k-Anonymity + l-Diversity**
  - Fixar l, variar k (ex: 5, 10, 15, 20)
  - Fixar k, variar l
  - Registar: Highest Risk, Success Rate, Loss Score, Suppressed Records
- [ ] 3.2 **Modelo 2: k-Anonymity + t-Closeness**
  - Variar t (ex: 0.10 a 0.35) para vários k
  - Mesma análise
- [ ] 3.3 Para cada modelo analisar:
  - Trade-off privacidade vs. utilidade (gráficos)
  - Risco de re-identificação (3 attacker models)
  - Nível de generalização aplicado a cada atributo
- [ ] 3.4 Exportar datasets anonimizados (melhor configuração de cada modelo)

## FASE 4 -Comparação e Relatório (Python + escrita)
**Objetivo:** Avaliar utilidade e documentar tudo.

- [ ] 4.1 Criar `scripts/compare.py` -estatística objetivo no dataset anonimizado vs. original
- [ ] 4.2 Escrever relatório:
  - Justificação de todas as decisões (dataset, colunas, classificações, hierarchies)
  - Gráficos de trade-off e tabelas comparativas
  - Análise de risco de re-identificação
  - Comparação da estatística objetivo (original vs. anonimizado)
  - Recomendações finais
- [ ] 4.3 Preparar defesa

# Decisões Tomadas

- **Dataset:** COMPAS Recidivism (ProPublica) -dados de avaliação de risco de reincidência criminal, Broward County, Florida
- **Objetivo de divulgação**: Permitir a análise de possíveis disparidades raciais nos scores de risco de reincidência (COMPAS), por género e faixa etária, sem identificar os indivíduos avaliados.
- **Estatística de comparação**: Tabela com média do DecileScore_Recidivism por Ethnic_Code_Text × Sex_Code_Text (original vs. anonimizado).

## Preparação necessária (pivotar)
- O dataset original tem 3 linhas por pessoa (Risk of Violence, Risk of Recidivism, Risk of Failure to Appear)
- Pivotar para 1 linha por pessoa com 3 pares de scores (RawScore + DecileScore para cada tipo)

## Colunas a REMOVER (e porquê)
- `Person_ID`, `AssessmentID`, `Case_ID` -Identifying (IDs internos)
- `FirstName`, `LastName`, `MiddleName` -Identifying (nomes)
- `DateOfBirth` -Identifying (converter para Age antes de remover)
- `ScaleSet_ID`, `Scale_ID` -IDs internos do sistema COMPAS
- `ScaleSet` -96% "Risk and Prescreen", pouca variação
- `AssessmentReason` -só 1 valor ("Intake")
- `IsCompleted` -só 1 valor (1)
- `IsDeleted` -só 1 valor (0)
- `AssessmentType` -metadata do sistema
- `DisplayText` -usado para pivotar, removido depois
- `ScoreText` -redundante com DecileScore (Low/Medium/High derivável do score)

## Colunas a MANTER (após pivotar, classificação preliminar)
- `Age` (derivado de DateOfBirth) → Quasi-identifying
- `Sex_Code_Text` → Quasi-identifying
- `Ethnic_Code_Text` → Quasi-identifying
- `MaritalStatus` → Quasi-identifying
- `Language` → Quasi-identifying
- `LegalStatus` → Quasi-identifying
- `CustodyStatus` → Quasi-identifying
- `Screening_Year` (derivado de Screening_Date) → Quasi-identifying
- `Agency_Text` → Insensitive
- `RecSupervisionLevelText` → Sensitive
- `RawScore_Recidivism` → Sensitive
- `RawScore_Violence` → Sensitive
- `RawScore_FTA` → Sensitive
- `DecileScore_Recidivism` → Sensitive
- `DecileScore_Violence` → Sensitive
- `DecileScore_FTA` → Sensitive

## Análise de Risco do Dataset Original (baseline, antes de anonimizar)

| Attacker Model | Records at Risk | Highest Risk | Success Rate |
|---|---|---|---|
| Prosecutor | 37.24% | 100% | 28.56% |
| Journalist | 37.24% | 100% | 28.56% |
| Marketer | - | - | 28.56% |

- Risk thresholds usados: Highest risk 20%, Records at risk 5%, Success rate 5%
- Valores iguais entre Prosecutor e Journalist indicam muitos registos únicos nos QIDs

## Distinction/Separation dos QIDs

| QID | Distinction | Separation | Notas |
|---|---|---|---|
| Sex_Code_Text | 0.01% | 34.73% | Só 2 valores, separação razoável |
| MaritalStatus | 0.04% | 43.20% | Baixa distinction, separação moderada |
| Ethnic_Code_Text | 0.04% | 65.47% | Boa separação apesar de poucos valores |
| Age | 0.37% | 97.25% | QID mais discriminativo, precisa hierarchy mais profunda |

- Combinações mais discriminativas: Age+Ethnic (99.0% sep.), Age+Sex (98.2% sep.)
- Language e Screening_Year não aparecem na análise (distinction/separation negligíveis)
- Decisão: manter todos os QIDs, sem alterações
