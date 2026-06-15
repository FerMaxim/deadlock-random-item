# DeadlockPredictionML

Machine Learning pipeline and build simulator for the game **Deadlock**. This project focuses on processing massive raw match data (`.parquet` dumps), extracting meaningful item and ability progression sequences, and using ML algorithms (like XGBoost) to predict, simulate, and generate optimized meta-builds.

## Features
- **Data Processing:** Parses 3GB+ `.parquet` files containing raw match data using `DuckDB` and `pandas`.
- **Ability Extraction:** Reconstructs chronologically ordered skill upgrades from raw item matrices.
- **Clustering & Meta Analysis:** Groups builds into distinct playstyles (e.g., Gun vs Spirit Bebop) using clustering techniques.
- **Build Simulator:** Generates autoregressive item/skill builds utilizing an XGBoost-based predictive model with temperature sampling.

## Project Structure
```text
deadlockPredictionML/
├── data/
│   ├── processed/     # ML-ready CSV datasets (e.g., clustered data, clean stats)
│   ├── raw/           # Raw .parquet match dumps
│   └── reference/     # API references (heroes.json, items.json)
├── src/
│   ├── data_collection/ # Scripts for fetching external API data
│   ├── data_processing/ # Pipeline for cleaning and transforming match data
│   ├── ml_pipeline/     # Training and clustering scripts
│   └── simulator/       # Generative build scripts (xgb_generator.py)
├── project_overview.md  # Detailed architecture documentation
└── README.md
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/deadlockPredictionML.git
   cd deadlockPredictionML
   ```
2. Install dependencies:
   ```bash
   pip install duckdb pandas xgboost scikit-learn requests
   ```
3. **Data Requirements**: The raw `.parquet` database files are too large for GitHub and are excluded via `.gitignore`. You must download them manually from [Deadlock API Data Dumps](https://deadlock-api.com/data-dumps) and place them in the `data/raw/` directory before running the pipeline.

## Usage
- **Data Processing:** Run `src/data_processing/build_training_dataset.py` to convert raw Parquet match files into ML-ready CSV datasets (separating out pure item builds and skill progressions).
- **Simulator:** Run `src/simulator/xgb_generator.py` to generate new builds based on the learned meta.

## Documentation
For a detailed architectural breakdown and data pipeline explanation, see [project_overview.md](project_overview.md).
