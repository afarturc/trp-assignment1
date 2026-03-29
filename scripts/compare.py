import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

os.makedirs('results/arx', exist_ok=True)

# ============================================================
# Uso: python scripts/compare.py <ficheiro_anonimizado>
# Ex:  python scripts/compare.py data/anonymized/compas_kanon_ldiv_k5_l3.csv
# ============================================================

if len(sys.argv) < 2:
    print("Uso: python scripts/compare.py <ficheiro_anonimizado>")
    sys.exit(1)

anon_path = sys.argv[1]
label = os.path.splitext(os.path.basename(anon_path))[0]

print(f"Comparando: {anon_path}")

# ============================================================
# 1. Carregar datasets
# ============================================================
orig = pd.read_csv('data/sanitized/compas_sanitized.csv')
anon = pd.read_csv(anon_path)

print(f"Original:    {len(orig)} registos")
print(f"Anonimizado: {len(anon)} registos")

# Suprimidos: todos os QIDs sao *
qids = ['Age', 'Sex_Code_Text', 'Ethnic_Code_Text', 'MaritalStatus',
        'Language', 'LegalStatus', 'CustodyStatus', 'Screening_Year']
suppressed_mask = (anon[qids] == '*').all(axis=1)
suppressed = anon[suppressed_mask]
non_supp = anon[~suppressed_mask].copy()
suppressed_pct = len(suppressed) / len(anon) * 100
print(f"Suprimidos:  {len(suppressed)} ({suppressed_pct:.2f}%)")

# ============================================================
# 2. Estatística objetivo: média DecileScore_Recidivism
#    por Ethnic_Code_Text x Sex_Code_Text
# ============================================================

# Original (já calculado, mas recalcula para garantir consistência)
obj_orig = orig.groupby(['Ethnic_Code_Text', 'Sex_Code_Text']).agg(
    mean_decile_orig=('DecileScore_Recidivism', 'mean'),
    count_orig=('DecileScore_Recidivism', 'size')
).round(2)

# Anonimizado (converter DecileScore_Recidivism para numérico)
non_supp['DecileScore_Recidivism'] = pd.to_numeric(non_supp['DecileScore_Recidivism'], errors='coerce')
obj_anon = non_supp.groupby(['Ethnic_Code_Text', 'Sex_Code_Text']).agg(
    mean_decile_anon=('DecileScore_Recidivism', 'mean'),
    count_anon=('DecileScore_Recidivism', 'size')
).round(2)

# Juntar
comparison = obj_orig.join(obj_anon, how='left')
comparison['diff'] = (comparison['mean_decile_anon'] - comparison['mean_decile_orig']).round(2)
comparison['count_retained_pct'] = (comparison['count_anon'] / comparison['count_orig'] * 100).round(1)

print("\n=== Estatística Objetivo: média DecileScore_Recidivism ===")
print(comparison.to_string())

out_csv = f'results/arx/comparison_{label}.csv'
comparison.to_csv(out_csv)
print(f"\nGuardado em {out_csv}")

# ============================================================
# 3. Gráfico: original vs anonimizado por etnia x género
# ============================================================
comp_reset = comparison.reset_index()

fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
for i, sex in enumerate(['Male', 'Female']):
    subset = comp_reset[comp_reset['Sex_Code_Text'] == sex].dropna(subset=['mean_decile_anon'])
    x = range(len(subset))
    width = 0.35
    axes[i].bar([xi - width/2 for xi in x], subset['mean_decile_orig'], width, label='Original', color='steelblue')
    axes[i].bar([xi + width/2 for xi in x], subset['mean_decile_anon'], width, label='Anonimizado', color='coral')
    axes[i].set_xticks(list(x))
    axes[i].set_xticklabels(subset['Ethnic_Code_Text'], rotation=30, ha='right')
    axes[i].set_title(f'{sex}')
    axes[i].set_ylabel('Média DecileScore Recidivism')
    axes[i].legend()
    axes[i].set_ylim(0, 10)

fig.suptitle(f'Original vs Anonimizado ({label})', fontsize=13)
fig.tight_layout()
out_png = f'results/arx/comparison_{label}.png'
fig.savefig(out_png, dpi=150)
plt.close()
print(f"Gráfico guardado em {out_png}")

# ============================================================
# 4. MAE global (erro médio absoluto da estatística objetivo)
# ============================================================
mae = comparison['diff'].abs().mean()
print(f"\nMAE da estatística objetivo: {mae:.4f}")
