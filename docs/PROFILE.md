# OPSEE RO-Crate Profile Specification

**Profile URI**: `https://w3id.org/opsee/ro-crate-profile/chemical-engineering/1.0`  
**Version**: 1.0.0  
**Release Date**: March 23, 2026  
**Status**: Beta

## Abstract

The OPSEE RO-Crate Profile defines a domain-specific extension to the RO-Crate specification for packaging chemical and bioprocess engineering experimental data with rich, machine-readable metadata. This profile enables semantic linking between analytical data files, process equipment, and engineering assets.

## 1. Introduction

### 1.1 Purpose

Chemical and bioprocess engineering research generates diverse data types:
- Analytical measurements (GC, HPLC, spectroscopy)
- Process monitoring data (temperature, pressure, pH)
- Engineering artifacts (CAD models, P&ID diagrams)
- Experimental protocols and parameters

The OPSEE profile standardizes how these resources are packaged together with their semantic relationships, enabling:
- **Reproducibility**: Complete experimental context
- **Reusability**: Clear provenance and methodology
- **Interoperability**: Machine-readable links between data and equipment
- **Discoverability**: Rich metadata for search and indexing

### 1.2 Scope

This profile applies to:
- Laboratory-scale chemical experiments
- Pilot plant operations
- Bioprocess engineering studies
- Process development campaigns

### 1.3 Conformance

An RO-Crate conforms to this profile if:
1. It is a valid RO-Crate 1.2
2. The root dataset includes `conformsTo: https://w3id.org/opsee/ro-crate-profile/chemical-engineering/1.0`
3. It contains at least one entity of type `ChemicalExperiment`
4. Analytical data files are typed as `AnalyticalData` and linked to instruments
5. DEXPI P&ID files (if present) are typed correctly and linked to equipment entities

## 2. Entity Types

### 2.1 ChemicalExperiment

Represents the experiment as a whole.

**Type**: `ChemicalExperiment`

**Properties**:
- `name` (REQUIRED): Experiment title
- `description` (REQUIRED): Detailed methodology
- `experimentalConditions` (RECOMMENDED): Operating parameters (object)
- `methodology` (RECOMMENDED): Experimental procedures
- `startDate` (RECOMMENDED): ISO 8601 date
- `endDate` (RECOMMENDED): ISO 8601 date

**Example**:
```json
{
  "@id": "#experiment",
  "@type": "ChemicalExperiment",
  "name": "n-Butanol Production via ABE Fermentation",
  "description": "Investigation of optimal fermentation conditions...",
  "experimentalConditions": {
    "temperature": "35°C",
    "pH": "5.5",
    "pressure": "1 atm"
  },
  "startDate": "2024-03-15",
  "endDate": "2024-03-17"
}
```

### 2.2 ProcessEquipment

Represents physical process equipment from P&ID.

**Type**: `ProcessEquipment`

**Properties**:
- `name` (REQUIRED): Equipment name
- `identifier` (REQUIRED): Equipment tag from P&ID (e.g., "R-101")
- `additionalType` (RECOMMENDED): Specific type (Reactor, Tank, Pump, etc.)
- `description` (RECOMMENDED): Equipment details
- `isDefinedIn` (RECOMMENDED): Reference to DEXPI file
- `hasRepresentation` (OPTIONAL): Array of CAD models or drawings

**Example**:
```json
{
  "@id": "#equipment-R-101",
  "@type": "ProcessEquipment",
  "name": "Main CSTR Reactor",
  "identifier": "R-101",
  "additionalType": "Reactor",
  "description": "5L continuous stirred-tank reactor, SS316",
  "isDefinedIn": {"@id": "data/engineering/process.xml"},
  "hasRepresentation": [
    {"@id": "data/engineering/reactor_r101.step"}
  ]
}
```

### 2.3 AnalyticalInstrument

Represents analytical or measuring instruments.

**Type**: `AnalyticalInstrument`

**Properties**:
- `name` (REQUIRED): Instrument name
- `identifier` (REQUIRED): Instrument tag from P&ID
- `additionalType` (RECOMMENDED): Instrument type (GC, HPLC, etc.)
- `description` (OPTIONAL): Instrument details
- `isDefinedIn` (RECOMMENDED): Reference to DEXPI file
- `manufacturer` (OPTIONAL): Manufacturer name
- `model` (OPTIONAL): Model number

**Example**:
```json
{
  "@id": "#instrument-GC-001",
  "@type": "AnalyticalInstrument",
  "name": "Gas Chromatograph",
  "identifier": "GC-001",
  "additionalType": "GC-FID",
  "manufacturer": "Agilent",
  "model": "7890B",
  "isDefinedIn": {"@id": "data/engineering/process.xml"}
}
```

### 2.4 AnalyticalData

Represents data files from analytical instruments.

**Type**: `["File", "AnalyticalData"]` (array)

**Properties**:
- `name` (REQUIRED): File name
- `encodingFormat` (REQUIRED): MIME type
- `additionalType` (REQUIRED): One of:
  - `RawData`: Direct instrument output
  - `CalibrationData`: Calibration curves
  - `ProcessedData`: Derived results
  - `QualityControlData`: QC samples
- `description` (RECOMMENDED): What the file contains
- `instrument` (REQUIRED): Reference to AnalyticalInstrument
- `wasGeneratedBy` (RECOMMENDED): Provenance link to instrument
- `dateCreated` (RECOMMENDED): When data was collected

**Example**:
```json
{
  "@id": "data/raw/gc_sample_t06.csv",
  "@type": ["File", "AnalyticalData"],
  "name": "gc_sample_t06.csv",
  "encodingFormat": "text/csv",
  "additionalType": "RawData",
  "description": "GC analysis of reactor sample at t=6h",
  "instrument": {"@id": "#instrument-GC-001"},
  "wasGeneratedBy": {"@id": "#instrument-GC-001"},
  "dateCreated": "2024-03-15T12:00:00Z"
}
```

### 2.5 EngineeringAsset

Represents CAD models, drawings, or technical documentation.

**Type**: `["File", "EngineeringAsset"]` (array)

**Properties**:
- `name` (REQUIRED): File name
- `encodingFormat` (REQUIRED): MIME type
- `additionalType` (REQUIRED): One of:
  - `CADModel`: 3D models
  - `TechnicalDrawing`: 2D drawings
  - `GeometryFile`: Geometry specifications
  - `Specification`: Datasheets
  - `Photo`: Equipment photographs
- `about` (REQUIRED): Reference to ProcessEquipment
- `description` (RECOMMENDED): What the asset represents

**Example**:
```json
{
  "@id": "data/engineering/reactor_r101.step",
  "@type": ["File", "EngineeringAsset"],
  "name": "reactor_r101.step",
  "encodingFormat": "application/step",
  "additionalType": "CADModel",
  "about": {"@id": "#equipment-R-101"},
  "description": "3D STEP model of CSTR reactor with internals"
}
```

## 3. Required Metadata

### 3.1 Root Dataset

The root dataset (`@id": "./"`) MUST include:
- `name`: Descriptive title
- `description`: Detailed explanation
- `author`: Array of Person entities
- `license`: License identifier or URL
- `conformsTo`: OPSEE profile URI

SHOULD include:
- `keywords`: Array of terms
- `dateCreated`: ISO 8601 date
- `about`: Reference to ChemicalExperiment entity

### 3.2 Person Entities

Author/contributor entities MUST include:
- `name`: Full name
- `@type`: "Person"

SHOULD include:
- `@id`: ORCID URL (e.g., "https://orcid.org/0000-0000-0000-0000")
- `affiliation`: Institution name

## 4. Relationships

### 4.1 Experiment Relationships

- **Root Dataset** `about` → **ChemicalExperiment**: What the crate is about
- **AnalyticalData** `instrument` → **AnalyticalInstrument**: Which instrument
- **AnalyticalData** `wasGeneratedBy` → **AnalyticalInstrument**: Provenance
- **EngineeringAsset** `about` → **ProcessEquipment**: What equipment
- **ProcessEquipment** `hasRepresentation` → **EngineeringAsset**: Bidirectional
- **ProcessEquipment** `isDefinedIn` → **DEXPI File**: P&ID source
- **AnalyticalInstrument** `isDefinedIn` → **DEXPI File**: P&ID source

### 4.2 Relationship Diagram

```
Root Dataset
    |-- about --> ChemicalExperiment
    |-- author --> Person (ORCID)
    |
    |-- hasPart --> AnalyticalData
    |                   |-- instrument --> AnalyticalInstrument
    |                   |-- wasGeneratedBy --> AnalyticalInstrument
    |                                              |-- isDefinedIn --> DEXPI File
    |
    |-- hasPart --> EngineeringAsset
                        |-- about --> ProcessEquipment
                                          |-- isDefinedIn --> DEXPI File
```

## 5. File Organization

### 5.1 Recommended Structure

```
ro-crate/
├── ro-crate-metadata.json
├── ro-crate-preview.html
├── data/
│   ├── raw/                    # Raw analytical data
│   │   ├── gc_*.csv
│   │   ├── hplc_*.csv
│   │   └── calibration_*.csv
│   ├── processed/              # Derived/calculated data
│   │   ├── yields.xlsx
│   │   └── kinetics.csv
│   └── engineering/            # CAD, DEXPI, drawings
│       ├── process_pid.xml     # DEXPI file
│       ├── reactor_r101.step   # CAD models
│       └── flow_diagram.pdf    # Drawings
└── experiment_parameters.yaml  # Experimental metadata (optional)
```

### 5.2 File Naming Conventions

RECOMMENDED naming patterns:
- Analytical data: `{instrument}_{type}_{timestamp}.{ext}`
  - Example: `gc_sample_t06h.csv`
- Calibration: `{instrument}_calibration_{analyte}_{date}.{ext}`
  - Example: `gc_calibration_butanol_20240315.csv`
- CAD models: `{equipment_tag}_{description}.{ext}`
  - Example: `r101_reactor_assembly.step`

## 6. Validation

### 6.1 Structural Validation

Validators SHOULD check:
1. Valid RO-Crate 1.2 structure
2. Presence of conformsTo with OPSEE profile URI
3. At least one ChemicalExperiment entity
4. All AnalyticalData linked to instruments
5. All EngineeringAsset entities linked to equipment

### 6.2 Semantic Validation

Validators SHOULD check:
1. Referenced entities exist (no broken links)
2. File paths resolve correctly
3. DEXPI file validates as XML
4. Equipment identifiers match between DEXPI and RO-Crate

### 6.3 Profile Compliance Levels

**Level 1 (Minimal)**:
- Valid RO-Crate structure
- ChemicalExperiment entity present
- Basic metadata (name, description, author)

**Level 2 (Recommended)**:
- DEXPI file included
- All analytical data linked to instruments
- Equipment entities created from DEXPI
- CAD models or drawings included

**Level 3 (Exemplary)**:
- Complete experimental parameters
- Quality control data included
- Multiple replicate experiments
- Detailed provenance chains
- Published to repository with DOI

## 7. Extensions

### 7.1 Custom Properties

Implementations MAY add custom properties prefixed with namespace:

```json
{
  "@id": "#equipment-R-101",
  "@type": "ProcessEquipment",
  "opsee:volumeLiters": 5.0,
  "opsee:designPressureBar": 2.0
}
```

### 7.2 Subprofiles

Domain-specific subprofiles MAY be created:
- `opsee-bioprocess`: Bioprocessing specifics
- `opsee-catalysis`: Catalysis research
- `opsee-scale-up`: Pilot plant and scale-up

## 8. Examples

See repository `examples/` directory for complete examples:
- `gc_calibration/`: Gas chromatography workflow
- `batch_reactor/`: Complete batch experiment
- `continuous_process/`: Continuous operation data

## 9. Tooling

### 9.1 Creation Tools

- **opsee_workflow.ipynb**: Interactive Jupyter notebook
- **Python API**: `from src.rocrate_builder import create_crate`

### 9.2 Validation Tools

- **Python**: `python -m src.validators validate_crate`
- **Profile validator**: `python -m src.validators validate_profile`

## 10. References

### 10.1 Standards

- [RO-Crate 1.2](https://www.researchobject.org/ro-crate/1.2/)
- [DEXPI](https://www.dexpi.org/)
- [PROV-O](https://www.w3.org/TR/prov-o/)
- [Schema.org](https://schema.org/)

### 10.2 Related Work

- [Workflow RO-Crate](https://w3id.org/workflowhub/workflow-ro-crate/)
- [RO-Crate for Life Sciences](https://www.researchobject.org/workflow-ro-crate/)
- [ISA-Tab](https://isa-tools.org/)

## Appendix A: Complete Example

See `examples/complete_crate.json` in repository.

## Appendix B: JSON Schema

See `templates/profile_schema.json` for validation schema.

## Change Log

### Version 1.0.0 (2026-03-23)
- Initial release
- Core entity types defined
- DEXPI integration specified
- File organization conventions established

---

**Maintained by**: OPSEE Community  
**Contact**: opsee-support@example.org  
**Repository**: https://github.com/yourusername/opsee
