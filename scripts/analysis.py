import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs('results/exploratory', exist_ok=True)
os.makedirs('results/arx', exist_ok=True)

df = pd.read_csv('data/original/compas-scores-raw.csv')
print(f"Linhas: {len(df)}, Colunas: {len(df.columns)}")

# ============================================================
# 1. Valores nulos por coluna
# ============================================================
print("\n=== 1. Valores Nulos ===")
nulls = df.isnull().sum()
nulls_pct = (nulls / len(df) * 100).round(2)
nulls_df = pd.DataFrame({'nulls': nulls, '%': nulls_pct})
print(nulls_df[nulls_df['nulls'] > 0])
nulls_df.to_csv('results/exploratory/nulls.csv')

# ============================================================
# 2. Colunas constantes ou quase constantes (validação)
# ============================================================
print("\n=== 2. Colunas Constantes / Quase Constantes ===")
for col in ['AssessmentReason', 'IsCompleted', 'IsDeleted', 'ScaleSet', 'AssessmentType']:
    vc = df[col].value_counts()
    print(f"\n  {col} ({df[col].nunique()} valores):")
    print(f"    {vc.to_string()}")

# ============================================================
# 3. DisplayText (confirmar 3 scales para pivot)
# ============================================================
print("\n=== 3. DisplayText (scales) ===")
print(df['DisplayText'].value_counts().to_string())

# Confirmar que cada Person_ID tem exatamente 3 linhas
lines_per_person = df.groupby('Person_ID').size()
print(f"\n  Linhas por Person_ID: min={lines_per_person.min()}, max={lines_per_person.max()}")
print(f"  Distribuição:")
print(lines_per_person.value_counts().sort_index().to_string())

# ============================================================
# 4. Atributos categóricos (futuros QIDs e outros)
# ============================================================
cat_cols = ['Sex_Code_Text', 'Ethnic_Code_Text', 'MaritalStatus',
            'Language', 'LegalStatus', 'CustodyStatus',
            'Agency_Text', 'RecSupervisionLevelText']

print("\n=== 4. Distribuição - Atributos Categóricos ===")
for col in cat_cols:
    vc = df[col].value_counts()
    vc_pct = (vc / len(df) * 100).round(2)
    display = pd.DataFrame({'count': vc, '%': vc_pct})
    print(f"\n  {col} ({df[col].nunique()} valores):")
    print(f"    {display.to_string()}")
    display.to_csv(f'results/exploratory/dist_{col}.csv')

# ============================================================
# 5. Scores numéricos (RawScore e DecileScore por tipo de scale)
# ============================================================
print("\n=== 5. Estatísticas - Scores Numéricos (por scale) ===")
for scale in df['DisplayText'].unique():
    subset = df[df['DisplayText'] == scale]
    print(f"\n  --- {scale} ---")
    for score_col in ['RawScore', 'DecileScore']:
        desc = subset[score_col].describe(percentiles=[.01, .05, .25, .5, .75, .95, .99]).round(2)
        print(f"\n    {score_col}:")
        print(f"      {desc.to_string()}")

# Estatísticas globais
print("\n  --- Global ---")
for score_col in ['RawScore', 'DecileScore']:
    desc = df[score_col].describe(percentiles=[.01, .05, .25, .5, .75, .95, .99]).round(2)
    print(f"\n    {score_col}:")
    print(f"      {desc.to_string()}")
    desc.to_csv(f'results/exploratory/stats_{score_col}.csv')

# ============================================================
# 6. DateOfBirth - distribuição de idades
# ============================================================
print("\n=== 6. Idade (derivada de DateOfBirth) ===")
# Usar a primeira ocorrência de cada pessoa para não contar 3x
first_per_person = df.drop_duplicates(subset='Person_ID')

dob = pd.to_datetime(first_per_person['DateOfBirth'], format='%m/%d/%y', errors='coerce')
# Corrigir anos futuros (pandas interpreta 2-digit year: 68 -> 2068 em vez de 1968)
dob = dob.where(dob.dt.year <= 2025, dob - pd.DateOffset(years=100))

screening = pd.to_datetime(first_per_person['Screening_Date'], errors='coerce')
age = ((screening - dob).dt.days / 365.25).round(0).astype('Int64')
first_per_person = first_per_person.copy()
first_per_person['Age'] = age

print(f"  Min: {age.min()}, Max: {age.max()}, Média: {age.mean():.1f}, Mediana: {age.median():.1f}")
print(f"  Nulls: {age.isna().sum()}")

fig, ax = plt.subplots(figsize=(10, 5))
age.dropna().astype(int).hist(bins=50, ax=ax, edgecolor='black')
ax.set_xlabel('Idade')
ax.set_ylabel('Frequência')
ax.set_title('Distribuição de Idade (por pessoa)')
fig.tight_layout()
fig.savefig('results/exploratory/dist_age.png', dpi=150)
plt.close()

# ============================================================
# 7. Screening_Date - distribuição por ano
# ============================================================
print("\n=== 7. Screening_Date (por ano) ===")
screening_all = pd.to_datetime(df['Screening_Date'], errors='coerce')
years = screening_all.dt.year.value_counts().sort_index()
print(years.to_string())
years.to_csv('results/exploratory/dist_screening_year.csv')

# ============================================================
# 8. Histogramas / Boxplots
# ============================================================

# 8a. DecileScore de Recidivism por Ethnic_Code_Text (pessoas únicas)
recid = df[df['DisplayText'] == 'Risk of Recidivism'].drop_duplicates(subset='Person_ID')

fig, ax = plt.subplots(figsize=(12, 5))
ethnicities = recid['Ethnic_Code_Text'].value_counts().index.tolist()
data_by_eth = [recid[recid['Ethnic_Code_Text'] == e]['DecileScore'].values for e in ethnicities]
ax.boxplot(data_by_eth, labels=ethnicities)
ax.set_ylabel('DecileScore (Recidivism)')
ax.set_title('DecileScore Recidivism por Etnia')
plt.xticks(rotation=30, ha='right')
fig.tight_layout()
fig.savefig('results/exploratory/boxplot_decile_by_ethnicity.png', dpi=150)
plt.close()

# 8b. DecileScore de Recidivism por Etnia x Género
fig, axes = plt.subplots(1, 2, figsize=(16, 5), sharey=True)
for i, sex in enumerate(['Male', 'Female']):
    subset = recid[recid['Sex_Code_Text'] == sex]
    data = [subset[subset['Ethnic_Code_Text'] == e]['DecileScore'].values for e in ethnicities]
    axes[i].boxplot(data, labels=ethnicities)
    axes[i].set_title(f'DecileScore Recidivism - {sex}')
    axes[i].set_ylabel('DecileScore')
    axes[i].tick_params(axis='x', rotation=30)
fig.tight_layout()
fig.savefig('results/exploratory/boxplot_decile_by_ethnicity_gender.png', dpi=150)
plt.close()

# 8c. Heatmap de correlação entre scores (por pessoa, após pivot simplificado)
print("\n=== 8. Correlação entre Scores ===")
pivot_scores = df.pivot_table(
    index='Person_ID',
    columns='DisplayText',
    values=['RawScore', 'DecileScore'],
    aggfunc='first'
)
pivot_scores.columns = [f'{score}_{scale.replace("Risk of ", "")}' for score, scale in pivot_scores.columns]
corr = pivot_scores.corr().round(2)
print(corr.to_string())

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.columns)))
ax.set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=8)
ax.set_yticklabels(corr.columns, fontsize=8)
for i in range(len(corr)):
    for j in range(len(corr)):
        ax.text(j, i, f'{corr.values[i, j]:.2f}', ha='center', va='center', fontsize=7)
fig.colorbar(im)
ax.set_title('Correlação entre Scores')
fig.tight_layout()
fig.savefig('results/exploratory/heatmap_score_correlation.png', dpi=150)
plt.close()

# ============================================================
# 9. Distribuição de Ethnic_Code_Text (bar chart, por pessoa)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))
eth_counts = first_per_person['Ethnic_Code_Text'].value_counts()
eth_counts.plot.bar(ax=ax, edgecolor='black')
ax.set_ylabel('Frequência')
ax.set_title('Distribuição de Etnia (por pessoa)')
ax.tick_params(axis='x', rotation=30)
fig.tight_layout()
fig.savefig('results/exploratory/dist_ethnicity.png', dpi=150)
plt.close()

# ============================================================
# 10. Estatística do objetivo (DecileScore_Recidivism por Etnia x Sexo)
# ============================================================
print("\n=== 10. Estatística do Objetivo ===")
print("Média de DecileScore_Recidivism por Ethnic_Code_Text x Sex_Code_Text:")
obj = recid.groupby(['Ethnic_Code_Text', 'Sex_Code_Text']).agg(
    mean_decile=('DecileScore', 'mean'),
    count=('DecileScore', 'size')
).round(2)
print(obj.to_string())
obj.to_csv('results/arx/objetivo_original.csv')

print("\n=== Resultados guardados em results/exploratory/ e results/arx/ ===")
