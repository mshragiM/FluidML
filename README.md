# FluidML

FluidML is a Python framework that trains Random Forest models and exports FPGA-ready HLS inference code for Xilinx Vivado HLS / Vitis HLS workflows.

It is designed for fast end-to-end flow:

1. Load tabular dataset
2. Train and evaluate model
3. Export C++/HLS source + TCL scripts
4. Run synthesis and hardware integration

## Key Features

- End-to-end CLI for training + HLS export
- Random Forest regression/classification support
- Multi-output regression support
- Automatic preprocessing and scaling
- Jinja2-based hardware code generation templates
- Backend-aware export for `vivado_hls` and `vitis_hls`
- Auto-generated artifacts:
  - model/scaler/config/metrics files
  - HLS source (`.h` / `.cpp`)
  - HLS project TCL
  - Vivado block design TCL
  - Markdown report

## Repository Structure

```text
FluidML/
|-- fluidml/
|   |-- __init__.py
|   |-- cli.py
|   |-- config.py
|   |-- data.py
|   |-- training.py
|   |-- codegen.py
|   `-- framework.py
|-- templates/
|   |-- firmware/
|   `-- test/
|-- fluidml_cli.py          # Main CLI entrypoint
|-- rf_cli.py               # Legacy compatibility wrapper
|-- rf_framework.py         # Legacy compatibility wrapper
`-- README.md
```

## Requirements

- Python 3.9+ (recommended: 3.10)
- Python packages:
  - `numpy`
  - `pandas`
  - `scikit-learn`
  - `jinja2`
  - `pyyaml`

Install quickly:

```bash
pip install numpy pandas scikit-learn jinja2 pyyaml
```

## Quick Start (Your Energy Dataset)

From repository root:

```bash
python fluidml_cli.py quick-start --data https://raw.githubusercontent.com/AbuAli3/ee/main/alldata.csv --features Occupancy,Rel_Hum,Room_Temp,Air_Flow_Rat,Air_Temp --targets Elec_Cons --output energy_pred --verbose
```

This will:

- train a model
- evaluate inference performance
- save model + metrics
- generate HLS files and TCL scripts in `energy_pred/`

## Main CLI Commands

### 1) Quick start

```bash
python fluidml_cli.py quick-start --data data.csv --features f1,f2 --targets y --output out_dir
```

### 2) Train only

```bash
python fluidml_cli.py train --data data.csv --features f1,f2 --targets y --output out_dir --save-model model.pkl
```

### 3) Export from saved model

```bash
python fluidml_cli.py export --model model.pkl --output out_dir --backend vivado_hls
```

### 4) Create config template

```bash
python fluidml_cli.py create-config --output fluidml_config.yaml
```

### 5) Print synthesis report summary

```bash
python fluidml_cli.py hls-report --project-dir energy_pred/fluidml_project
```

## Generated Output Files

After a successful quick start, `energy_pred/` will include files such as:

- `fluidml_model.pkl`
- `fluidml_config.yaml`
- `fluidml_metrics.json`
- `fluidml_report.md`
- `X_test.npy`, `Y_test.npy`, `Y_pred.npy`
- generated firmware/test C++ and headers
- `<project_name>.tcl` (default: `fluidml_project.tcl`)
- `vivado_block_design.tcl`

## HLS / FPGA Flow

### Vivado HLS

```bash
cd energy_pred
vivado_hls -f fluidml_project.tcl
```

### Bitstream generation (Vivado batch)

```bash
cd energy_pred
vivado -mode batch -source vivado_block_design.tcl
```

### Vitis HLS (optional)

```bash
python fluidml_cli.py quick-start --data data.csv --features f1,f2 --targets y --backend vitis_hls --output out_vitis
```

## Python API Example

```python
from fluidml import FluidMLFramework

fw = FluidMLFramework()
fw.load_data(
    "https://raw.githubusercontent.com/AbuAli3/ee/main/alldata.csv",
    feature_cols=["Occupancy", "Rel_Hum", "Room_Temp", "Air_Flow_Rat", "Air_Temp"],
    target_cols=["Elec_Cons"],
)
metrics = fw.train()
fw.export_to_hls_j2("energy_pred")
fw.generate_report()
print(metrics)
```

## Backward Compatibility

Legacy wrappers are still available:

- `python rf_cli.py ...`
- `from rf_framework import ...`

New projects should use `fluidml` modules directly.

## Publication Notes (Recommended for GitHub)

Before public release, add:

- `LICENSE` file (for example, MIT)
- `requirements.txt` or `pyproject.toml`
- unit tests (CLI smoke tests + data/model/export tests)
- CI workflow (lint + tests)
- tagged release (`v1.0.0`)

## Author

Mohammed Mshragi
