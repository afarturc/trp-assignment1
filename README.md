# TRP Assignment 1 - Anonymization of Datasets

Privacy, Utility and Risk Analysis using [ARX](https://arx.deidentifier.org/).

**Dataset:** [COMPAS Recidivism Risk Score Data](https://www.kaggle.com/datasets/danofer/compass) (ProPublica, ~60K rows, 28 columns - ~18.6K after pivoting)

## Project Structure

```
├── data/
│   ├── original/          # Original dataset (not tracked by git)
│   ├── sanitized/         # Cleaned dataset ready for ARX (compas_sanitized.csv)
│   ├── hierarchies/       # Generalization hierarchies for quasi-identifiers
│   └── anonymized/        # Anonymized datasets exported from ARX (not tracked by git)
├── arx/
│   └── assignment-1.deid  # ARX project file
├── scripts/
│   ├── analysis.py        # Exploratory analysis and distributions
│   ├── sanitize.py        # Data cleaning and preparation
│   └── compare.py         # Original vs. anonymized comparison (Phase 4)
├── notebooks/
│   └── 01_exploratory_analysis.ipynb
├── results/
│   ├── exploratory/       # Distributions, plots and stats from Phase 1
│   └── arx/               # ARX experiment metrics and baseline stats
├── docs/
│   ├── enunciado/         # Assignment specification
│   └── exemplos/          # Example reports
└── report/                # Final report
```

## Setup

```bash
pip install -r requirements.txt
```

Scripts should be run from the project root:

```bash
python scripts/analysis.py
python scripts/sanitize.py
python scripts/compare.py
```

## Phases

| Phase | Description | Status |
|---|---|---|
| 1 | Data preparation and exploratory analysis (Python) | Done |
| 2 | ARX configuration: attribute classification, hierarchies, risk baseline | Done |
| 3 | Privacy models: k-Anonymity + l-Diversity, k-Anonymity + t-Closeness | In progress |
| 4 | Comparison, report and defence | Pending |
