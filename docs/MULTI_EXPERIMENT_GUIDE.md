# Multi-Experiment RO-Crate Guide

This guide explains how to create RO-Crates containing multiple experiments with different processing parameters or DEXPI files.

## Overview

OPSEE now supports two modes for creating RO-Crates:

1. **Single Experiment Mode**: Traditional approach with one experiment per crate
2. **Multiple Experiments Mode**: Package multiple related experiments in a single crate

## When to Use Multi-Experiment Mode

Use multi-experiment mode when you have:

- **Parameter variations**: Same setup, different operating conditions (temperature, pressure, pH)
- **Time series experiments**: Sequential experiments on the same system
- **Process optimization studies**: Testing different configurations
- **Comparative studies**: Baseline vs. modified conditions
- **DEXPI variations**: Slightly modified equipment configurations

## Structure

### Single RO-Crate with Multiple Experiments

```
multi_experiment_rocrate/
├── ro-crate-metadata.json          # Combined metadata for all experiments
├── data/
│   ├── engineering/
│   │   ├── exp_1_setup.dexpi.xml   # DEXPI for experiment 1
│   │   ├── exp_2_setup.dexpi.xml   # DEXPI for experiment 2 (modified)
│   │   └── exp_3_setup.dexpi.xml   # DEXPI for experiment 3
│   ├── exp_1/                       # Experiment 1 data
│   │   ├── raw/
│   │   │   ├── gc_data_001.csv
│   │   │   └── temperature_log.csv
│   │   ├── processed/
│   │   │   └── calibrated_results.csv
│   │   └── engineering/
│   │       └── reactor_photo.jpg
│   ├── exp_2/                       # Experiment 2 data
│   │   ├── raw/
│   │   └── processed/
│   └── exp_3/                       # Experiment 3 data
│       ├── raw/
│       └── processed/
└── parameters/
    ├── exp_1_params.yaml
    ├── exp_2_params.yaml
    └── exp_3_params.yaml
```

## Workflow in Jupyter Notebook

### Step 1: Select Mode

```python
# In the notebook, select "Multiple Experiments" mode
w_mode.value = 'multi'
```

### Step 2: Configure First Experiment

1. **Set Experiment ID**: `exp_1` (or descriptive name like `baseline`)
2. **Set Experiment Name**: "Baseline Experiment - 35°C"
3. **Load DEXPI file**: `data/engineering/baseline_setup.xml`
4. **Load parameters**: `parameters/baseline_params.yaml`
5. **Add analytical files**: Link data files to instruments
6. **Add engineering assets**: Link CAD files to equipment
7. **Click "Add Experiment to Crate"**

### Step 3: Configure Additional Experiments

For each subsequent experiment:

1. **Click "Reset Current Experiment"**
2. **Update Experiment ID**: `exp_2`, `exp_3`, etc.
3. **Update Experiment Name**: Descriptive name
4. **Load new DEXPI** (if equipment changed) or reuse same file
5. **Load new parameters** (different conditions)
6. **Add data files** for this experiment
7. **Add assets** for this experiment
8. **Click "Add Experiment to Crate"**

### Step 4: Review and Export

1. Click **"Review Metadata"** to see all experiments
2. Set output directory
3. Click **"Export RO-Crate"**

## Example Use Case: Temperature Optimization

### Scenario
Testing n-butanol production at three different temperatures:

- **Experiment 1**: Baseline at 35°C
- **Experiment 2**: Increased to 40°C  
- **Experiment 3**: Reduced to 30°C

Same equipment, same DEXPI, different parameters.

### Implementation

#### Experiment 1: Baseline
```yaml
# parameters/exp1_35C.yaml
experiment:
  title: "n-Butanol Production - Baseline 35°C"
  description: "Baseline experiment at optimal temperature"
  
conditions:
  temperature:
    value: 35
    unit: "°C"
  # ... other conditions
```

#### Experiment 2: Higher Temperature
```yaml
# parameters/exp2_40C.yaml
experiment:
  title: "n-Butanol Production - 40°C"
  description: "Testing increased temperature effect"
  
conditions:
  temperature:
    value: 40
    unit: "°C"
  # ... other conditions (same as baseline)
```

#### Experiment 3: Lower Temperature
```yaml
# parameters/exp3_30C.yaml
experiment:
  title: "n-Butanol Production - 30°C"
  description: "Testing reduced temperature effect"
  
conditions:
  temperature:
    value: 30
    unit: "°C"
  # ... other conditions (same as baseline)
```

### Data Organization
```
data/
├── engineering/
│   └── reactor_setup.dexpi.xml      # Same for all 3 experiments
├── exp1_35C/
│   └── raw/
│       ├── gc_sample_001.csv
│       └── gc_sample_002.csv
├── exp2_40C/
│   └── raw/
│       ├── gc_sample_003.csv
│       └── gc_sample_004.csv
└── exp3_30C/
    └── raw/
        ├── gc_sample_005.csv
        └── gc_sample_006.csv
```

## Example Use Case: Modified Equipment

### Scenario
Testing two reactor configurations:

- **Experiment 1**: Standard stirrer configuration
- **Experiment 2**: Modified stirrer with baffles

Different DEXPI files (equipment modification), similar parameters.

### Implementation

```
data/
├── engineering/
│   ├── standard_config.dexpi.xml    # Original equipment
│   └── modified_config.dexpi.xml    # Modified with baffles
├── exp1_standard/
│   └── raw/
└── exp2_modified/
    └── raw/
```

Load different DEXPI files for each experiment in the notebook.

## Metadata Structure

The resulting `ro-crate-metadata.json` will contain:

```json
{
  "@graph": [
    {
      "@id": "./",
      "@type": "Dataset",
      "name": "Temperature Optimization Study",
      "hasPart": [
        {"@id": "#experiment-exp1_35C"},
        {"@id": "#experiment-exp2_40C"},
        {"@id": "#experiment-exp3_30C"}
      ]
    },
    {
      "@id": "#experiment-exp1_35C",
      "@type": "ChemicalExperiment",
      "name": "n-Butanol Production - Baseline 35°C",
      "experimentalConditions": { ... }
    },
    {
      "@id": "data/engineering/exp1_35C_reactor_setup.dexpi.xml",
      "@type": ["File", "SoftwareSourceCode"],
      "name": "Process P&ID (DEXPI) - exp1_35C"
    },
    {
      "@id": "#equipment-exp1_35C/R-101",
      "@type": "ProcessEquipment",
      "isDefinedIn": {"@id": "data/engineering/exp1_35C_reactor_setup.dexpi.xml"}
    }
  ]
}
```

Each experiment has:
- Unique experiment entity (`#experiment-exp_id`)
- Unique equipment references (`#equipment-exp_id/tag`)
- Unique instrument references (`#instrument-exp_id/tag`)
- Separate data file paths (`data/exp_id/raw/...`)

## Best Practices

### Experiment IDs
- Use descriptive IDs: `baseline`, `high_temp`, `modified_stirrer`
- Or systematic: `exp_1`, `exp_2`, `exp_3`
- Keep IDs short and filesystem-safe (no spaces, special chars)

### DEXPI File Reuse
- **Same equipment**: Reuse the same DEXPI file for all experiments
- **Modified equipment**: Create separate DEXPI files
- **Different instruments only**: Still use same DEXPI if structure unchanged

### Parameter Files
- Create one YAML file per experiment
- Use consistent structure across all files
- Clearly document what changed between experiments

### Data Files
- Organize by experiment ID
- Keep consistent folder structure (raw/, processed/)
- Use clear naming conventions that include experiment context

### Documentation
- Add clear experiment names and descriptions
- Document what varies between experiments
- Explain rationale for parameter choices

## Advantages of Multi-Experiment Crates

✅ **Comparative analysis**: All related experiments in one package  
✅ **Context preservation**: Relationships between experiments are explicit  
✅ **Reduced redundancy**: Shared equipment/DEXPI referenced once  
✅ **Easier distribution**: One crate contains complete study  
✅ **Better provenance**: Clear experimental design and variations  

## Limitations

⚠️ **Size**: Very large studies might create unwieldy crates  
⚠️ **Independence**: Experiments that aren't related should be separate crates  
⚠️ **Updates**: Modifying one experiment requires re-exporting entire crate  

## Migration from Single-Experiment Crates

If you have existing single-experiment crates and want to combine them:

1. Create a new multi-experiment crate
2. For each existing crate:
   - Import the DEXPI file
   - Import the parameter file
   - Copy data files to `exp_N/` subdirectories
   - Add experiment with unique ID
3. Export combined crate

## See Also

- [Main Workflow Documentation](WORKFLOW.md)
- [DEXPI Mapping Guide](DEXPI_MAPPING.md)
- [RO-Crate Profile Specification](PROFILE.md)
