# DEXPI to RO-Crate Mapping Guide

This document explains how OPSEE maps DEXPI P&ID components to RO-Crate entities.

## Overview

DEXPI (Data Exchange in the Process Industry) is an XML-based standard for representing process engineering information. OPSEE parses DEXPI files to extract equipment and instrumentation metadata, creating corresponding RO-Crate entities that can be linked to experimental data.

## DEXPI Structure

### Key DEXPI Elements

DEXPI represents process systems using:

- **Equipment**: Vessels, reactors, tanks, pumps, heat exchangers
- **ActuatingSystem**: Control systems, valves, analytical instruments
- **MeasuringEquipment**: Sensors, meters, indicators
- **Nozzle**: Connection points, sampling ports
- **PipingNetworkSegment**: Pipes, process streams

### DEXPI Attributes

Each component typically has:

- **ID**: Unique identifier in the DEXPI file
- **TagName**: Engineering tag (e.g., "R-101", "GC-001")
- **ComponentClass**: Type of component
- **ComponentName**: Human-readable name
- **Custom Attributes**: Equipment-specific properties

## Mapping Strategy

### 1. Equipment → ProcessEquipment

#### DEXPI XML

```xml
<Equipment ID="R-101" TagName="R-101" 
           ComponentClass="Reactor" 
           ComponentName="Main CSTR Reactor">
    <Attribute Name="Volume" Value="5.0" Unit="L"/>
    <Attribute Name="Material" Value="SS316"/>
</Equipment>
```

#### RO-Crate Entity

```json
{
  "@id": "#equipment-R-101",
  "@type": "ProcessEquipment",
  "name": "Main CSTR Reactor",
  "identifier": "R-101",
  "additionalType": "Reactor",
  "description": "Reactor R-101",
  "isDefinedIn": {"@id": "data/engineering/process_setup.xml"}
}
```

#### Mapping Rules

| DEXPI Attribute | RO-Crate Property | Notes |
|-----------------|-------------------|-------|
| ID | Used in @id | Prefixed with "#equipment-" |
| TagName | identifier | Primary reference for linking |
| ComponentClass | additionalType | Equipment type |
| ComponentName | name | Human-readable label |
| - | isDefinedIn | Link to DEXPI file |

### 2. ActuatingSystem → AnalyticalInstrument

#### DEXPI XML

```xml
<ActuatingSystem ID="GC-001" TagName="GC-001" 
                 ComponentClass="AnalyticalInstrument"
                 ComponentName="Gas Chromatograph">
    <Attribute Name="Manufacturer" Value="Agilent"/>
    <Attribute Name="Model" Value="7890B"/>
    <Attribute Name="Detector" Value="FID"/>
</ActuatingSystem>
```

#### RO-Crate Entity

```json
{
  "@id": "#instrument-GC-001",
  "@type": "AnalyticalInstrument",
  "name": "Gas Chromatograph",
  "identifier": "GC-001",
  "additionalType": "AnalyticalInstrument",
  "description": "Gas Chromatograph",
  "isDefinedIn": {"@id": "data/engineering/process_setup.xml"}
}
```

#### Mapping Rules

| DEXPI Attribute | RO-Crate Property | Notes |
|-----------------|-------------------|-------|
| ID | Used in @id | Prefixed with "#instrument-" |
| TagName | identifier | Used for data file linking |
| ComponentClass | additionalType | Instrument type |
| ComponentName or description | name | Instrument name |

### 3. MeasuringEquipment → Sensor/Instrument

#### DEXPI XML

```xml
<MeasuringEquipment ID="TE-101" TagName="TE-101" 
                    ComponentClass="TemperatureSensor"
                    ComponentName="Reactor Temperature">
    <Attribute Name="Type" Value="Pt100"/>
    <Attribute Name="Range_Max" Value="100" Unit="°C"/>
</MeasuringEquipment>
```

#### RO-Crate Entity

```json
{
  "@id": "#instrument-TE-101",
  "@type": "AnalyticalInstrument",
  "name": "Reactor Temperature",
  "identifier": "TE-101",
  "additionalType": "TemperatureSensor",
  "description": "Reactor Temperature"
}
```

### 4. Nozzle → SamplingPoint

#### DEXPI XML

```xml
<Nozzle ID="SP-R101-01" TagName="SP-R101-01" 
        ComponentName="Reactor Sample Port 1">
    <Attribute Name="Location" Value="Top"/>
    <Attribute Name="Size" Value="6" Unit="mm"/>
</Nozzle>
```

#### RO-Crate Entity

```json
{
  "@id": "#nozzle-SP-R101-01",
  "@type": "SamplingPoint",
  "name": "Reactor Sample Port 1",
  "identifier": "SP-R101-01",
  "description": "Sampling point at reactor top"
}
```

## Data File Linking

### Analytical Data → Instrument

When adding an analytical data file, OPSEE creates links using the instrument's TagName:

#### Process

1. User selects instrument by TagName (e.g., "GC-001")
2. OPSEE finds corresponding RO-Crate entity (`#instrument-GC-001`)
3. Creates File entity with links

#### Result

```json
{
  "@id": "data/raw/gc_sample_t06.csv",
  "@type": ["File", "AnalyticalData"],
  "name": "gc_sample_t06.csv",
  "encodingFormat": "text/csv",
  "additionalType": "RawData",
  "instrument": {"@id": "#instrument-GC-001"},
  "wasGeneratedBy": {"@id": "#instrument-GC-001"}
}
```

#### Link Types

- **instrument**: Direct reference to the instrument
- **wasGeneratedBy**: PROV-O provenance property indicating data generation

### Engineering Asset → Equipment

When adding a CAD model or drawing:

#### Process

1. User selects equipment by TagName (e.g., "R-101")
2. OPSEE finds corresponding entity (`#equipment-R-101`)
3. Creates bidirectional link

#### Result

```json
{
  "@id": "data/engineering/reactor_r101.step",
  "@type": ["File", "EngineeringAsset"],
  "name": "reactor_r101.step",
  "encodingFormat": "application/step",
  "additionalType": "CADModel",
  "about": {"@id": "#equipment-R-101"}
}
```

Equipment entity updated:

```json
{
  "@id": "#equipment-R-101",
  "@type": "ProcessEquipment",
  "hasRepresentation": [
    {"@id": "data/engineering/reactor_r101.step"}
  ]
}
```

## Complex Mappings

### Equipment Hierarchies

Some DEXPI files have nested equipment structures:

```xml
<Equipment ID="R-101" TagName="R-101">
    <Nozzle ID="N-101" TagName="N-101"/>
    <Nozzle ID="N-102" TagName="N-102"/>
</Equipment>
```

OPSEE handles this by:
1. Creating separate entities for parent and children
2. Storing parent reference in child entity
3. Enabling queries like "all nozzles on R-101"

### Multi-Component Instruments

Complex instruments (e.g., GC-MS with autosampler):

```xml
<ActuatingSystem ID="GCMS-001">
    <InstrumentComponent ID="GC-001" Type="GC"/>
    <InstrumentComponent ID="MS-001" Type="MS"/>
</ActuatingSystem>
```

OPSEE creates:
1. Parent instrument entity
2. Child component entities
3. Links between them

## ID Generation

### RO-Crate Entity IDs

OPSEE generates RO-Crate IDs using a consistent pattern:

| DEXPI Element | ID Prefix | Example |
|---------------|-----------|---------|
| Equipment | `#equipment-` | `#equipment-R-101` |
| ActuatingSystem (instrument) | `#instrument-` | `#instrument-GC-001` |
| MeasuringEquipment | `#instrument-` | `#instrument-TE-101` |
| Nozzle | `#nozzle-` | `#nozzle-SP-R101-01` |
| PipingNetworkSegment | `#piping-` | `#piping-S-101` |

### Collision Handling

If multiple DEXPI elements share the same ID:
1. OPSEE appends element type to ID
2. Logs a warning
3. Preserves all entities separately

## Lookup Methods

### By TagName

Most common lookup method:

```python
# In DEXPI parser
component = parser.find_by_tag_name("R-101")

# Returns:
{
    'id': 'R-101',
    'tag_name': 'R-101',
    'type': 'Reactor',
    'element': 'Equipment'
}
```

### By Type

Find all components of a specific type:

```python
all_reactors = [eq for eq in equipment.values() 
                if eq['type'] == 'Reactor']
```

### By Parent

Find child components:

```python
nozzles_on_reactor = [n for n in nozzles.values() 
                      if n.get('parent_equipment') == 'R-101']
```

## Validation

### DEXPI Validation

OPSEE validates:
1. **XML well-formedness**: Valid XML structure
2. **Presence of components**: At least some equipment or instruments
3. **TagName completeness**: All components have TagNames
4. **Attribute consistency**: Required attributes present

### Link Validation

After creating RO-Crate:
1. **ID existence**: All referenced IDs exist
2. **Bidirectional links**: Equipment ↔ Assets links are mutual
3. **Type consistency**: Instruments linked to AnalyticalData, equipment to EngineeringAssets

## Extending the Mapping

### Custom DEXPI Attributes

To extract additional DEXPI attributes:

1. Modify the inline helper functions (`extract_equipment()` or `extract_instruments()`) in the notebook
2. Access attributes from the pyDEXPI model objects
3. Store in component dictionary
4. Map to RO-Crate properties in `rocrate_builder.py`

Example:

```python
# In notebook helper function extract_equipment()
for eq in dexpi_model.conceptualModel.taggedPlantItems:
    eq_id = str(eq.id) if hasattr(eq, 'id') else str(id(eq))
    
    # Extract custom attributes if available
    volume = eq.volume if hasattr(eq, 'volume') else None
    material = eq.material if hasattr(eq, 'material') else None
    
    equipment[eq_id] = {
        'id': eq_id,
        'tag_name': eq.tagName if hasattr(eq, 'tagName') else eq_id,
        'type': eq.__class__.__name__,
        'volume': volume,
        'material': material
    }
```

### Custom RO-Crate Properties

Add domain-specific properties:

```python
# In rocrate_builder.py
eq_entity['volume'] = eq_data.get('volume')
eq_entity['material'] = eq_data.get('material')
```

## Example Workflow

### Complete Mapping Example

Starting with DEXPI:

```xml
<Equipment ID="R-101" TagName="R-101" ComponentClass="Reactor">
    <Attribute Name="Volume" Value="5.0" Unit="L"/>
</Equipment>
<ActuatingSystem ID="GC-001" TagName="GC-001">
    <Attribute Name="Function" Value="Product Analysis"/>
</ActuatingSystem>
```

After OPSEE processing:

```json
{
  "@graph": [
    {
      "@id": "#equipment-R-101",
      "@type": "ProcessEquipment",
      "identifier": "R-101",
      "name": "Reactor R-101",
      "hasRepresentation": [
        {"@id": "data/engineering/reactor_r101.step"}
      ]
    },
    {
      "@id": "#instrument-GC-001",
      "@type": "AnalyticalInstrument",
      "identifier": "GC-001",
      "name": "GC-001"
    },
    {
      "@id": "data/raw/gc_sample.csv",
      "@type": ["File", "AnalyticalData"],
      "instrument": {"@id": "#instrument-GC-001"},
      "wasGeneratedBy": {"@id": "#instrument-GC-001"}
    },
    {
      "@id": "data/engineering/reactor_r101.step",
      "@type": ["File", "EngineeringAsset"],
      "about": {"@id": "#equipment-R-101"}
    }
  ]
}
```

## Troubleshooting

### Missing TagNames

**Problem**: DEXPI components without TagName attributes

**Solution**:
- Use ID as fallback identifier
- Flag in validation warnings
- Recommend adding TagNames to DEXPI

### Namespace Issues

**Problem**: Different DEXPI versions use different namespaces

**Solution**:
- OPSEE uses namespace-agnostic XPath (`local-name()`)
- Detects and adapts to DEXPI namespace automatically

### Ambiguous Links

**Problem**: Multiple components with same TagName

**Solution**:
- OPSEE uses element type + TagName for disambiguation
- Logs warnings for duplicates
- User should fix DEXPI file

## Best Practices

1. **Use unique TagNames** in DEXPI files
2. **Document custom attributes** in equipment specifications
3. **Maintain DEXPI version consistency** across projects
4. **Validate DEXPI** before importing to OPSEE
5. **Link systematically**: All analytical files to instruments, all assets to equipment
6. **Review generated entities** in RO-Crate metadata
7. **Test with sample data** before full-scale application

## References

- [DEXPI Specification](https://www.dexpi.org/)
- [ISO 15926](https://www.iso.org/standard/29557.html) - Industrial automation systems
- [RO-Crate Contextual Entities](https://www.researchobject.org/ro-crate/specification/1.2/contextual-entities.html)
- [PROV-O Provenance Ontology](https://www.w3.org/TR/prov-o/)
