# RF Framework Documentation

## Overview
The **RF Framework** automates **Random Forest training**, **HLS code generation**, **Vivado HLS synthesis**, and **prediction verification**.  
It uses a CLI (`rf_cli.py` or `rf`) for an end-to-end workflow from data to deployable FPGA code.

---

## Installation

```bash
pip install scikit-learn pandas numpy matplotlib jinja2 pyyaml vivado_hls
```

Ensure that **Vivado HLS** is available in your system `PATH`.

Check the CLI help:
```bash
python rf_cli.py --help
```

---

## CLI Commands

### Create Configuration
```bash
rf create-config --output rf_config.yaml
```

### Train Model
```bash
rf train --data data.csv --features f1,f2 --targets t1 --output rf_output
```

### Quick Start (Train + Export)
```bash
rf quick-start --data data.csv --features f1,f2 --targets t1   --output rf_output --export-format legacy
```

### Export Trained Model to HLS
```bash
rf export --model model.pkl --output rf_export --export-format legacy
```

### Generate HLS Synthesis Report
```bash
rf hls-report --project-dir rf_output
```

### Verify Predictions
```bash
rf verify --output-dir rf_output
```

---

## Training Workflow

### 1. Config Setup
Edit `rf_config.yaml` for dataset and model parameters:

```yaml
yamldata:
  source: https://example.com/data.csv
  feature_cols: [f1, f2]
  target_cols: [t1]
  scaler: minmax
  test_size: 0.2
model:
  type: random_forest
  task: regression
  n_estimators: 20
  max_depth: 6
```

### 2. Run Training
```bash
rf quick-start --data data.csv --features f1,f2 --targets t1 --output rf_output
```

**Process:**
- Loads and splits data.
- Applies scaling.
- Trains Random Forest model.
- Saves outputs:
  - `Y_pred.npy` — scaled predictions.
  - `scaler_y.pkl` — target scaler.
  - `rf_config.yaml` — final config.
  - `rf_metrics.json` — performance metrics.

**Outputs:** Model artifacts in `rf_output/`.

---

## HLS Code Generation

Triggered during `quick-start` or `export` step.

**Generated Files:**
```
myproj_core.cpp
myproj_axi.cpp
rfr_tb.cpp
rfr_common.h
scaler_constants.h
rf_project.tcl
```

**Mechanism:**
- Uses Jinja2 templates to export trained Random Forest trees.
- Generates complete Vivado HLS project files automatically.

Run inside Vivado HLS:
```bash
cd rf_output/rf_project
vivado_hls -f rf_project.tcl
```

---

## Vivado HLS Synthesis

### 1. Run C Simulation (Testbench)
```bash
cd rf_output/rf_project
vivado_hls -f rf_project.tcl
```

**Executes:**
```
csim_design
```

**Output:**
- `Y_hls_pred.csv` — unscaled predictions (from HLS simulation).

Located in:
```
solution1/csim/build/
```

### 2. Run Synthesis and Export
```bash
# Uncomment in rf_project.tcl if needed:
# csynth_design
# cosim_design
# export_design -format ip_catalog
```

**Reports:**
```bash
rf hls-report --project-dir rf_output
```

Shows:
- Resource utilization
- Timing
- Performance summaries

---

## Verification & Comparison

### Run Verification
```bash
rf verify --output-dir rf_output
```

or directly:
```bash
python pred_verification.py --output-dir rf_output
```

### Process:
1. Loads `rf_config.yaml` for feature/target columns.
2. Unscales `Y_pred.npy` using `scaler_y.pkl`.
3. Compares predictions from Python vs HLS (`Y_hls_pred.csv`).
4. Computes metrics:
   - MAE (Mean Absolute Error)
   - R² (Coefficient of Determination)
5. Generates `pred_comparison.png` — scatter plot of HLS vs Python outputs.

### Outputs:
- **Console metrics:** e.g., `R² = 0.9991`
- **Plot:** `pred_comparison.png`

---

## Troubleshooting

| Issue | Possible Cause / Fix |
|--------|----------------------|
| **Missing Config** | Ensure `rf_config.yaml` contains `data.source`, `feature_cols`, `target_cols`. |
| **No CSV output** | Run CSim first. |
| **Shape Error** | Framework auto-handles 1D/2D; ensure correct column names. |
| **Low Metrics** | Check scaling/unscaling correctness. |

---

## Full Workflow Example

```bash
# 1. Quick Start (Train + Export)
rf quick-start --data https://raw.githubusercontent.com/AbuAli3/ee/main/alldata.csv   --features Occupancy,Rel_Hum,Room_Temp,Air_Flow_Rat,Air_Temp   --targets Elec_Cons,Therm_Eng_Cons,PMV   --output my_proj --export-format legacy

# 2. Synthesize (Vivado HLS)
cd my_proj/rf_project
vivado_hls -f rf_project.tcl

# 3. Verify Predictions
cd ..
rf verify --output-dir my_proj
```

---

## 📘 Example for Local Salary Dataset

```bash
python3 rf_cli.py quick-start   --data /home/mo/fastml_framework_rf/Salary_dataset.csv   --features YearsExperience   --targets Salary   --export-format legacy   --output salary_proj   --verbose
```

**Dataset Example:**
```csv
,YearsExperience,Salary
0,1.2,39344.0
1,1.4,46206.0
2,1.6,37732.0
...
29,10.6,121873.0
```

This trains a 1-feature Random Forest Regressor on salary data, exports it to `salary_proj/`, and prepares it for Vivado HLS synthesis and verification.

---

**End of Document**
