# RF Framework CLI Documentation

© 2025 Mohammed Ali. All rights reserved.

## Overview
RF Framework is a machine learning framework that trains Random Forest models and generates optimized HLS C++ code for FPGA deployment.

## Installation
```bash
# Clone the repository
git clone <your-repo>
cd fastml_framework_rf

# Install dependencies
pip install -r requirements.txt
```

## Quick Start
```bash
# Quick start with automatic configuration
python rf_cli.py quick-start --data data.csv --features col1,col2 --targets target1,target2

# Example with energy dataset
python rf_cli.py quick-start --data https://raw.githubusercontent.com/AbuAli3/ee/main/alldata.csv  --features Hour,Day,Month,Occupancy,Rel_Hum --targets Elec_Cons,Therm_Eng_Cons,PMV --output my_project --verbose
```

## Commands

### 1. Quick Start
Fastest way to train and export a model with sensible defaults.

```bash
python rf_cli.py quick-start --data <data_source> [options]

# Options:
--data, -d          Path to dataset file or URL (required)
--features, -f      Comma-separated feature columns
--targets, -t       Comma-separated target columns  
--output, -o        Output directory (default: rf_quickstart)
--n-estimators      Number of trees (default: 20)
--max-depth         Maximum tree depth (default: 6)
--export-format     Export format: default, legacy (default: legacy)
--verbose, -v       Enable verbose output
--quiet, -q         Suppress output
```

### 2. Train
Train a model with custom configuration.

```bash
python rf_cli.py train --data <data_source> [options]

# Options:
--data, -d          Path to dataset file or URL (required)
--features, -f      Comma-separated feature columns
--targets, -t       Comma-separated target columns
--test-size         Test set size (default: 0.2)
--n-estimators      Number of trees (default: 20)
--max-depth         Maximum tree depth (default: 6)
--config, -c        Configuration file (YAML/JSON)
--output, -o        Output directory (default: rf_output)
--save-model        Save trained model to file
--verbose, -v       Enable verbose output
```

### 3. Export
Export a pre-trained model to HLS code.

```bash
python rf_cli.py export --model <model_file> [options]

# Options:
--model, -m         Path to trained model file (required)
--target            Export target: hls (default: hls)
--output, -o        Output directory (default: rf_export)
--export-format     Export format: default, legacy (default: legacy)
--jinja2            Use Jinja2 templates (default: True)
--verbose, -v       Enable verbose output
```

### 4. Create Config
Generate a configuration template file.

```bash
python rf_cli.py create-config [options]

# Options:
--template          Template type: default, energy, automotive (default: default)
--output, -o        Output config file (default: rf_config.yaml)
```

## Examples

### Salary Prediction
```bash
python rf_cli.py quick-start --data Salary_dataset.csv --features YearsExperience --targets Salary --n-estimators 50 --max-depth 8 --output salary_model --verbose
```

### Multi-target Energy Prediction
```bash
python rf_cli.py train --data energy_data.csv --features Temperature,Humidity,Occupancy --targets Power_Consumption,CO2_Emissions --n-estimators 100 --max-depth 10 --output energy_model
```

### Using Configuration File
```bash
# Create config template
python rf_cli.py create-config --output my_config.yaml

# Edit the config file, then use it
python rf_cli.py train --config my_config.yaml --data dataset.csv
```

### Export Pre-trained Model
```bash
python rf_cli.py export --model trained_model.pkl --output hls_code --export-format legacy
```

## Output Structure
After successful execution, the output directory contains:

```
my_project/
├── *.h              # Header files (rfr_common.h, rf_trees_array.h, etc.)
├── *.cpp            # Implementation files (myproj_axi.cpp, myproj_core.cpp, etc.)
├── build_hls.tcl    # Vivado HLS build script
├── CMakeLists.txt   # CMake configuration
├── Makefile         # Makefile for compilation
├── run_synthesis.sh # HLS synthesis script
├── rf_config.yaml   # Configuration used
├── rf_metrics.json  # Training metrics
└── rf_report.md     # Comprehensive project report
```

## HLS Synthesis
After code generation, run HLS synthesis:

```bash
cd my_project
./run_synthesis.sh
```

## Software Simulation
Test the generated code:

```bash
cd my_project
make
./rfr_tb
```

## Tips
- Use `--verbose` for detailed logging during development
- Use `--quiet` for clean output in scripts
- For large datasets, increase `--n-estimators` and `--max-depth`
- Use configuration files for reproducible experiments
- Check `rf_report.md` for project summary and usage instructions

