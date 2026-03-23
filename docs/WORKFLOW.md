# OPSEE Workflow Guide

This document provides a detailed walkthrough of the OPSEE workflow for creating RO-Crates for chemical and bioprocess engineering experiments.

## Overview

The OPSEE workflow consists of five main stages:

1. **General Metadata Entry** - Basic information about the research object
2. **Process Setup** - Loading DEXPI P&ID and experimental parameters
3. **Analytical Data Linking** - Connecting data files to instruments
4. **Engineering Asset Linking** - Connecting CAD/geometry files to equipment
5. **Export and Validation** - Generating and validating the RO-Crate

## Stage 1: General Metadata Entry

### Required Information

- **Crate Name**: Descriptive title for the research object
- **Description**: Detailed explanation of the experiment and its objectives
- **Keywords**: Comma-separated terms for discoverability
- **License**: Data usage license (default: CC-BY-4.0)
- **Date Created**: When the experiment was conducted

### Authors and Contributors

Add all people involved in the research:

- **Name**: Full name of the person
- **ORCID** (recommended): Persistent digital identifier
- **Affiliation**: Institution or organization
- **Role**: Author, Contributor, DataCollector, DataCurator, or ProjectLeader

**Best Practice**: Always include ORCIDs when available for unambiguous identification.

## Stage 2: Process Setup

### DEXPI P&ID File

The DEXPI (Data Exchange in the Process Industry) XML file represents the process setup including:

- Equipment (reactors, tanks, pumps, heat exchangers)
- Instrumentation (temperature sensors, pressure gauges, controllers)
- Analytical instruments (GC, HPLC, spectrophotometers)
- Piping and process streams
- Sampling points

#### DEXPI File Structure

OPSEE extracts the following attributes from DEXPI elements:

| DEXPI Element | Key Attributes | Used For |
|---------------|----------------|----------|
| `Equipment` | ID, TagName, ComponentClass | Process equipment entities |
| `ActuatingSystem` | ID, TagName, ComponentClass | Analytical instruments |
| `MeasuringEquipment` | ID, TagName, Type | Sensors and meters |
| `Nozzle` | ID, TagName, Parent | Sampling points |
| `PipingNetworkSegment` | ID, TagName | Process streams |

#### Loading DEXPI

1. Place your DEXPI XML file in `data/engineering/`
2. Enter the path in the notebook widget
3. Click "Load DEXPI"
4. Review the extracted equipment and instruments

**Note**: If no DEXPI file exists, you can use the provided template (`templates/example_dexpi.xml`) as a starting point.

### Experimental Parameters (YAML)

The experimental parameters file captures:

- **Experiment metadata**: title, dates, investigators
- **Process conditions**: temperature, pressure, pH, agitation
- **Feed composition**: substrates, nutrients, inoculum
- **Sampling strategy**: frequency, time points, analyses
- **Quality control**: calibrations, replicates, blanks
- **Safety information**: risk assessment, PPE, waste disposal

#### YAML Structure

```yaml
experiment:
  title: "Your Experiment Name"
  description: "Detailed description"
  
conditions:
  temperature:
    value: 35
    unit: "°C"
  # ... more conditions
  
sampling:
  frequency:
    value: 6
    unit: "hours"
  analyses:
    - type: "GC"
      instrument_tag: "GC-001"
```

See `templates/experiment_parameters.yaml` for a complete example.

## Stage 3: Analytical Data Linking

### Supported Data Types

- **RawData**: Direct output from analytical instruments
- **CalibrationData**: Calibration curves and standards
- **ProcessedData**: Derived or calculated results
- **QualityControlData**: QC samples and validation data

### Linking Process

1. **Add file path**: Location of the analytical data file
2. **Select instrument**: Choose from instruments extracted from DEXPI
3. **Set data type**: Classify the data appropriately
4. **Add description**: Explain what the file contains

### Example: GC Calibration Data

```
File Path: data/raw/gc_calibration_butanol_20240315.csv
Instrument: GC-001 - Gas Chromatograph
Data Type: CalibrationData
Description: n-Butanol calibration curve, 0.1-10 g/L range
```

### File Organization

Analytical files are automatically organized in the crate:

```
data/
├── raw/
│   ├── gc_calibration_butanol.csv
│   ├── gc_sample_t00.csv
│   └── hplc_glucose_t06.csv
└── processed/
    ├── butanol_yield_calculations.xlsx
    └── product_distribution_summary.csv
```

## Stage 4: Engineering Asset Linking

### Supported Asset Types

- **CADModel**: 3D models (.step, .stp, .iges, .stl)
- **TechnicalDrawing**: 2D drawings (.dwg, .dxf, .pdf)
- **GeometryFile**: Geometry specifications
- **Specification**: Equipment specifications and datasheets
- **Photo**: Photographs of equipment

### Linking Process

1. **Add asset path**: Location of the engineering file
2. **Select equipment**: Choose from equipment extracted from DEXPI
3. **Set asset type**: Classify the asset
4. **Add description**: Explain what the asset represents

### Example: Reactor CAD Model

```
Asset Path: data/engineering/reactor_r101.step
Equipment: R-101 - Main CSTR Reactor
Asset Type: CADModel
Description: 3D STEP model of CSTR reactor with internal geometry
```

## Stage 5: Export and Validation

### Export Process

1. **Review metadata**: Check all entered information
2. **Select output directory**: Default is current directory (.)
3. **Enable validation**: Recommended for quality assurance
4. **Click "Export RO-Crate"**

### Generated Files

The export process creates:

1. **ro-crate-metadata.json** - Machine-readable metadata
2. **ro-crate-preview.html** - Human-readable preview
3. **Data files** - Copied to appropriate subdirectories

### RO-Crate Structure

```
your-crate/
├── ro-crate-metadata.json
├── ro-crate-preview.html
├── data/
│   ├── raw/
│   │   └── [analytical data files]
│   ├── processed/
│   │   └── [processed data files]
│   └── engineering/
│       ├── process_setup.xml (DEXPI)
│       └── [CAD models, drawings]
└── [experiment parameters, if saved]
```

### Validation

OPSEE performs several validation checks:

1. **Structure validation**: Checks RO-Crate JSON-LD structure
2. **Profile compliance**: Verifies OPSEE profile requirements
3. **Link integrity**: Confirms all referenced files exist
4. **DEXPI validation**: Validates XML structure

#### Interpreting Validation Results

- **✓ No errors**: Crate is valid and ready to share
- **⚠ Warnings**: Crate is valid but could be improved
- **✗ Errors**: Crate has issues that must be fixed

## Advanced Topics

### Custom Entity Types

You can extend the OPSEE profile with custom entity types by editing the RO-Crate metadata JSON directly:

```json
{
  "@id": "#custom-sensor",
  "@type": "CustomSensor",
  "name": "My Custom Sensor",
  "measures": "Special Property"
}
```

### Batch Processing

For multiple experiments with similar structure:

1. Create a template crate
2. Use Python scripts to replicate structure
3. Modify metadata programmatically
4. Validate each crate

### Integration with ELNs

OPSEE can integrate with Electronic Lab Notebooks:

- Export ELN entries as YAML parameters
- Link ELN experiment IDs in metadata
- Automate crate generation from ELN workflows

## Troubleshooting

### DEXPI Not Loading

- **Check XML syntax**: Use an XML validator
- **Verify namespaces**: OPSEE handles most DEXPI versions
- **Check file path**: Use absolute or relative paths correctly

### Files Not Found During Export

- **Relative paths**: Paths are relative to notebook location
- **Create placeholder structure**: Use `mkdir -p data/raw data/processed data/engineering`
- **Reference-only mode**: Files are added to metadata even if not present

### Validation Failures

- **Missing required fields**: Add name and description to root
- **Invalid JSON-LD**: Check for syntax errors in manual edits
- **Broken links**: Ensure instrument/equipment IDs match DEXPI

## Best Practices

1. **Use ORCIDs** for all authors
2. **Document everything** - descriptions are crucial for reuse
3. **Calibrate instruments** before each experiment
4. **Include QC data** in your crate
5. **Version your crates** when updating
6. **Validate before sharing** to catch issues early
7. **Use consistent naming** for files and identifiers
8. **Archive raw data** separately as backup

## Next Steps

After creating your RO-Crate:

1. **Review the HTML preview** to ensure completeness
2. **Archive the crate** in your institutional repository
3. **Share with collaborators** via Zenodo, Dataverse, or similar
4. **Link from publications** using DOI or persistent URL
5. **Update as needed** when adding new data or insights

## Resources

- [RO-Crate Specification](https://www.researchobject.org/ro-crate/)
- [DEXPI Standard](https://www.dexpi.org/)
- [OPSEE GitHub Repository](https://github.com/yourusername/opsee)
- [FAIR Data Principles](https://www.go-fair.org/fair-principles/)
