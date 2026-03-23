# Multi-Experiment RO-Crate Implementation - Summary

## What Was Updated

### 1. Core Builder (`src/rocrate_builder.py`)

**Added Support For:**
- Multiple experiments in a single RO-Crate
- Experiment-specific IDs for all entities
- Namespaced equipment and instrument references
- Organized file paths by experiment

**Key Changes:**
- `build_crate()`: Detects and processes `experiments` list
- `_add_dexpi()`: Accepts optional `experiment_id` parameter
- `_add_experimental_parameters()`: Returns entity, supports experiment IDs
- `_add_analytical_file()`: Organizes files under `data/{exp_id}/raw/` or `data/{exp_id}/processed/`
- `_add_engineering_asset()`: Organizes assets under `data/{exp_id}/engineering/`

**Backward Compatible:**
- Still supports single-experiment mode (legacy)
- Falls back to original behavior when no `experiments` list provided

### 2. Interactive Notebook (`opsee_workflow.ipynb`)

**New Features:**
- Mode selector: Single vs. Multiple Experiments
- Experiment ID and name input fields
- Current experiment tracking
- "Add Experiment to Crate" button
- "Reset Current Experiment" button
- Enhanced review showing all experiments

**Updated Sections:**
- General metadata: Added mode selection
- DEXPI loading: Mode-aware storage
- Parameters: Mode-aware storage
- Data files: Mode-aware storage and refresh
- Engineering assets: Mode-aware storage and refresh
- Review: Shows all experiments with details
- Export: Handles both modes

### 3. Documentation

**New Files:**
- `docs/MULTI_EXPERIMENT_GUIDE.md`: Complete guide with examples
- `examples/temperature_optimization/README.md`: Concrete use case

**Updated Files:**
- `README.md`: Added multi-experiment features and workflow

## RO-Crate Structure

### Single Experiment (Original)
```
rocrate/
├── ro-crate-metadata.json
├── data/
│   ├── engineering/
│   │   └── setup.dexpi.xml
│   ├── raw/
│   │   └── data.csv
│   └── processed/
│       └── results.csv
```

### Multiple Experiments (New)
```
rocrate/
├── ro-crate-metadata.json
├── data/
│   ├── engineering/
│   │   ├── exp_1_setup.dexpi.xml
│   │   └── exp_2_setup.dexpi.xml
│   ├── exp_1/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── engineering/
│   └── exp_2/
│       ├── raw/
│       ├── processed/
│       └── engineering/
```

## Metadata Organization

### Entity IDs

**Single Experiment:**
- `#experiment`
- `#equipment-R-101`
- `#instrument-GC-001`

**Multiple Experiments:**
- `#experiment-exp_1`
- `#experiment-exp_2`
- `#equipment-exp_1/R-101`
- `#equipment-exp_2/R-101`
- `#instrument-exp_1/GC-001`
- `#instrument-exp_2/GC-001`

### Relationships

The root dataset uses `hasPart` to link all experiments:

```json
{
  "@id": "./",
  "@type": "Dataset",
  "hasPart": [
    {"@id": "#experiment-exp_1"},
    {"@id": "#experiment-exp_2"}
  ]
}
```

Each experiment entity contains its conditions and links to its specific equipment/instruments.

## Use Cases

### Perfect For Multi-Experiment:
- Parameter studies (temperature, pressure, pH variations)
- Optimization experiments (baseline vs. modifications)
- Time series (sequential runs)
- Equipment comparisons (different configurations)
- Replication studies (same conditions, different batches)

### Better As Separate Crates:
- Unrelated experiments
- Different research projects
- Different research groups
- Very large datasets (>10GB per experiment)

## Workflow Example

```python
# 1. Set mode
w_mode.value = 'multi'

# 2. For each experiment:
for exp in experiments:
    # Set ID and name
    w_exp_id.value = exp['id']
    w_exp_name.value = exp['name']
    
    # Load DEXPI and parameters
    load_dexpi(exp['dexpi_path'])
    load_params(exp['params_path'])
    
    # Add data files
    for file in exp['data_files']:
        add_data_file(file)
    
    # Add to crate
    add_experiment_to_crate()
    reset_current_experiment()

# 3. Export
export_crate()
```

## Key Implementation Details

### Namespace Prefixing
- Equipment: `#equipment-{exp_id}/{tag_name}`
- Instruments: `#instrument-{exp_id}/{tag_name}`
- Experiments: `#experiment-{exp_id}`

### File Path Organization
- DEXPI: `data/engineering/{exp_id}_filename.xml`
- Raw data: `data/{exp_id}/raw/filename.csv`
- Processed: `data/{exp_id}/processed/filename.csv`
- Assets: `data/{exp_id}/engineering/filename.step`

### Entity Linking
Each data file links to its experiment-specific instrument:
```python
data_file['instrument'] = f"#instrument-{exp_id}/GC-001"
data_file['wasGeneratedBy'] = f"#instrument-{exp_id}/GC-001"
```

## Migration Path

Existing single-experiment notebooks continue to work without changes. To migrate:

1. Keep existing code as-is (single mode)
2. Or wrap in multi-experiment structure:
   ```python
   crate_data = {
       'general': {...},
       'authors': [...],
       'experiments': [
           {
               'id': 'exp_1',
               'dexpi': {...},
               'experimental_parameters': {...},
               'analytical_files': [...],
               'engineering_assets': [...]
           }
       ]
   }
   ```

## Testing Checklist

- [ ] Single experiment mode still works
- [ ] Multiple experiments can be added
- [ ] Each experiment has isolated paths
- [ ] Equipment/instrument IDs are namespaced
- [ ] Review shows all experiments
- [ ] Export creates correct structure
- [ ] Metadata validates correctly
- [ ] Links between entities are correct
- [ ] DEXPI files are properly named
- [ ] Data files are in correct subdirectories

## Next Development Steps

Potential enhancements:
1. **Batch import**: Load multiple experiments from config file
2. **Experiment comparison**: Visual diff of parameters
3. **Template experiments**: Clone and modify
4. **Experiment groups**: Hierarchical organization
5. **Selective export**: Export subset of experiments
6. **Merge crates**: Combine separate single-experiment crates

## Documentation Links

- Multi-Experiment Guide: `docs/MULTI_EXPERIMENT_GUIDE.md`
- Temperature Optimization Example: `examples/temperature_optimization/README.md`
- RO-Crate Profile: `docs/PROFILE.md`
- Main Workflow: `docs/WORKFLOW.md`
