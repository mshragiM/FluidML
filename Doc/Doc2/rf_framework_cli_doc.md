# RF Framework CLI Documentation

## Overview
RF Framework is a production-ready machine learning framework that trains Random Forest models and generates optimized HLS C++ code for FPGA deployment with complete automation from dataset to synthesized IP.

### 🚀 What's New
- Auto-scaling integration - Features and targets automatically scaled
- Synthesis reporting - FPGA resource utilization and timing analysis
- Professional CLI - Beautiful interface with comprehensive help
- Multi-format export - Support for different HLS coding styles
- Template system - Jinja2-based code generation

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
# Complete workflow: data -> model -> HLS -> synthesis -> report
python rf_cli.py quick-start --data data.csv --features col1,col2 --targets target1,target2

# Real-world energy prediction example
python rf_cli.py quick-start \
  --data https://raw.githubusercontent.com/AbuAli3/ee/main/alldata.csv  \
  --features Occupancy,Rel_Hum,Room_Temp,Air_Flow_Rat,Air_Temp \
  --targets Elec_Cons,Therm_Eng_Cons,PMV \
  --output my_project \
  --verbose
```

## Commands

### 1. Quick Start 🚀
Fastest way from data to synthesized FPGA code.

```bash
python rf_cli.py quick-start --data <data_source> [options]

# Options:
--data, -d          Path to dataset file or URL (required)
--features, -f      Comma-separated feature columns
--targets, -t       Comma-separated target columns  
--output, -o        Output directory (default: rf_output)
--n-estimators      Number of trees (default: 20)
--max-depth         Maximum tree depth (default: 6)
--test-size         Test set size (default: 0.2)
--scaler            Feature scaler: minmax, standard, robust (default: minmax)
--export-format     Export format: default, legacy (default: legacy)
--verbose, -v       Enable verbose output
--quiet, -q         Suppress output
```

Example:
```bash
python rf_cli.py quick-start \
  --data dataset.csv \
  --features temp,pressure,humidity \
  --targets output1,output2 \
  --n-estimators 50 \
  --max-depth 8 \
  --scaler standard \
  --output my_model
```

### 2. Train 🎯
Train a model with full customization.

```bash
python rf_cli.py train --data <data_source> [options]

# Options:
--data, -d          Path to dataset file or URL (required)
--features, -f      Comma-separated feature columns
--targets, -t       Comma-separated target columns
--test-size         Test set size (default: 0.2)
--n-estimators      Number of trees (default: 20)
--max-depth         Maximum tree depth (default: 6)
--scaler            Feature scaler: minmax, standard, robust (default: minmax)
--config, -c        Configuration file (YAML/JSON)
--output, -o        Output directory (default: rf_output)
--save-model        Save trained model to file
--verbose, -v       Enable verbose output
--quiet, -q         Suppress output
```

### 3. Export 📤
Export pre-trained model to optimized HLS code.

```bash
python rf_cli.py export --model <model_file> [options]

# Options:
--model, -m         Path to trained model file (required)
--target            Export target: hls (default: hls)
--output, -o        Output directory (default: rf_export)
--export-format     Export format: default, legacy (default: legacy)
--jinja2            Use Jinja2 templates (default: True)
--precision         Data precision: float, fixed, ap_fixed<16,6> (default: fixed)
--max-nodes         Maximum nodes per tree (default: 128)
--verbose, -v       Enable verbose output
--quiet, -q         Suppress output
```

### 4. Create Config ⚙️
Generate configuration templates for reproducible experiments.

```bash
python rf_cli.py create-config [options]

# Options:
--template          Template type: default, energy, automotive (default: default)
--output, -o        Output config file (default: rf_config.yaml)
--verbose, -v       Enable verbose output
```

Examples:
```bash
python rf_cli.py create-config --template energy --output energy_config.yaml
python rf_cli.py create-config --template automotive --output auto_config.yaml
```

### 5. HLS Report 📊 NEW!
Analyze FPGA synthesis results and performance.

```bash
python rf_cli.py hls-report [options]

# Options:
--project-dir, -p   Vivado HLS project directory (default: rf_output)
--verbose, -v       Enable verbose output
--quiet, -q         Suppress output
```

Examples:
```bash
python rf_cli.py hls-report                        # Check default project
python rf_cli.py hls-report --project-dir my_proj  # Check specific project
```

## Output Structure
After successful execution:
```
my_project/
├── 📄 HLS Source Files
│   ├── rfr_common.h          # Common definitions and types
│   ├── rf_trees_array.h      # Tree data structures
│   ├── myproj_axi.cpp        # AXI-Stream interface
│   ├── myproj_core.cpp       # Core prediction logic
│   ├── model_predict.cpp     # Model implementation
│   ├── bitcast_utils.h       # Fixed-point utilities
│   └── scaler_constants.h    # Auto-generated scaling constants
├── 🧪 Test Files
│   ├── rfr_tb.cpp            # Testbench for simulation
│   └── X_test.h              # Test dataset
├── 🔧 Build Files
│   ├── rf_project.tcl        # Vivado HLS project script
│   ├── run_synthesis.sh      # Automated synthesis script
│   └── Makefile              # Software compilation
├── 📊 Analysis Files
│   ├── rf_config.yaml        # Complete configuration
│   ├── rf_metrics.json       # Training performance metrics
│   ├── rf_report.md          # Comprehensive project report
│   ├── X_test.npy            # Test features
│   ├── Y_test.npy            # Test targets
│   ├── Y_pred.npy            # Predictions
│   ├── scaler_x.pkl          # Feature scaler
│   └── scaler_y.pkl          # Target scaler
└── 🎯 Synthesis Results (after running synthesis)
    └── solution1/
        ├── syn/
        │   └── report/       # Utilization and timing reports
        ├── sim/              # Simulation results
        ├── impl/             # Implemented design
        └── csim/             # C simulation results
```

## HLS Synthesis Workflow
1. Generate HLS Code
```bash
python rf_cli.py quick-start --data dataset.csv --features f1,f2 --targets out
```
2. Run Synthesis
```bash
cd rf_output
vivado_hls -f rf_project.tcl
```
3. Analyze Results
```bash
python rf_cli.py hls-report --project-dir rf_output
```
4. Software Simulation
```bash
cd rf_output
make
./rfr_tb
```

## Tips & Best Practices
- Use `--precision fixed` for optimal resource usage
- Set `--max-depth 6-8` for balanced accuracy/size
- Choose `--n-estimators 20-50` for most applications
- Enable pipelining with `--export-format legacy`
- Use `--verbose` for detailed debugging information
- Run `hls-report` after synthesis to verify results

## Getting Help
```bash
python rf_cli.py -h
python rf_cli.py train -h
python rf_cli.py hls-report -h
python rf_cli.py --version
```

## Real-World Applications
- Energy Management - Building energy prediction
- Industrial IoT - Sensor data processing
- Financial Analytics - Risk assessment
- Automotive - Sensor fusion and control
- Healthcare - Medical device intelligence

# RF Framework CLI Documentation

© 2025 Mohammed Ali. All rights reserved.
