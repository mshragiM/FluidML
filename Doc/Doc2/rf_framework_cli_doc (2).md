# RF Framework CLI Documentation

"""
  ███████╗ █████╗ ███████╗████████╗    ███╗   ███╗██╗     
  ██╔════╝██╔══██╗██╔════╝╚══██╔══╝    ████╗ ████║██║     
  █████╗  ███████║███████╗   ██║       ██╔████╔██║██║     
  ██╔══╝  ██╔══██║╚════██║   ██║       ██║╚██╔╝██║██║     
  ██║     ██║  ██║███████║   ██║       ██║ ╚═╝ ██║███████╗
  ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝       ╚═╝     ╚═╝╚══════╝
                                                            
                        By Mohammed Ali
"""


## Overview
RF Framework is a production-ready machine learning framework that trains Random Forest models and generates optimized HLS C++ code for FPGA deployment with complete automation from dataset to synthesized IP.

© Mohammed Ali

## 🚀 What's New
- Auto-scaling integration - Features and targets automatically scaled
- Synthesis reporting - FPGA resource utilization and timing analysis
- Professional CLI - Beautiful interface with comprehensive help
- Multi-format export - Support for different HLS coding styles
- Template system - Jinja2-based code generation

## Installation
```bash
# Clone the repository
git clone <my-repo>
cd fastml_framework_rf

# Install dependencies
pip install -r requirements.txt
```

## Quick Start
```bash
# Complete workflow: data → model → HLS → synthesis → report
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
```bash
python rf_cli.py quick-start --data <data_source> [options]
```
Options:
- `--data, -d` Path to dataset file or URL (required)
- `--features, -f` Comma-separated feature columns
- `--targets, -t` Comma-separated target columns
- `--output, -o` Output directory (default: rf_output)
- `--n-estimators` Number of trees (default: 20)
- `--max-depth` Maximum tree depth (default: 6)
- `--test-size` Test set size (default: 0.2)
- `--scaler` Feature scaler: minmax, standard, robust (default: minmax)
- `--export-format` Export format: default, legacy (default: legacy)
- `--verbose, -v` Enable verbose output
- `--quiet, -q` Suppress output

### 2. Train 🎯
```bash
python rf_cli.py train --data <data_source> [options]
```
Options:
- `--data, -d` Path to dataset file or URL (required)
- `--features, -f` Comma-separated feature columns
- `--targets, -t` Comma-separated target columns
- `--test-size` Test set size (default: 0.2)
- `--n-estimators` Number of trees (default: 20)
- `--max-depth` Maximum tree depth (default: 6)
- `--scaler` Feature scaler: minmax, standard, robust (default: minmax)
- `--config, -c` Configuration file (YAML/JSON)
- `--output, -o` Output directory (default: rf_output)
- `--save-model` Save trained model to file
- `--verbose, -v` Enable verbose output
- `--quiet, -q` Suppress output

### 3. Export 📤
```bash
python rf_cli.py export --model <model_file> [options]
```
Options:
- `--model, -m` Path to trained model file (required)
- `--target` Export target: hls (default: hls)
- `--output, -o` Output directory (default: rf_export)
- `--export-format` Export format: default, legacy (default: legacy)
- `--jinja2` Use Jinja2 templates (default: True)
- `--precision` Data precision: float, fixed, ap_fixed<16,6> (default: fixed)
- `--max-nodes` Maximum nodes per tree (default: 128)
- `--verbose, -v` Enable verbose output
- `--quiet, -q` Suppress output

### 4. Create Config ⚙️
```bash
python rf_cli.py create-config [options]
```
Options:
- `--template` Template type: default, energy, automotive (default: default)
- `--output, -o` Output config file (default: rf_config.yaml)
- `--verbose, -v` Enable verbose output

### 5. HLS Report 📊 NEW!
```bash
python rf_cli.py hls-report [options]
```
Options:
- `--project-dir, -p` Vivado HLS project directory (default: rf_output)
- `--verbose, -v` Enable verbose output
- `--quiet, -q` Suppress output

## 🏗️ Framework Architecture

### 1. Framework Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    RF Framework Architecture                 │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   Dataset   │    │  Training   │    │   Model     │
    │   Input     │───▶│   Pipeline  │───▶│   Export    │
    │  (CSV/URL)  │    │             │    │             │
    └─────────────┘    └─────────────┘    └─────────────┘
                            │                    │
                            ▼                    ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   Config    │    │  Metrics &  │    │  HLS Code   │
    │  Template   │◀───│   Reports   │◀───│ Generation  │
    │  Generator  │    │             │    │             │
    └─────────────┘    └─────────────┘    └─────────────┘
                                                    │
                                                    ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │ Synthesis   │    │   Vivado    │    │  FPGA IP    │
    │   Report    │◀───│    HLS      │◀───│   Core      │
    │  Analysis   │    │ Synthesis   │    │  Export     │
    └─────────────┘    └─────────────┘    └─────────────┘
```

### 2. End-to-End Workflow Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                End-to-End ML-to-FPGA Workflow               │
└─────────────────────────────────────────────────────────────┘

  ┌───────────┐     ┌───────────┐     ┌───────────┐
  │   Data    │     │  Model    │     │   HLS     │
  │  Loading  │────▶│ Training  │────▶│  Code Gen │
  └───────────┘     └───────────┘     └───────────┘
        │                │                    │
        ▼                ▼                    ▼
  ┌───────────┐     ┌───────────┐     ┌───────────┐
  │ Feature   │     │ Model     │     │ Optimized │
  │ Scaling   │     │ Evaluation│     │   C++     │
  └───────────┘     └───────────┘     └───────────┘
                                            │
                                            ▼
  ┌───────────┐     ┌───────────┐     ┌───────────┐
  │ Vivado    │     │  C/RTL    │     │  FPGA IP  │
  │ HLS       │────▶│ Co-Sim    │────▶│   Core    │
  │ Synthesis │     │           │     │           │
  └───────────┘     └───────────┘     └───────────┘
        │                                    │
        ▼                                    ▼
  ┌───────────┐                       ┌───────────┐
  │ Synthesis │                       │ Hardware  │
  │  Report   │                       │ Deployment│
  └───────────┘                       └───────────┘
```

### 3. HLS Code Generation Pipeline
```
┌─────────────────────────────────────────────────────────────┐
│               HLS Code Generation Pipeline                  │
└─────────────────────────────────────────────────────────────┘

  ┌─────────────┐    Trained     ┌─────────────┐
  │  Random     │   Random      │  Tree Data   │
  │ Forest Model│   Forest      │  Extraction  │
  │             │ ────────────▶ │              │
  └─────────────┘               └─────────────┘
                                        │
                                        ▼
  ┌─────────────┐    Jinja2      ┌─────────────┐
  │  Template   │   Templates    │  HLS Code   │
  │   System    │ ────────────▶  │ Generation │
  │             │                │             │
  └─────────────┘                └─────────────┘
                                        │
                                        ▼
  ┌─────────────────────────────────────────────────┐
  │              Generated HLS Files                │
  ├─────────────────────────────────────────────────┤
  │  • rfr_common.h        - Common definitions     │
  │  • rf_trees_array.h    - Tree structures        │
  │  • myproj_axi.cpp      - AXI interface          │
  │  • myproj_core.cpp     - Core logic             │
  │  • model_predict.cpp   - Prediction engine      │
  │  • scaler_constants.h  - Scaling parameters     │
  │  • rfr_tb.cpp          - Testbench              │
  └─────────────────────────────────────────────────┘
```

### 4. CLI Command Structure
```
┌─────────────────────────────────────────────────────────────┐
│                   CLI Command Hierarchy                     │
└─────────────────────────────────────────────────────────────┘

                      rf_cli.py
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
  quick-start          train              export
 (Auto pipeline)   (Custom training)  (Model export)
      │                   │                   │
      ▼                   ▼                   ▼
 create-config        hls-report          --help
(Config templates) (Synthesis analysis) (All commands)
```

### 5. FPGA Resource Utilization Chart
```
┌─────────────────────────────────────────────────────────────┐
│              Typical FPGA Resource Utilization              │
└─────────────────────────────────────────────────────────────┘

 Resource    Used    Available    Utilization
┌──────────┬────────┬───────────┬─────────────────────────────┐
│ BRAM     │  126   │    280    │ ████████████████████ 45%    │
│ DSP      │    6   │    220    │ ██ 2%                       │
│ FF       │ 5,142  │  106,400  │ ████ 4%                     │
│ LUT      │ 3,492  │   53,200  │ ██████ 6%                   │
└──────────┴────────┴───────────┴─────────────────────────────┘

Performance Metrics:
 • Clock Frequency: 234 MHz (Target: 200 MHz) ✅
 • Timing Slack: 0.728 ns ✅
 • Latency: 51 cycles (0.255 μs) ⚡
 • Throughput: 29,663 inferences/sec 🚀

### 6. Complete Integration Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                  Framework Integration                      │
└─────────────────────────────────────────────────────────────┘

    Python ML World                    FPGA Hardware World
┌───────────────────────┐        ┌───────────────────────────┐
│                       │        │                           │
│  ┌─────────────────┐  │        │  ┌─────────────────────┐  │
│  │   Scikit-learn  │  │        │  │   AXI-Stream        │  │
│  │  Random Forest  │──┼────────┼──│    Interface        │  │
│  └─────────────────┘  │        │  └─────────────────────┘  │
│           │           │        │             │             │
│  ┌─────────────────┐  │        │  ┌─────────────────────┐  │
│  │  Data Scaling   │  │        │  │   Tree Traversal    │  │
│  │   (MinMax)      │──┼────────┼──│     Engine          │  │
│  └─────────────────┘  │        │  └─────────────────────┘  │
│           │           │        │             │             │
│  ┌─────────────────┐  │        │  ┌─────────────────────┐  │
│  │  Jinja2 Code    │  │        │  │   Fixed-Point       │  │
│  │   Generator     │──┼────────┼──│    Arithmetic       │  │
│  └─────────────────┘  │        │  └─────────────────────┘  │
│                       │        │                           │
└───────────────────────┘        └───────────────────────────┘
            │                                    │
            ▼                                    ▼
    ┌───────────────┐                    ┌───────────────┐
    │  Model.json   │                    │  FPGA.bit     │
    │  Config.yaml  │                    │   IP Core     │
    │  Report.md    │                    │   RTL Code    │
    └───────────────┘                    └───────────────┘


