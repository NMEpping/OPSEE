# Multi-Experiment Example: Temperature Optimization Study

This directory contains an example of packaging multiple experiments in a single RO-Crate.

## Study Overview

**Objective**: Optimize n-butanol production temperature in a CSTR reactor

**Experiments**:
1. **Baseline (35°C)**: Standard operating conditions
2. **High Temperature (40°C)**: Test increased metabolic activity
3. **Low Temperature (30°C)**: Test reduced metabolic stress

## Setup

All three experiments use the same equipment setup (DEXPI file), but with different operating parameters.

### Equipment (Shared)
- CSTR Reactor (R-101): 5L volume
- Gas Chromatograph (GC-001): For butanol analysis
- Temperature Controller (TIC-101)
- pH Controller (PIC-101)

### Variable Parameters
| Experiment | Temperature | Duration | Agitation |
|------------|-------------|----------|-----------|
| Baseline   | 35°C        | 48h      | 200 rpm   |
| High Temp  | 40°C        | 48h      | 200 rpm   |
| Low Temp   | 30°C        | 48h      | 200 rpm   |

## File Organization

```
temperature_optimization_study/
├── dexpi/
│   └── reactor_setup.xml              # Shared DEXPI for all experiments
├── parameters/
│   ├── exp1_baseline_35C.yaml
│   ├── exp2_high_temp_40C.yaml
│   └── exp3_low_temp_30C.yaml
├── data/
│   ├── exp1_baseline/
│   │   ├── gc_sample_001.csv
│   │   ├── gc_sample_002.csv
│   │   ├── temperature_log.csv
│   │   └── ph_log.csv
│   ├── exp2_high_temp/
│   │   ├── gc_sample_003.csv
│   │   ├── gc_sample_004.csv
│   │   ├── temperature_log.csv
│   │   └── ph_log.csv
│   └── exp3_low_temp/
│       ├── gc_sample_005.csv
│       ├── gc_sample_006.csv
│       ├── temperature_log.csv
│       └── ph_log.csv
└── README.md                          # This file
```

## Workflow Steps

### 1. General Metadata

```python
# In the notebook
w_mode.value = 'multi'  # Select multi-experiment mode

# Fill in general information
w_name.value = "Temperature Optimization Study - n-Butanol Production"
w_description.value = "Comparative study testing three different fermentation temperatures"
w_keywords.value = "n-butanol, fermentation, temperature optimization, CSTR"
w_license.value = "CC-BY-4.0"
```

### 2. Configure Experiment 1 (Baseline)

```python
# Experiment identification
w_exp_id.value = "exp1_baseline"
w_exp_name.value = "Baseline Experiment - 35°C"

# Load DEXPI (same for all)
w_dexpi_path.value = "dexpi/reactor_setup.xml"
# Click "Load DEXPI"

# Load parameters
w_params_path.value = "parameters/exp1_baseline_35C.yaml"
# Click "Load Parameters"

# Add analytical data files
# File 1:
w_data_path.value = "data/exp1_baseline/gc_sample_001.csv"
w_instrument_select.value = "GC-001"
w_data_type.value = "RawData"
w_data_description.value = "GC analysis at t=24h, sample 1"
# Click "Add Data File"

# File 2:
w_data_path.value = "data/exp1_baseline/gc_sample_002.csv"
w_instrument_select.value = "GC-001"
w_data_type.value = "RawData"
w_data_description.value = "GC analysis at t=48h, sample 2"
# Click "Add Data File"

# File 3:
w_data_path.value = "data/exp1_baseline/temperature_log.csv"
w_instrument_select.value = "TIC-101"
w_data_type.value = "RawData"
w_data_description.value = "Continuous temperature monitoring"
# Click "Add Data File"

# File 4:
w_data_path.value = "data/exp1_baseline/ph_log.csv"
w_instrument_select.value = "PIC-101"
w_data_type.value = "RawData"
w_data_description.value = "Continuous pH monitoring"
# Click "Add Data File"

# Finalize experiment 1
# Click "Add Experiment to Crate"
```

### 3. Configure Experiment 2 (High Temperature)

```python
# Reset for next experiment
# Click "Reset Current Experiment"

# Experiment identification
w_exp_id.value = "exp2_high_temp"
w_exp_name.value = "High Temperature - 40°C"

# Load same DEXPI
w_dexpi_path.value = "dexpi/reactor_setup.xml"
# Click "Load DEXPI"

# Load different parameters
w_params_path.value = "parameters/exp2_high_temp_40C.yaml"
# Click "Load Parameters"

# Add data files for experiment 2
w_data_path.value = "data/exp2_high_temp/gc_sample_003.csv"
w_instrument_select.value = "GC-001"
w_data_type.value = "RawData"
w_data_description.value = "GC analysis at t=24h, sample 3"
# Click "Add Data File"
# ... (repeat for other files)

# Finalize experiment 2
# Click "Add Experiment to Crate"
```

### 4. Configure Experiment 3 (Low Temperature)

```python
# Reset for next experiment
# Click "Reset Current Experiment"

# Experiment identification
w_exp_id.value = "exp3_low_temp"
w_exp_name.value = "Low Temperature - 30°C"

# Load same DEXPI
w_dexpi_path.value = "dexpi/reactor_setup.xml"
# Click "Load DEXPI"

# Load different parameters
w_params_path.value = "parameters/exp3_low_temp_30C.yaml"
# Click "Load Parameters"

# Add data files for experiment 3
# ... (similar to experiments 1 and 2)

# Finalize experiment 3
# Click "Add Experiment to Crate"
```

### 5. Review and Export

```python
# Review all experiments
# Click "Review Metadata"
# Output shows:
# - 3 experiments configured
# - Each with 4 data files
# - All sharing the same DEXPI

# Export
w_output_dir.value = "output/temperature_optimization_rocrate"
# Click "Export RO-Crate"
```

## Expected Output

### Directory Structure

```
output/temperature_optimization_rocrate/
├── ro-crate-metadata.json
├── ro-crate-preview.html
└── data/
    ├── engineering/
    │   ├── exp1_baseline_reactor_setup.xml
    │   ├── exp2_high_temp_reactor_setup.xml
    │   └── exp3_low_temp_reactor_setup.xml
    ├── exp1_baseline/
    │   └── raw/
    │       ├── gc_sample_001.csv
    │       ├── gc_sample_002.csv
    │       ├── temperature_log.csv
    │       └── ph_log.csv
    ├── exp2_high_temp/
    │   └── raw/
    │       └── ...
    └── exp3_low_temp/
        └── raw/
            └── ...
```

### Metadata Entities

The `ro-crate-metadata.json` will contain:

1. **Root Dataset**
   - Name: "Temperature Optimization Study..."
   - `hasPart`: Links to all 3 experiments

2. **Experiment Entities** (3x)
   - `#experiment-exp1_baseline`
   - `#experiment-exp2_high_temp`
   - `#experiment-exp3_low_temp`
   - Each with unique parameters

3. **DEXPI Files** (3x, but same content)
   - `exp1_baseline_reactor_setup.xml`
   - `exp2_high_temp_reactor_setup.xml`
   - `exp3_low_temp_reactor_setup.xml`

4. **Equipment Entities** (per experiment)
   - `#equipment-exp1_baseline/R-101`
   - `#equipment-exp2_high_temp/R-101`
   - `#equipment-exp3_low_temp/R-101`

5. **Instrument Entities** (per experiment)
   - `#instrument-exp1_baseline/GC-001`
   - `#instrument-exp2_high_temp/GC-001`
   - `#instrument-exp3_low_temp/GC-001`

6. **Data Files** (12 total)
   - Organized under respective experiment paths
   - Linked to experiment-specific instruments

## Key Benefits

✅ **Single Package**: All related experiments in one RO-Crate  
✅ **Easy Comparison**: Clear parameter differences documented  
✅ **Complete Context**: Experimental design is explicit  
✅ **Reproducible**: All conditions and data together  
✅ **Efficient**: Shared DEXPI referenced, not duplicated in metadata logic  

## Analysis Possibilities

With this structure, you can:

1. **Compare results** across temperatures
2. **Identify optimal conditions** from combined data
3. **Reproduce** any individual experiment
4. **Trace provenance** from raw data to conclusions
5. **Share** complete study as one artifact

## Notes

- DEXPI file is physically copied for each experiment but references same equipment
- Each experiment has isolated data paths preventing conflicts
- Experiment IDs are used throughout for clear separation
- Parameters are explicitly documented in YAML files
- All metadata relationships are preserved

## Next Steps

After creating the RO-Crate:

1. **Validate**: Check `ro-crate-metadata.json` structure
2. **Review**: Open `ro-crate-preview.html` in browser
3. **Analyze**: Load data files for comparative analysis
4. **Share**: Publish to repository (Zenodo, institutional repo)
5. **Cite**: Generate citation from metadata
