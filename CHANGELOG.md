# Changelog

All notable changes to the OPSEE project will be documented in this file.

## [0.2.0] - 2026-03-23

### Changed
- **BREAKING**: Switched DEXPI parsing library from incorrect `pydexpi` package to official **pyDEXPI** from [process-intelligence-research/pyDEXPI](https://github.com/process-intelligence-research/pyDEXPI)
- **Simplified architecture**: Removed `src/dexpi_parser.py` wrapper module - now using pyDEXPI `ProteusSerializer` directly in notebook
- Modified `pyproject.toml` to install pyDEXPI from GitHub repository
- **Removed `requirements.txt`** - all dependencies now managed in `pyproject.toml` (single source of truth for `uv`)
- Updated imports in `opsee_workflow.ipynb` to avoid conflicts with pip `validators` package
- Enhanced QUICKSTART.md with v0.2 features and pyDEXPI integration details

### Added
- Inline helper functions `extract_equipment()` and `extract_instruments()` in notebook
- Comprehensive QUICKSTART.md guide for new users
- CHANGELOG.md to track project changes
- `docs/ARCHITECTURE.md` with complete architecture documentation

### Removed
- `src/dexpi_parser.py` - 270 lines of unnecessary wrapper code
- `requirements.txt` - redundant with `pyproject.toml`

### Fixed
- Fixed DEXPI parser syntax errors and import issues
- Corrected equipment and instrument extraction to work with DEXPI 1.3 model structure
- Resolved validator import conflicts in notebook

### Technical Details

**pyDEXPI Integration:**
- Uses `ProteusSerializer` directly in notebook to load DEXPI XML files (Proteus format)
- Inline helper functions extract equipment from `conceptualModel.taggedPlantItems`
- Inline helper functions extract instruments from `conceptualModel.actuatingSystems` and `processSignalGeneratingSystems`
- Supports DEXPI version 1.3 standard
- **Removed wrapper module** for simpler, more maintainable codebase

**API Changes:**
```python
# Old (with wrapper):
from dexpi_parser import DexpiParser
parser = DexpiParser(xml_path)
equipment = parser.get_equipment()

# New (direct pyDEXPI):
from pydexpi.loaders import ProteusSerializer
loader = ProteusSerializer()
dexpi_model = loader.load(directory_path, filename)
equipment = extract_equipment(dexpi_model)  # inline helper
```

## [0.1.0] - Initial Release

### Added
- Interactive Jupyter Notebook workflow for RO-Crate creation
- Support for 0 to many experiments on one shared experimental setup
- DEXPI P&ID file integration
- RO-Crate builder with OPSEE profile
- Validation utilities
- Example templates and documentation
