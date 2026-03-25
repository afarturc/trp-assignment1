# TRP Assignment 1 — Anonymization of Datasets

Privacy, Utility and Risk Analysis using [ARX](https://arx.deidentifier.org/).

**Dataset:** [Steam Games Dataset 2025](https://www.kaggle.com/datasets/abhishekgupta56447/steam-games-dataset-2025) (~4M rows, 23 columns)

## Project Structure

```
├── data/
│   ├── original/          # Original dataset (not tracked by git)
│   └── anonymized/        # Anonymized datasets exported from ARX
├── scripts/
│   ├── analysis.py        # Exploratory analysis and distributions
│   ├── sanitize.py        # Data cleaning and preparation
│   └── compare.py         # Original vs. anonymized comparison
├── arx/
│   └── hierarchies/       # Generalization hierarchies for quasi-identifiers
├── docs/
│   ├── enunciado/         # Assignment specification
│   └── exemplos/          # Example reports
├── report/                # Final report
└── results/               # Figures, tables, analysis outputs
```

## Setup

```bash
pip install -r requirements.txt
```

Scripts should be run from the project root:

```bash
python scripts/analysis.py
```
