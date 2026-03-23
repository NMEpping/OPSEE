# OPSEE - Open Process Systems Engineering Environment

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![RO-Crate](https://img.shields.io/badge/RO--Crate-1.2-purple)](https://www.researchobject.org/ro-crate/)

**OPSEE** is a reproducible workflow for creating FAIR (Findable, Accessible, Interoperable, Reusable) RO-Crates that package chemical and bioprocess engineering experiments.

## Overview

OPSEE enables researchers to:
- **Package experimental datasets** with rich, machine-readable metadata
- **Link analytical data** to instruments and equipment defined in DEXPI P&ID files using **pydexpi**
- **Connect engineering assets** (CAD, models, geometry files) to process equipment
- **Support 0 to many experiments** on one experimental setup (single shared DEXPI file)
- **Generate RO-Crates** that comply with FAIR principles
- **Share reproducible research** with complete provenance information

## Quick Start

### Prerequisites

- Python 3.9 or later
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Jupyter Notebook/Lab
- Basic familiarity with JSON and YAML

### Installation with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/opsee.git
cd opsee

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Alternative Installation with pip

```bash
# Clone the repository
git clone https://github.com/yourusername/opsee.git
cd opsee

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Usage

1. **Launch the notebook**:
   ```bash
   jupyter notebook opsee_workflow.ipynb
   ```

2. **Follow the interactive workflow**:
   - **Select output directory** - Where your RO-Crate will be created
   - Enter general RO-Crate metadata (title, authors, description)
   - Upload or reference your DEXPI XML file (parsed with **pyDEXPI** from [process-intelligence-research](https://github.com/process-intelligence-research/pyDEXPI))
   - Add 0 or more experiments with their parameters (YAML format)
   - Link analytical data files to instruments (from shared DEXPI)
   - Link CAD/geometry files to equipment (from shared DEXPI)
   - Export the RO-Crate - **all files are copied** into the output directory

3. **Generated output** (self-contained RO-Crate):
   ```
   my_rocrate/
   ├── ro-crate-metadata.json      (all metadata)
   ├── ro-crate-preview.html       (human-readable view)
   └── data/                       (all copied files!)
       ├── engineering/
       │   └── setup.dexpi.xml     (copied DEXPI)
       └── experiments/
           ├── exp_1/
           │   ├── raw/            (copied data files)
           │   ├── processed/
           │   └── engineering/    (copied CAD/drawings)
           └── exp_2/
               └── ...
   ```
   
   ✅ **Fully portable** - can be moved, shared, or archived as a single package!

## Repository Structure

```
opsee/
├── README.md                      # This file
├── LICENSE                        # Apache 2.0 license
├── CONTRIBUTING.md                # Contribution guidelines
├── pyproject.toml                 # Project dependencies (uv/pip)
├── .gitignore                     # Git ignore patterns
├── ro-crate-metadata.json         # RO-Crate metadata (generated/example)
├── opsee_workflow.ipynb           # Main interactive notebook
├── src/                           # Supporting Python modules
│   ├── __init__.py
│   ├── rocrate_builder.py         # RO-Crate construction helpers
│   └── validators.py              # Validation functions
├── data/                          # Experimental data (example/workspace)
│   ├── raw/                       # Raw analytical data
│   │   └── .gitkeep
│   ├── processed/                 # Processed/derived data
│   │   └── .gitkeep
│   └── engineering/               # DEXPI and CAD files
│       └── .gitkeep
├── templates/                     # Template files
│   ├── experiment_parameters.yaml # Experimental metadata template
│   ├── example_dexpi.xml          # Example DEXPI P&ID file
│   └── profile_schema.json        # RO-Crate profile definition
├── docs/                          # Additional documentation
│   ├── WORKFLOW.md                # Detailed workflow guide
│   ├── DEXPI_MAPPING.md           # DEXPI-to-RO-Crate mapping guide
│   └── PROFILE.md                 # Profile specification
└── examples/                      # Example datasets (future)
    └── gc_calibration/            # GC calibration example
        └── README.md
```

## Key Features

### 1. Interactive Notebook Workflow
- **Widget-based interface** for users with limited programming experience
- **Step-by-step guidance** through metadata entry and file linking
- **Real-time validation** of RO-Crate structure

### 2. DEXPI Integration
- **Parse P&ID information** from DEXPI XML files
- **Extract equipment and instrument identifiers** for semantic linking
- **Map engineering assets** to process equipment components

### 3. RO-Crate Profile for Chemical Engineering
- **Specialized metadata schema** for chemical and bioprocess experiments
- **Analytical data provenance** tracking
- **Process equipment and instrumentation references**
- **Raw vs. processed data organization**

### 4. Validation and Quality Assurance
- **Schema validation** for RO-Crate metadata
- **DEXPI XML structure validation**
- **Link integrity checking** between files and equipment
- **Profile compliance verification**

## Workflow Overview

```
1. General Metadata Entry
   ├─ Crate name, description, keywords
   ├─ Authors, contributors, affiliations
   ├─ License, dates, version
   └─ Select mode: Single or Multiple Experiments

2. Process Setup Definition (per experiment)
   ├─ Set experiment ID and name
   ├─ Upload DEXPI XML file
   ├─ Enter experimental parameters (YAML)
   └─ Validate P&ID structure

3. Analytical Data Linking (per experiment)
   ├─ Add raw data files (GC, HPLC, etc.)
   ├─ Link to instruments in DEXPI
   └─ Specify data types and formats

4. Engineering Asset Linking (per experiment)
   ├─ Add CAD/geometry files
   ├─ Link to equipment in DEXPI
   └─ Document file relationships

5. Finalize Experiments (multi-experiment mode)
   ├─ Add current experiment to crate
   ├─ Reset for next experiment
   └─ Repeat steps 2-4 for additional experiments

6. Export and Validation
   ├─ Review all experiments
   ├─ Generate ro-crate-metadata.json
   ├─ Create HTML preview
   └─ Validate profile compliance
```

## Multi-Experiment Support

OPSEE supports packaging **multiple related experiments** in a single RO-Crate, ideal for:

- **Parameter studies**: Testing different temperatures, pressures, or pH values
- **Optimization studies**: Comparing baseline vs. modified conditions
- **Equipment variations**: Testing modified setups with different DEXPI files
- **Time series**: Sequential experiments on the same system

Each experiment maintains:
- Separate DEXPI file (or shared if equipment is identical)
- Independent experimental parameters
- Isolated data files organized by experiment ID
- Individual equipment and instrument references

See [`docs/MULTI_EXPERIMENT_GUIDE.md`](docs/MULTI_EXPERIMENT_GUIDE.md) for detailed examples.

## Example Use Cases

### Gas Chromatography Calibration
Link GC calibration curves and measurement files to the gas chromatograph component defined in the DEXPI P&ID:

```python
# Notebook cell example
add_analytical_file(
    file_path="data/raw/gc_calibration_20240315.csv",
    instrument_id="GC-001",  # From DEXPI
    data_type="CalibrationData",
    description="n-Butanol calibration curve"
)
```

### Reactor CAD Model
Connect a reactor 3D model to its P&ID representation:

```python
# Notebook cell example
add_engineering_asset(
    file_path="data/engineering/reactor_r101.step",
    equipment_id="R-101",  # From DEXPI
    asset_type="CADModel",
    description="CSTR reactor geometry"
)
```

## RO-Crate Profile

OPSEE implements a domain-specific RO-Crate profile for chemical and bioprocess engineering:

**Profile URI**: `https://w3id.org/opsee/ro-crate-profile/chemical-engineering/1.0`

**Key Entity Types**:
- `ChemicalExperiment` - Experiment-level metadata
- `ProcessEquipment` - Equipment from DEXPI
- `AnalyticalInstrument` - Analytical instruments from DEXPI
- `AnalyticalData` - Raw/processed analytical measurements
- `EngineeringAsset` - CAD models, technical drawings

See [`docs/PROFILE.md`](docs/PROFILE.md) for complete specification.

## DEXPI Mapping Strategy

OPSEE maps DEXPI XML components to RO-Crate entities using TagName and ID attributes:

| DEXPI Element | Attribute | RO-Crate Entity Type | Example |
|---------------|-----------|---------------------|---------|
| `Equipment` | `TagName` | `ProcessEquipment` | R-101 (Reactor) |
| `ActuatingSystem` | `TagName` | `AnalyticalInstrument` | GC-001 |
| `Nozzle` | `TagName` | `SamplingPoint` | SP-R101-01 |
| `PipingNetworkSegment` | `TagName` | `ProcessStream` | S-101 |

See [`docs/DEXPI_MAPPING.md`](docs/DEXPI_MAPPING.md) for detailed mapping rules.

## Python Stack

### Core Dependencies
- **rocrate** (>=0.14.0) - RO-Crate creation and manipulation
- **ipywidgets** (>=8.1.0) - Interactive notebook interface
- **lxml** (>=5.0.0) - DEXPI XML parsing
- **pyyaml** (>=6.0) - Experimental parameters handling
- **jsonschema** (>=4.20.0) - RO-Crate profile validation

### Optional Dependencies
- **jupyter** (>=1.0.0) - Notebook environment
- **pandas** (>=2.0.0) - Data file handling
- **ipyfilechooser** (>=0.6.0) - File selection widget

See [`requirements.txt`](requirements.txt) for complete list.

## Validation and Testing

### RO-Crate Validation
```bash
python -m src.validators validate_crate ro-crate-metadata.json
```

### DEXPI XML Validation
```bash
python -m src.validators validate_dexpi data/engineering/process_setup.xml
```

### Profile Compliance
```bash
python -m src.validators validate_profile ro-crate-metadata.json templates/profile_schema.json
```

## Roadmap

### Version 1.0 (Current)
- [x] Basic notebook workflow
- [x] DEXPI parsing and equipment extraction
- [x] RO-Crate generation with core metadata
- [x] File-to-equipment linking
- [x] Profile definition and validation

### Version 1.1 (Planned)
- [ ] Example GC calibration dataset
- [ ] HPLC data integration
- [ ] Batch process metadata
- [ ] Multi-experiment crates
- [ ] Enhanced validation with detailed error messages

### Version 2.0 (Future)
- [ ] Integration with electronic lab notebooks
- [ ] Automated DEXPI generation from CAD
- [ ] Real-time data acquisition support
- [ ] Cloud storage backends
- [ ] Web-based interface

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- Development setup
- Contribution workflow
- Testing guidelines
- Documentation standards

## Citation

If you use OPSEE in your research, please cite:

```bibtex
@software{opsee2026,
  title = {OPSEE: Open Process Systems Engineering Environment},
  author = {Schömig, Richard & Epping, Niklas-Maximilian},
  year = {2026},
  url = {https://github.com/yourusername/opsee},
  version = {1.0}
}
```

## License

OPSEE is licensed under the [Apache License 2.0](LICENSE).

## Acknowledgments

- **RO-Crate Community** - For the foundational RO-Crate specification
- **DEXPI Initiative** - For the P&ID data exchange standard
- **Research Object Community** - For FAIR data principles and tools

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/opsee/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/opsee/discussions)
- **Email**: opsee-support@example.org

## Related Projects

- [ro-crate-py](https://github.com/ResearchObject/ro-crate-py) - Python library for RO-Crate
- [DEXPI](https://www.dexpi.org/) - Data Exchange in the Process Industry
- [WorkflowHub](https://workflowhub.eu/) - FAIR workflow registry using RO-Crate
- [Dataverse](https://dataverse.org/) - Research data repository with RO-Crate support

---

**Status**: Beta | **Last Updated**: March 2026 | **Maintained by**: Epping, Niklas-Maximilian
