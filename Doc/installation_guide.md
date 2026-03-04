# RF Framework - Complete Installation & Usage Guide

## Installation

### 1. Project Structure

Create the following directory structure:

```
fastml_framework_rf/
├── rf_framework.py          # Main framework
├── rf_cli.py               # Command-line interface
├── templates/
│   ├── firmware/
│   │   ├── rfr_common.h.j2
│   │   ├── rf_trees_array.h.j2
│   │   ├── bitcast_utils.h.j2
│   │   ├── scaler_constants.h.j2
│   │   ├── myproj_axi.cpp.j2
│   │   ├── myproj_core.cpp.j2
│   │   └── model_predict.cpp.j2
│   └── test/
│       ├── X_test.h.j2
│       └── rfr_tb.cpp.j2
├── requirements.txt
└── README.md
```

### 2. Install Dependencies

Create `requirements.txt`:

```
numpy>=1.20.0
pandas>=1.3.0
scikit-learn>=1.0.0
jinja2>=3.0.0
pyyaml>=5.4.0
```

Install:

```bash
pip install -r requirements.txt
```

### 3. Create Template Files

Copy all template files from the "All Jinja2 Templates" artifact into the appropriate directories.

## Usage

### Quick Start Example

```bash
python rf_cli.py quick-start \
    --data https://raw.githubusercontent.com/AbuAli3/ee/main/alldata.csv \
    --features Hour,Day,Month,Occupancy,Rel_Hum,Wat_Tem,Room_Temp,Air_Flow_Rat,Air_Temp \
    --targets Elec_Cons,Therm_Eng_Cons,PMV \
    --export-format legacy \
    --output fastml_output \
    --jinja2 \
    --n-estimators 20 \
    --max-depth 6
```

### Expected Output

```
2025-10-05 22:40:00 - root - INFO - RF Quick Start
2025-10-05 22:40:00 - root - INFO - ========================================
2025-10-05 22:40:00 - root - INFO - Loading data from: https://raw.githubusercontent.com/AbuAli3/ee/main/alldata.csv
2025-10-05 22:40:00 - rf_framework - INFO - Dataset loaded successfully. Shape: (17320, 12)
2025-10-05 22:40:00 - rf_framework - INFO - Features: ['Hour', 'Day', 'Month', ...]
2025-10-05 22:40:00 - rf_framework - INFO - Targets: ['Elec_Cons', 'Therm_Eng_Cons', 'PMV']
2025-10-05 22:40:02 - rf_framework - INFO - Model trained successfully in 1.73 seconds
2025-10-05 22:40:02 - rf_framework - INFO - Generated rfr_common.h
2025-10-05 22:40:02 - rf_framework - INFO - Generated rf_trees_array.h
2025-10-05 22:40:02 - rf_framework - INFO - Generated bitcast_utils.h
2025-10-05 22:40:02 - rf_framework - INFO - Generated scaler_constants.h
2025-10-05 22:40:02 - rf_framework - INFO - Generated myproj_axi.cpp
2025-10-05 22:40:02 - rf_framework - INFO - Generated myproj_core.cpp
2025-10-05 22:40:02 - rf_framework - INFO - Generated model_predict.cpp
2025-10-05 22:40:02 - rf_framework - INFO - Generated X_test.h
2025-10-05 22:40:02 - rf_framework - INFO - Generated rfr_tb.cpp
2025-10-05 22:40:02 - root - INFO - Quick start completed!
2025-10-05 22:40:02 - root - INFO - Check results in: fastml_output
```

### Generated Files

After running, you'll find these files in your output directory:

```
fastml_output/
├── rfr_common.h              # Common types and constants
├── rf_trees_array.h          # Tree structure definitions
├── bitcast_utils.h           # Bit manipulation utilities
├── scaler_constants.h        # MinMax scaler constants
├── myproj_axi.cpp           # AXI stream interface
├── myproj_core.cpp          # Core prediction logic
├── model_predict.cpp        # Tree data definitions
├── X_test.h                 # Test data
├── rfr_tb.cpp               # Testbench
├── X_test.npy               # Numpy test data
├── Y_test.npy               # Numpy test labels
├── Y_pred.npy               # Numpy predictions
├── scaler_x.pkl             # Input scaler
├── scaler_y.pkl             # Output scaler
├── rf_config.yaml           # Configuration
├── rf_metrics.json          # Training metrics
└── rf_report.md             # Detailed report
```

## Command-Line Options

### train

Train a model:

```bash
python rf_cli.py train \
    --data dataset.csv \
    --features f1,f2,f3 \
    --targets t1,t2 \
    --n-estimators 20 \
    --max-depth 6 \
    --output training_output \
    --save-model model.pkl
```

### export

Export a trained model:

```bash
python rf_cli.py export \
    --model model.pkl \
    --output export_output \
    --export-format legacy \
    --jinja2
```

### quick-start

All-in-one training and export:

```bash
python rf_cli.py quick-start \
    --data dataset.csv \
    --features f1,f2,f3 \
    --targets t1,t2 \
    --output quickstart_output \
    --jinja2
```

### create-config

Create a configuration template:

```bash
python rf_cli.py create-config \
    --template energy \
    --output my_config.yaml
```

## Python API Usage

```python
from rf_framework import RFFramework

# Create framework
framework = RFFramework()

# Configure
framework.config.config['export']['format'] = 'legacy'
framework.config.config['model']['n_estimators'] = 20
framework.config.config['model']['max_depth'] = 6

# Load data
data_url = "https://raw.githubusercontent.com/AbuAli3/ee/main/alldata.csv"
feature_cols = ['Hour', 'Day', 'Month', 'Occupancy', 'Rel_Hum', 
                'Wat_Tem', 'Room_Temp', 'Air_Flow_Rat', 'Air_Temp']
target_cols = ['Elec_Cons', 'Therm_Eng_Cons', 'PMV']

framework.load_data(data_url, feature_cols, target_cols)

# Train
metrics = framework.train()
print(f"Training metrics: {metrics}")

# Export with Jinja2
generated_files = framework.export_to_hls_j2("output_dir")
print(f"Generated: {list(generated_files.keys())}")

# Generate report
framework.generate_report()
```

## Troubleshooting

### Template Not Found Error

**Error**: `jinja2.exceptions.TemplateNotFound`

**Solution**: Ensure templates directory exists with correct structure:
```bash
mkdir -p templates/firmware templates/test
```

### 'builtin_function_or_method' object is not iterable

**Error**: This error in template rendering

**Solution**: Make sure you're using the updated `rf_framework.py` with the fixed `_extract_tree_data()` method that uses list comprehensions:

```python
return {
    'features': [int(x) for x in features],
    'thresholds': [float(x) for x in thresholds],
    # ... etc
}
```

### Import Error

**Error**: `ImportError: No module named 'rf_framework'`

**Solution**: Run from the correct directory or add to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/fastml_framework_rf"
```

## Key Changes from Original

1. **Fixed Jinja2 Data Types**: All numpy arrays properly converted to Python lists
2. **Simplified Code Generator**: Single `_extract_tree_data()` method
3. **Better Error Handling**: Detailed logging and traceback on failures
4. **Template Format**: Using Jinja2's built-in `format` filter for floats
5. **Robust Conversion**: Explicit type conversion using list comprehensions

## Next Steps

1. Verify all generated files are created successfully
2. Check logs for any warnings or errors
3. Review generated C++ code for correctness
4. Test with Vivado HLS if available
5. Modify templates as needed for your specific requirements

## Support

If you encounter issues:

1. Check that all template files are in place
2. Verify Python dependencies are installed
3. Look for detailed error messages in logs
4. Check that data URLs are accessible
5. Ensure correct column names for features/targets
