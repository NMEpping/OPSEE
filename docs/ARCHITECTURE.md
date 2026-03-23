# OPSEE Architecture

## Overview

OPSEE uses a **simplified, direct integration** approach with pyDEXPI for parsing DEXPI XML files and building FAIR RO-Crates.

## Design Principles

1. **Minimal abstraction layers** - Use libraries directly rather than wrapping them
2. **Inline helpers over modules** - Simple extraction functions in notebook
3. **Clear data flow** - pyDEXPI → dictionaries → RO-Crate

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   User Input (Notebook)                     │
├─────────────────────────────────────────────────────────────┤
│  1. Output directory selection (where crate will be created)│
│  2. General metadata (title, authors, license)              │
│  3. DEXPI file path (from anywhere on filesystem)           │
│  4. Experiment parameters (YAML)                            │
│  5. Data files + instrument links (from anywhere)           │
│  6. Engineering assets + equipment links (from anywhere)    │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│           pyDEXPI (ProteusSerializer)                       │
├─────────────────────────────────────────────────────────────┤
│  Parses DEXPI XML → DexpiModel object                      │
│  • conceptualModel.taggedPlantItems (equipment)             │
│  • conceptualModel.actuatingSystems (instruments)           │
│  • conceptualModel.processSignalGeneratingSystems           │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│         Inline Helper Functions (Notebook)                  │
├─────────────────────────────────────────────────────────────┤
│  extract_equipment(dexpi_model) → dict                      │
│  extract_instruments(dexpi_model) → dict                    │
│                                                              │
│  Simple extraction to dictionary format:                    │
│  {                                                           │
│    'id': 'uuid',                                            │
│    'tag_name': 'R-101',                                     │
│    'type': 'Reactor',                                       │
│    'name': 'Main Reactor'                                   │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│           RO-Crate Builder (rocrate_builder.py)             │
├─────────────────────────────────────────────────────────────┤
│  OPSEECrateBuilder(output_dir):                             │
│    • Creates RO-Crate directory structure                   │
│    • COPIES all files into crate (self-contained!)          │
│    • Links data files to instruments                        │
│    • Links assets to equipment                              │
│    • Generates semantic metadata                            │
│                                                              │
│  Key method: _copy_and_add_file()                           │
│    → Copies source file to output_dir/relative_path         │
│    → Adds File entity with relative path to metadata        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              Self-Contained RO-Crate                        │
├─────────────────────────────────────────────────────────────┤
│  output_dir/                                                │
│  ├── ro-crate-metadata.json  (all metadata)                │
│  ├── ro-crate-preview.html   (human preview)               │
│  └── data/                    (all copied files!)           │
│      ├── engineering/                                        │
│      │   └── setup.dexpi.xml  ← COPIED                     │
│      └── experiments/                                        │
│          ├── exp_1/                                         │
│          │   ├── raw/         ← COPIED data files          │
│          │   ├── processed/   ← COPIED                     │
│          │   └── engineering/ ← COPIED CAD/drawings        │
│          └── exp_2/                                         │
│              └── ...                                         │
│                                                              │
│  ✅ Fully portable - can be moved/shared independently       │
│  ✅ No broken links - all paths relative to crate root      │
│  ✅ FAIR compliant - complete self-contained package        │
└─────────────────────────────────────────────────────────────┘
```
┌─────────────────────────────────────────────────────┐
│              Data Storage (crate_data)              │
├─────────────────────────────────────────────────────┤
│  {                                                   │
│    'general': {...},                                │
│    'authors': [...],                                │
│    'dexpi': {                                       │
│      'path': 'path/to/file.xml',                   │
│      'equipment': {...},  # extracted dicts         │
│      'instruments': {...}                           │
│    },                                               │
│    'experiments': [...]                             │
│  }                                                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│        RO-Crate Builder (rocrate_builder.py)        │
├─────────────────────────────────────────────────────┤
│  OPSEECrateBuilder.build_crate(crate_data)         │
│  • Adds DEXPI file to crate                        │
│  • Creates equipment ContextEntities                │
│  • Creates instrument ContextEntities               │
│  • Links data files to instruments                  │
│  • Links assets to equipment                        │
│  • Creates experiment entities                      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              RO-Crate Output                        │
├─────────────────────────────────────────────────────┤
│  ro-crate-metadata.json                            │
│  ro-crate-preview.html                             │
│  data/                                              │
│    ├── engineering/                                 │
│    │   └── setup.dexpi.xml                         │
│    └── experiments/                                 │
│        ├── exp_1/                                   │
│        └── exp_2/                                   │
└─────────────────────────────────────────────────────┘
```

## Module Structure

### Current Modules (Simplified)

```
src/
├── rocrate_builder.py    # RO-Crate construction
└── validators.py          # Validation utilities
```

### Removed Modules

- ~~`src/dexpi_parser.py`~~ - **REMOVED**: Unnecessary wrapper around pyDEXPI
  - Replaced with inline helper functions in notebook
  - Simpler, more maintainable, fewer dependencies

## Data Flow

### 1. DEXPI Loading
```python
# Direct pyDEXPI usage
from pydexpi.loaders import ProteusSerializer

loader = ProteusSerializer()
dexpi_model = loader.load(directory_path, filename)

# Simple inline extraction
equipment = extract_equipment(dexpi_model)
instruments = extract_instruments(dexpi_model)
```

### 2. Dictionary Format
Equipment and instruments are extracted into simple dictionaries that `rocrate_builder` can consume:

```python
equipment = {
    'uuid-1': {
        'id': 'uuid-1',
        'tag_name': 'R-101',
        'type': 'Reactor',
        'name': 'Main Reactor',
        'element': 'Equipment'
    }
}

instruments = {
    'uuid-2': {
        'id': 'uuid-2',
        'tag_name': 'GC-001',
        'type': 'ActuatingSystem',
        'description': 'Gas Chromatograph',
        'element': 'ActuatingSystem'
    }
}
```

### 3. RO-Crate Building
The builder receives dictionaries and creates RO-Crate entities:

```python
builder = OPSEECrateBuilder()
crate = builder.build_crate(crate_data)
crate.write(output_path)
```

## Benefits of Simplified Architecture

### ✅ Advantages

1. **Less code to maintain** - No wrapper module
2. **Direct library access** - Easier to update when pyDEXPI changes
3. **Transparent** - User can see extraction logic in notebook
4. **Flexible** - Easy to customize extraction for specific needs
5. **Fewer dependencies** - Only pyDEXPI, not custom wrappers

### ⚠️ Trade-offs

1. **Helper functions in notebook** - Not reusable across projects
   - *Acceptable*: This is a workflow tool, not a library
2. **No centralized DEXPI utilities** - Each notebook has own helpers
   - *Acceptable*: OPSEE is single-notebook focused

## Comparison: Before vs After

### Before (v0.1 with wrapper module)
```
pyDEXPI → dexpi_parser.py → dict → rocrate_builder.py → RO-Crate
           (270 lines wrapper)
```

### After (v0.2+ simplified)
```
pyDEXPI → inline helpers → dict → rocrate_builder.py → RO-Crate
          (in notebook)
```

**Improvements in v0.2:**
- **Lines of code removed**: ~270 (entire dexpi_parser.py module)
- **Dependencies removed**: requirements.txt (consolidated to pyproject.toml)
- **Complexity reduced**: 1 fewer module, single dependency source
- **Functionality preserved**: 100% - same output, simpler codebase
- **Maintainability**: Direct pyDEXPI usage, easier to understand
- **Portability added**: All files now copied into RO-Crate (self-contained!)

## Extension Points

If you need custom DEXPI extraction:

1. **Modify inline helpers** in notebook Cell 1
2. **Add new extraction functions** for specific component types
3. **Adjust dictionary format** if needed (update rocrate_builder accordingly)

Example - adding piping extraction:
```python
def extract_piping(dexpi_model):
    """Extract piping network from pyDEXPI model.
    
    Args:
        dexpi_model: Loaded DEXPI model from ProteusSerializer
    
    Returns:
        Dictionary mapping piping IDs to piping metadata
    \"""
    piping = {}
    if hasattr(dexpi_model.conceptualModel, 'pipingNetworkSystems'):
        for pns in dexpi_model.conceptualModel.pipingNetworkSystems:
            pipe_id = str(pns.id) if hasattr(pns, 'id') else str(id(pns))
            piping[pipe_id] = {
                'id': pipe_id,
                'tag_name': pns.tagName if hasattr(pns, 'tagName') else pipe_id,
                'type': pns.__class__.__name__
            }
    return piping
```

## Testing

**Interactive Testing via Notebook:**
Run all notebook cells in order:
1. ✅ Imports succeed (including pyDEXPI from GitHub)
2. ✅ DEXPI loads with ProteusSerializer
3. ✅ Equipment/instruments extracted correctly
4. ✅ RO-Crate builds and exports successfully
5. ✅ Validation passes (if enabled)

**No unit tests for inline helpers** - validation happens through notebook execution and RO-Crate output inspection.

## Dependency Management

**Package Manager:** uv (modern Python package installer)

**Single Source of Truth:** All dependencies in `pyproject.toml`
- rocrate, ipywidgets, jupyter, jupyterlab
- pyDEXPI from GitHub: `pydexpi @ git+https://github.com/process-intelligence-research/pyDEXPI.git`
- pyyaml, lxml, jsonschema, pandas
- ipyfilechooser, tqdm, notebook

**Installation:**
```bash
# Using uv (recommended)
uv pip install -e .

# Using pip (alternative)
pip install -e .
```

## Future Considerations

If OPSEE grows to multiple notebooks or becomes a library:
- Consider creating `opsee.dexpi` module with extraction utilities
- Add unit tests for extraction functions
- Package as standalone importable library
- Add CLI for batch processing

**Current philosophy:** **Simplicity wins** - keep it as an interactive notebook tool until there's clear need for more structure.
