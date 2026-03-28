import pandas as pd
import os

os.makedirs('data/sanitized', exist_ok=True)

df = pd.read_csv('data/original/compas-scores-raw.csv')
print(f"Original: {len(df)} linhas, {df['Person_ID'].nunique()} pessoas")

# ============================================================
# 1. Remover linhas com DecileScore = -1 (scores inválidos)
# ============================================================
invalid_persons = df[df['DecileScore'] == -1]['Person_ID'].unique()
df = df[~df['Person_ID'].isin(invalid_persons)]
print(f"Após remover DecileScore=-1: {len(df)} linhas, {df['Person_ID'].nunique()} pessoas (removidas {len(invalid_persons)})")

# ============================================================
# 2. Manter apenas a avaliação mais recente por pessoa
#    (maior AssessmentID = mais recente)
# ============================================================
latest_assessment = df.groupby('Person_ID')['AssessmentID'].max().reset_index()
df = df.merge(latest_assessment, on=['Person_ID', 'AssessmentID'])
print(f"Após manter última avaliação: {len(df)} linhas, {df['Person_ID'].nunique()} pessoas")

# Verificar que cada pessoa tem exatamente 3 linhas
lines_per_person = df.groupby('Person_ID').size()
assert (lines_per_person == 3).all(), f"Erro: nem todas as pessoas têm 3 linhas: {lines_per_person.value_counts().to_dict()}"
print(f"Confirmado: todas as pessoas têm exatamente 3 linhas")

# ============================================================
# 3. Pivotar: 3 linhas por pessoa -> 1 linha
# ============================================================
# Colunas que são iguais em todas as 3 linhas (dados da pessoa)
person_cols = [
    'Person_ID', 'FirstName', 'LastName', 'MiddleName', 'Case_ID',
    'Sex_Code_Text', 'Ethnic_Code_Text', 'DateOfBirth',
    'Language', 'LegalStatus', 'CustodyStatus', 'MaritalStatus',
    'Screening_Date', 'Agency_Text', 'RecSupervisionLevelText'
]

# Base: dados da pessoa (1 linha por pessoa)
base = df.drop_duplicates(subset='Person_ID')[person_cols].set_index('Person_ID')

# Pivot dos scores
scores = df.pivot_table(
    index='Person_ID',
    columns='DisplayText',
    values=['RawScore', 'DecileScore'],
    aggfunc='first'
)
# Flatten column names
scores.columns = [
    f'{score}_{scale.replace("Risk of ", "").replace("Failure to Appear", "FTA")}'
    for score, scale in scores.columns
]

result = base.join(scores).reset_index()
print(f"Após pivot: {len(result)} linhas, {len(result.columns)} colunas")

# ============================================================
# 4. Derivar Age a partir de DateOfBirth e Screening_Date
# ============================================================
dob = pd.to_datetime(result['DateOfBirth'], format='mixed', dayfirst=False, errors='coerce')
screening = pd.to_datetime(result['Screening_Date'], format='mixed', dayfirst=False, errors='coerce')

# Corrigir anos 2-digit: se DoB > Screening_Date, subtrair 100 anos
dob = dob.where(dob <= screening, dob - pd.DateOffset(years=100))

result['Age'] = ((screening - dob).dt.days / 365.25).round(0).astype(int)
print(f"Idade: min={result['Age'].min()}, max={result['Age'].max()}")

# ============================================================
# 5. Derivar Screening_Year
# ============================================================
result['Screening_Year'] = screening.dt.year

# ============================================================
# 6. Merge etnias
# ============================================================
result['Ethnic_Code_Text'] = result['Ethnic_Code_Text'].replace({
    'African-Am': 'African-American',
    'Oriental': 'Asian'
})
print(f"Etnias após merge: {result['Ethnic_Code_Text'].nunique()} valores")
print(result['Ethnic_Code_Text'].value_counts().to_string())

# ============================================================
# 7. Selecionar e ordenar colunas finais
# ============================================================
final_cols = [
    # Identifying (o ARX remove automaticamente)
    'Person_ID', 'FirstName', 'LastName', 'MiddleName', 'Case_ID', 'DateOfBirth',
    # Quasi-identifying
    'Age', 'Sex_Code_Text', 'Ethnic_Code_Text', 'MaritalStatus',
    'Language', 'LegalStatus', 'CustodyStatus', 'Screening_Year',
    # Insensitive
    'Agency_Text',
    # Sensitive
    'RecSupervisionLevelText',
    'RawScore_Recidivism', 'RawScore_Violence', 'RawScore_FTA',
    'DecileScore_Recidivism', 'DecileScore_Violence', 'DecileScore_FTA',
]

result = result[final_cols]
print(f"\nDataset final: {len(result)} linhas, {len(result.columns)} colunas")
print(f"Colunas: {list(result.columns)}")

# ============================================================
# 8. Guardar
# ============================================================
result.to_csv('data/sanitized/compas_sanitized.csv', index=False)
print(f"\nGuardado em data/sanitized/compas_sanitized.csv")

# Resumo
print("\n=== Resumo ===")
print(result.describe(include='all').to_string())
