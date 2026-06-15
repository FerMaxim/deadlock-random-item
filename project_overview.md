# Project Overview: DeadlockPredictionML

## Architecture & Pipeline

### 1. Raw Data Ingestion (`data/raw/`)
The system accepts large `.parquet` dumps containing detailed player match statistics. Because these files can exceed 3GB, they are excluded from version control. You must download the raw match databases from [Deadlock API Data Dumps](https://deadlock-api.com/data-dumps) and place them in the `data/raw/` directory. We utilize **DuckDB** to query the data efficiently without overloading system memory, bridging the gap between raw unstructured data and pandas DataFrames.

### 2. Data Cleaning & Transformation (`src/data_processing/`)
- **`build_training_dataset.py`**: The core pipeline script. It iterates over raw matches, extracts critical features, drops unnecessary API bloat, and creates an ML-ready dataset.
- **Skill Extraction Mechanics**: Deadlock's API tracks ability upgrades identically to regular shop items (all stored in `items.item_id`). Using `items.json` and `heroes.json` reference dictionaries, the script intelligently separates purchased shop items (`item_build`) from ability point distributions (`skill_build`). It outputs chronologically sorted progression sequences that model exactly how high-MMR players level up.

### 3. Machine Learning Pipeline (`src/ml_pipeline/`)
- Analyzes high-MMR matches to identify clustered archetypes.
- **Clustering (`bebop_clustered.csv`)**: Evaluates player soul distribution (e.g., Weapon vs. Spirit vs. Vitality souls) to automatically assign cluster IDs, discovering distinct meta playstyles (e.g., "Spirit Bomb Bebop" vs. "Gun Bebop").

### 4. Generative Simulator (`src/simulator/`)
- **`xgb_generator.py`**: An autoregressive generator using XGBoost. It takes an archetype (cluster) and current inventory state as input, and iteratively predicts the next best item/skill to purchase.
- **Temperature Control**:
  - `T = 0.0`: Strict adherence to the meta (highest probability items only).
  - `T = 0.1 - 0.5`: Realistic variation, providing viable, slight deviations from standard builds (simulating human variability).
  - `T > 1.0`: Chaos/Experimental builds.
- **Inventory Management**: Implements strict game logic to prevent duplicate item purchases and ensures the simulator respects active/passive slot limits.

## Next Steps & Roadmap
- **Reference Overrides**: Implementation of forced "Golden/Reference Builds" to guide the generator toward verified optimal paths before falling back to ML predictions.
- **Time-Series Powerspikes**: Deeper integration of time-series analysis to predict powerspikes based on `game_time_s` rather than just static sequences.
- **Automated Data Fetching**: Building a pipeline to automatically pull the latest Parquet dumps and patch data from the Deadlock API.
