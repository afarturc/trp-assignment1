# Estrutura do Relatório

## 1. Seleção, Importação e Objetivo do Dataset

### 1.1 Dataset Escolhido
- COMPAS Recidivism Risk Score Data (ProPublica, Broward County, Florida)
- Dataset original: ~60K linhas, 28 colunas (3 linhas por pessoa)
- Dataset final após sanitização: 18.574 registos, 16 colunas
- Disponível em: Kaggle / ProPublica GitHub

### 1.2 Distribuição do Dataset
- Distribuições dos QIDs (gráficos em results/exploratory/)
- Estatísticas descritivas dos atributos sensíveis (DecileScores, RawScores)
- Referência para Anexos (plots completos)

### 1.3 Sanitização
- Problema: 3 linhas por pessoa (Risk of Recidivism, Violence, FTA) -> pivotar para 1
- Remoção de avaliações inválidas (DecileScore=-1)
- Manter apenas a avaliação mais recente por pessoa
- Derivar Age a partir de DateOfBirth e Screening_Date
- Derivar Screening_Year a partir de Screening_Date
- Fusão de etnias: African-Am -> African-American, Oriental -> Asian
- Remoção de colunas: identifying (nomes, IDs), redundantes (ScoreText, ScaleSet, etc.)

### 1.4 Objetivo de Divulgação
- Permitir a análise de possíveis disparidades raciais nos scores de risco de reincidência
  (COMPAS), por género, sem identificar os indivíduos avaliados.
- Contexto: ProPublica demonstrou em 2016 que o COMPAS atribui scores mais altos a
  African-Americans do que a Caucasians com perfis semelhantes.

### 1.5 Estatística de Comparação
- Tabela: média do DecileScore_Recidivism por Ethnic_Code_Text x Sex_Code_Text
- Calculada no dataset original (results/arx/objetivo_original.csv)
- Será comparada com os datasets anonimizados via MAE

### 1.6 Requisitos de Privacidade
- Suppression limit: 5%
- Coding model: generalização (preferência sobre supressão)
- Utility measure: Granularity (Loss no ARX)
- Pesos dos atributos:
  - Ethnic_Code_Text: 1.0 (mais relevante para o objetivo)
  - Age: 0.8
  - Sex_Code_Text: 0.8
  - MaritalStatus, LegalStatus, CustodyStatus: 0.5
  - Language, Screening_Year: 0.3
- Modelos selecionados: k-Anonymity + l-Diversity e k-Anonymity + t-Closeness

---

## 2. Caracterização do Dataset e Coding Models

### 2.1 Caracterização de Atributos
Tabela com classificação e justificação de cada atributo:

| Atributo | Tipo | Justificação |
|---|---|---|
| Person_ID, FirstName, LastName, MiddleName, Case_ID, DateOfBirth | Identifying | Identificam diretamente o indivíduo |
| Age, Sex_Code_Text, Ethnic_Code_Text, MaritalStatus, Language, LegalStatus, CustodyStatus, Screening_Year | Quasi-identifying | Combinação pode re-identificar |
| RecSupervisionLevelText, DecileScore_*, RawScore_* | Sensitive | Scores de risco COMPAS - informação privada e potencialmente discriminatória |
| Agency_Text | Insensitive | Agência pública, não associada ao indivíduo |

### 2.2 Riscos de Privacidade do Dataset Original (baseline)

| Attacker Model | Highest Risk | Records at Risk | Success Rate |
|---|---|---|---|
| Prosecutor | 100% | 37.24% | 28.56% |
| Journalist | 100% | 37.24% | 28.56% |
| Marketer | - | - | 28.56% |

- Muitos registos únicos nos QIDs - justifica necessidade de anonimização
- Distinction/Separation: Age é o QID mais discriminativo (97.25% separation)
- Combinações críticas: Age+Ethnic (99.0%), Age+Sex (98.2%)

### 2.3 Criação de Hierarquias

Para cada QID, justificar os níveis da hierarchy:

- **Age**: valor -> [5 anos] -> [10 anos] -> [20 anos] -> *
  - Intervalo de 20 anos escolhido como nível prático (ex: jovens adultos vs meia-idade)
- **Ethnic_Code_Text**: valor -> African-American/Caucasian/Hispanic/Other Minority -> Minority/Caucasian -> *
  - Iteração necessária: hierarchy inicial fundiu African-American em "Black" no nivel 1,
    destruindo a estatística objetivo. Corrigido para manter African-American até nivel 2.
- **Sex_Code_Text**: valor -> *
- **MaritalStatus**: valor -> Single/In Relationship/Former/Unknown -> *
- **LegalStatus**: valor -> Pretrial/Sentenced/Other -> *
- **CustodyStatus**: valor -> Incarcerated/Community/Pretrial -> *
- **Language**: valor -> English/Spanish -> *
- **Screening_Year**: valor -> * (só 2 anos, generalização imediata)

### 2.4 Pesos dos Atributos
- Justificação baseada na relevância para o objetivo de divulgação
- Ethnic_Code_Text e Age com peso máximo (diretamente ligados à estatística objetivo)
- Language e Screening_Year com peso mínimo (pouca variação, baixa discriminação)

---

## 3. Modelos de Privacidade: Utilidade, Privacidade e Avaliação de Risco

### 3.1 k-Anonymity + l-Diversity

#### 3.1.1 Variação de k (l=3 fixo)

| k | Suprimidos | Granularity | Highest Risk | MAE objetivo | Ethnic generalizado |
|---|---|---|---|---|---|
| 5 | 4.85% | 69.99% | 20% | 0.108 | Sim (nivel 1) |
| 10 | 2.44% | 66.49% | 10% | 0.038 | Sim (nivel 1) |

- k=10 domina k=5 em quase todas as métricas
- Explicação: classes maiores satisfazem l=3 naturalmente, sem forçar generalização agressiva

#### 3.1.2 Variação de l (k=5 fixo)

| l | Suprimidos | Granularity | Highest Risk | MAE objetivo | Ethnic generalizado |
|---|---|---|---|---|---|
| 2 | 4.48% | 78.63% | 20% | 0.395 | Não |
| 3 | 4.85% | 69.99% | 20% | 0.108 | Sim (nivel 1) |

- l=2 preserva as etnias mas MAE alto por supressão dos grupos pequenos
- l=3 força generalização de Ethnic mas agrupa grupos pequenos, reduzindo distorção

#### 3.1.3 Resultados e Análise
- Melhor configuração: k=10, l=3
- Análise de risco pelos 3 attacker models
- Comparação da estatística objetivo (tabela original vs anonimizado)
- Discussão: grupos pequenos (Arabic, Asian, Native American) sempre problemáticos

### 3.2 k-Anonymity + t-Closeness

#### 3.2.1 Variação de t (k=5 fixo)

| t | Suprimidos | Granularity | Highest Risk | MAE objetivo | Ethnic generalizado |
|---|---|---|---|---|---|
| 0.20 | 4.93% | 52.45% | 1.89% | N/A | Sim (nivel 2: Minority/Caucasian) |
| 0.30 | 4.17% | 65.37% | 12.5% | 0.043 | Sim (nivel 1) |

- t=0.20 demasiado restritivo: funde Ethnic em 2 grupos, inutiliza estatística objetivo
- t=0.30 preserva African-American, resultados comparáveis ao melhor l-Diversity

#### 3.2.2 Resultados e Análise
- Melhor configuração: k=5, t=0.30
- Análise de risco pelos 3 attacker models
- Comparação da estatística objetivo
- Nota: RawScores reclassificados como insensitive para t-Closeness (justificação)

### 3.3 Comparação entre Modelos e Recomendação Final

| Configuração | Suprimidos | Granularity | Highest Risk | MAE objetivo |
|---|---|---|---|---|
| k=2, l=2 | 4.21% | 77.36% | 50% | 0.38 |
| k=5, l=2 | 4.48% | 78.63% | 20% | 0.395 |
| k=5, l=3 | 4.85% | 69.99% | 20% | 0.108 |
| **k=10, l=3** | **2.44%** | **66.49%** | **10%** | **0.038** |
| k=5, t=0.20 | 4.93% | 52.45% | 1.89% | N/A |
| **k=5, t=0.30** | **4.17%** | **65.37%** | **12.5%** | **0.043** |

- Recomendação: k=10, l=3 para análise de disparidades raciais
- Discussão: tensão fundamental entre t-Closeness e o objetivo de divulgação
  (t-Closeness esconde precisamente as distribuições que queremos estudar)
- Limitação: grupos étnicos pequenos (Arabic, Asian, Native American) perdem
  representatividade em todas as configurações

---

## 4. Anexos
- 4.1 Distribuição completa dos atributos (plots de results/exploratory/)
- 4.2 Hierarchies completas (tabelas)
- 4.3 Tabelas completas de comparação estatística objetivo (original vs anonimizado)
