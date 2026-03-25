import pandas as pd

df = pd.read_csv('data/original/reviews.csv', nrows=5000)

print(f"Linhas: {len(df)}, Colunas: {len(df.columns)}")

print("\n=== Colunas e Tipos ===")
print(df.dtypes)

print("\n=== Valores Nulos ===")
print(df.isnull().sum())

print("\n=== Valores Únicos por Coluna ===")
for col in df.columns:
    print(f"  {col}: {df[col].nunique()} únicos")
