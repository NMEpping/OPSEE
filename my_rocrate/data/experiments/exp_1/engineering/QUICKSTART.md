# OPSEE Quick Start Guide (v0.2)

## New in v0.2

- ✅ **uv package manager** for faster installation
- ✅ **pydexpi** integration for robust DEXPI parsing  
- ✅ **Simplified workflow**: One shared DEXPI file for all experiments
- ✅ **Support for 0 to many experiments** on the same setup
- ✅ No more single/multi-experiment mode distinction

## Installation

### Using uv (Recommended - Fast!)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install OPSEE
git clone https://github.com/yourusername/opsee.git
cd opsee
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Using pip (Alternative)

```bash
git clone https://github.com/yourusername/opsee.git
cd opsee
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Quick Workflow

### 1. Launch Notebook

```bash
jupyter notebook opsee_workflow.ipynb
```

### 2. Enter General Metadata

- Crate name: "My Experimental Study"
- Description, keywords, license, authors

### 3. Load Shared DEXPI File

- Path: `examples/C01V04-VER.EX01.xml`
- Click "Load DEXPI"
- ✅ Equipment and instruments are parsed with **pydexpi**

### 4. Configure Experiments (0 or more)

For each experiment:

**a) Set Experiment ID and Parameters**
- ID: `exp_1`, `exp_2`, etc.
- Load parameters YAML file
  
**b) Add Data Files**
- Link analytical files to instruments from shared DEXPI
- Specify data type (Raw/Processed/Calibration)
  
**c) Add Engineering Assets** (optional)
- Link CAD files, photos, drawings to equipment from shared DEXPI
  
**d) Finalize**
- Click "Add Experiment to Crate"
- Click "Reset for New Experiment" to add more
- Or click "Skip (No Experiments)" if documenting setup only

### 5. Review and Export

- Click "Review Metadata" to verify
- Set output directory
- Click "Export RO-Crate"
- ✅ Done!

## Output Structure

```
output_rocrate/
├── ro-crate-metadata.json        # All metadata
├── ro-crate-preview.html         # Human-readable view
└── data/
    ├── engineering/
    │   └── C01V04-VER.EX01.xml   # Shared DEXPI
    └── experiments/
        ├── exp_1/                 # Experiment 1 data
        │   ├── raw/
        │   │   └── gc_data_001.csv
        │   └── processed/
        │       └── results_001.csv
        └── exp_2/                 # Experiment 2 data
            ├── raw/
            └── processed/
```

## Key Concepts

### Shared Setup, Multiple Experiments

**One DEXPI File = One Experimental Setup**

The DEXPI P&ID file describes your physical experimental setup (equipment, instruments, piping). This stays the same across all your experiments.

**Multiple Experiments = Different Conditions**

Each experiment uses the same setup but with:
- Different operating parameters (temperature, pressure, pH, etc.)
- Different data files
- Different operating times
- Different sample points

**Example: Temperature Study**
```
Shared Setup (DEXPI):
  - CSTR Reactor (R-101)
  - GC (GC-001)
  - Temperature Controller (TIC-101)

Experiment 1: 35°C, 48h → data/experiments/exp1/
Experiment 2: 40°C, 48h → data/experiments/exp2/
Experiment 3: 30°C, 48h → data/experiments/exp3/
```

### When to Use 0 Experiments

Create a "setup-only" RO-Crate when:
- Documenting new experimental setups before use
- Sharing equipment configurations
- Planning future experiments
- Version control for setups

## Common Use Cases

### 1. Single Experiment

```python
# Just configure one experiment
w_exp_id.value = "baseline"
# ... add parameters and data files
# Click "Add Experiment to Crate"
# Click "Export"
```

### 2. Parameter Study (3 experiments)

```python
# Experiment 1: Baseline
w_exp_id.value = "baseline_35C"
# ... configure
# Add Experiment

# Reset

# Experiment 2: High temp
w_exp_id.value = "high_temp_40C"
# ... configure
# Add Experiment

# Reset

# Experiment 3: Low temp
w_exp_id.value = "low_temp_30C"
# ... configure
# Add Experiment

# Export
```

### 3. Setup Documentation Only

```python
# Load DEXPI
# Add general metadata
# Click "Skip (No Experiments)"
# Export
```

## pydexpi Integration

OPSEE now uses **pydexpi** for DEXPI parsing:

- ✅ Robust parsing of DEXPI 4.x standard
- ✅ Automatic extraction of equipment, instruments, and actuating systems
- ✅ Handles complex P&IDs with thousands of components
- ✅ Proper namespace handling

The parser extracts:
- **Equipment**: Reactors, vessels, pumps, heat exchangers
- **Instruments**: Actuating systems, measurement devices
- **Tag names**: Identifiers like R-101, GC-001, TIC-101
- **Attributes**: Component classes, descriptions, properties

## File Organization

All experiment data is organized by experiment ID:

```
data/experiments/{experiment_id}/
├── raw/              # Raw data files
├── processed/        # Analyzed/calibrated data
└── engineering/      # Experiment-specific assets
```

The shared DEXPI file goes in:
```
data/engineering/     # Shared setup files
```

## Metadata Structure

### Shared Equipment and Instruments

All equipment and instruments from DEXPI are referenced by **all experiments**:

```json
{
  "@id": "#equipment-R-101",
  "@type": "ProcessEquipment",
  "identifier": "R-101",
  "isDefinedIn": {"@id": "data/engineering/setup.xml"}
}
```

### Experiment Entities

Each experiment gets its own entity:

```json
{
  "@id": "#experiment-exp_1",
  "@type": "ChemicalExperiment",
  "name": "Baseline at 35°C",
  "experimentalConditions": {...}
}
```

### Data File Links

Data files link to the **shared instruments**:

```json
{
  "@id": "data/experiments/exp_1/raw/gc_data.csv",
  "@type": ["File", "AnalyticalData"],
  "instrument": {"@id": "#instrument-GC-001"},
  "wasGeneratedBy": {"@id": "#instrument-GC-001"}
}
```

## Troubleshooting

### DEXPI File Not Loading

```
✗ Error loading DEXPI: ...
```

**Solution:**
- Check file path is correct
- Verify DEXPI file is valid XML
- Try the example file: `examples/C01V04-VER.EX01.xml`
- Check pydexpi is installed: `uv pip list | grep pydexpi`

### No Equipment/Instruments Found

```
✓ DEXPI loaded
  Equipment items: 0
  Instruments: 0
```

**Solution:**
- DEXPI file may not contain expected elements
- Check if file follows DEXPI 4.x standard
- Verify XML structure manually

### Module Import Errors

```
ModuleNotFoundError: No module named 'pydexpi'
```

**Solution:**
```bash
source .venv/bin/activate  # Activate virtual environment
uv pip install pydexpi
```

## Tips & Best Practices

✅ **Use descriptive experiment IDs**: `baseline_35C` instead of `exp1`  
✅ **Document parameter changes**: Use YAML files for reproducibility  
✅ **Consistent file naming**: `{exp_id}_{instrument}_{sample}.csv`  
✅ **Load DEXPI first**: Before adding any experiments  
✅ **Review before export**: Check metadata is complete  
✅ **Test with example**: Use provided `C01V04-VER.EX01.xml` file first  

## Next Steps

- Read full documentation: [`docs/WORKFLOW.md`](docs/WORKFLOW.md)
- Explore DEXPI mapping: [`docs/DEXPI_MAPPING.md`](docs/DEXPI_MAPPING.md)
- Check example files: [`examples/`](examples/)
- Learn about RO-Crate profile: [`docs/PROFILE.md`](docs/PROFILE.md)

## Support

- GitHub Issues: Report bugs or request features
- Documentation: Check `docs/` folder
- Examples: See `examples/` for templates
