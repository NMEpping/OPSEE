# Multi-Experiment RO-Crate Structure Diagrams

## Single Experiment Structure (Original)

```
┌─────────────────────────────────────────────────────────────────┐
│                        RO-Crate Root                            │
│  ro-crate-metadata.json                                         │
│                                                                 │
│  Root Dataset                                                   │
│  ├─ name: "My Experiment"                                       │
│  ├─ authors: [...]                                              │
│  └─ about: #experiment ────────────────────┐                    │
└─────────────────────────────────────────────┼───────────────────┘
                                              │
                    ┌─────────────────────────▼─────────────┐
                    │   #experiment                         │
                    │   @type: ChemicalExperiment           │
                    │   conditions: {...}                   │
                    └───────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌─────────────────┐
│ DEXPI File    │    │ Data Files    │    │ Assets          │
│ setup.xml     │    │ data.csv      │    │ reactor.step    │
└───────────────┘    └───────────────┘    └─────────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌─────────────────┐
│ #equipment-   │    │ #instrument-  │    │ Links to        │
│ R-101         │◄───┤ GC-001        │◄───┤ equipment       │
└───────────────┘    └───────────────┘    └─────────────────┘
```

## Multiple Experiments Structure (New)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                            RO-Crate Root                                      │
│  ro-crate-metadata.json                                                       │
│                                                                               │
│  Root Dataset                                                                 │
│  ├─ name: "Temperature Optimization Study"                                    │
│  ├─ authors: [...]                                                            │
│  └─ hasPart: ───────────────┬────────────────────┬─────────────────────┐     │
└─────────────────────────────┼────────────────────┼─────────────────────┼─────┘
                              │                    │                     │
                    ┌─────────▼──────────┐ ┌───────▼─────────┐ ┌────────▼─────────┐
                    │ #experiment-exp_1  │ │ #experiment-    │ │ #experiment-     │
                    │ Baseline 35°C      │ │ exp_2           │ │ exp_3            │
                    │                    │ │ High Temp 40°C  │ │ Low Temp 30°C    │
                    │ conditions:        │ │                 │ │                  │
                    │   temp: 35°C       │ │ conditions:     │ │ conditions:      │
                    └────────┬───────────┘ │   temp: 40°C    │ │   temp: 30°C     │
                             │             └─────┬───────────┘ └────┬─────────────┘
                             │                   │                  │
        ┌────────────────────┼───────────────┐   │                  │
        │                    │               │   │                  │
        ▼                    ▼               ▼   ▼                  ▼
┌──────────────┐    ┌─────────────────┐  (Similar structures for exp_2 and exp_3)
│ DEXPI File   │    │ Data Files      │
│ exp_1_       │    │ exp_1/raw/      │
│ setup.xml    │    │   gc_001.csv    │
└──────────────┘    │   gc_002.csv    │
        │           │ exp_1/proc/     │
        │           │   results.csv   │
        │           └─────────────────┘
        │                    │
        │                    │
        ▼                    ▼
┌──────────────┐    ┌─────────────────┐
│ #equipment-  │    │ #instrument-    │
│ exp_1/R-101  │◄───┤ exp_1/GC-001    │
└──────────────┘    └─────────────────┘
```

## File System Layout Comparison

### Single Experiment
```
rocrate/
├── ro-crate-metadata.json
├── ro-crate-preview.html
└── data/
    ├── engineering/
    │   └── setup.dexpi.xml
    ├── raw/
    │   ├── gc_sample_001.csv
    │   └── gc_sample_002.csv
    └── processed/
        └── calibrated_results.csv
```

### Multiple Experiments
```
rocrate/
├── ro-crate-metadata.json
├── ro-crate-preview.html
└── data/
    ├── engineering/
    │   ├── exp_1_setup.dexpi.xml        ← Separate DEXPI per experiment
    │   ├── exp_2_setup.dexpi.xml
    │   └── exp_3_setup.dexpi.xml
    ├── exp_1/                            ← Experiment 1 data
    │   ├── raw/
    │   │   ├── gc_sample_001.csv
    │   │   └── gc_sample_002.csv
    │   ├── processed/
    │   │   └── results.csv
    │   └── engineering/
    │       └── reactor_photo.jpg
    ├── exp_2/                            ← Experiment 2 data
    │   ├── raw/
    │   ├── processed/
    │   └── engineering/
    └── exp_3/                            ← Experiment 3 data
        ├── raw/
        ├── processed/
        └── engineering/
```

## Metadata Graph Relationships

### Single Experiment
```
Root Dataset
    │
    ├─ about ──────────► Experiment
    │                        │
    └─ author ───► Person    ├─ defines ──► Equipment
                             │                  ▲
                             └─ defines ──► Instrument
                                                │
                                                │
Data File ─────────────────────────────────────┘
    │
    └─ wasGeneratedBy ──► Instrument
```

### Multiple Experiments
```
Root Dataset
    │
    ├─ hasPart ────► Experiment 1 ───► Equipment (exp_1/R-101)
    │                    │                  ▲
    │                    └─► Instrument (exp_1/GC-001)
    │                            ▲          │
    │                            │          │
    ├─ hasPart ────► Experiment 2    Data Files (exp_1/...)
    │                    │                  │
    │                    └─► Equipment (exp_2/R-101)
    │                    └─► Instrument (exp_2/GC-001)
    │                            ▲
    │                            │
    └─ hasPart ────► Experiment 3    Data Files (exp_2/...)
         │               │
         │               └─► Equipment (exp_3/R-101)
         │               └─► Instrument (exp_3/GC-001)
         │                       ▲
         │                       │
         └─ author ──► Person    │
                                 │
                          Data Files (exp_3/...)
```

## Namespace Isolation

### Why Namespaced IDs?

Without namespacing:
```
❌ Problem: ID conflicts!

#equipment-R-101  ← Which experiment?
#equipment-R-101  ← Collision!
#equipment-R-101  ← Ambiguous!
```

With namespacing:
```
✅ Solution: Unique IDs per experiment

#equipment-exp_1/R-101  ← Experiment 1's reactor
#equipment-exp_2/R-101  ← Experiment 2's reactor
#equipment-exp_3/R-101  ← Experiment 3's reactor
```

## Data Flow: Notebook to RO-Crate

```
┌──────────────────────────────────────────────────────────────┐
│                    Jupyter Notebook                          │
│                                                              │
│  Step 1: Select "Multiple Experiments" mode                  │
│          w_mode.value = 'multi'                              │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 2: Configure Experiment 1                              │
│          ┌───────────────────────────────────┐               │
│          │ current_experiment = {            │               │
│          │   'id': 'exp_1',                  │               │
│          │   'dexpi': {...},                 │               │
│          │   'parameters': {...},            │               │
│          │   'analytical_files': [...],      │               │
│          │   'engineering_assets': [...]     │               │
│          │ }                                 │               │
│          └───────────────────────────────────┘               │
│          Button: "Add Experiment to Crate"                   │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│  Storage in crate_data                                       │
│          ┌───────────────────────────────────┐               │
│          │ crate_data['experiments'].append( │               │
│          │   current_experiment               │               │
│          │ )                                 │               │
│          └───────────────────────────────────┘               │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 3: Reset and repeat for experiments 2, 3, ...         │
│          Button: "Reset Current Experiment"                  │
│          (Go back to Step 2)                                 │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 4: Export                                              │
│          OPSEECrateBuilder.build_crate(crate_data)           │
│          ┌───────────────────────────────────┐               │
│          │ for exp in crate_data['experiments']: │           │
│          │   add_dexpi(exp['dexpi'], exp['id'])  │           │
│          │   add_params(exp['params'], exp['id']) │          │
│          │   for file in exp['analytical_files']: │          │
│          │     add_file(file, exp['id'])          │          │
│          └───────────────────────────────────┘               │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                 ro-crate-metadata.json                       │
│  {                                                           │
│    "@graph": [                                               │
│      {"@id": "./", "hasPart": ["#experiment-exp_1", ...]},   │
│      {"@id": "#experiment-exp_1", ...},                      │
│      {"@id": "#experiment-exp_2", ...},                      │
│      {"@id": "data/exp_1/raw/file.csv", ...}                 │
│    ]                                                         │
│  }                                                           │
└──────────────────────────────────────────────────────────────┘
```

## Comparison Matrix

| Aspect                  | Single Experiment      | Multiple Experiments    |
|-------------------------|------------------------|-------------------------|
| **Experiments**         | 1                      | 2+                      |
| **Root relationship**   | `about`                | `hasPart`               |
| **Experiment ID**       | `#experiment`          | `#experiment-{id}`      |
| **Equipment ID**        | `#equipment-{tag}`     | `#equipment-{id}/{tag}` |
| **Instrument ID**       | `#instrument-{tag}`    | `#instrument-{id}/{tag}`|
| **Data path**           | `data/raw/file.csv`    | `data/{id}/raw/file.csv`|
| **DEXPI path**          | `data/eng/file.xml`    | `data/eng/{id}_file.xml`|
| **Use case**            | Single run             | Comparative study       |
| **Complexity**          | Simple                 | More complex            |
| **Shareability**        | One experiment         | Complete study          |

## Summary

**Key Design Principles:**
1. ✅ Namespace isolation prevents ID conflicts
2. ✅ File system organization by experiment ID
3. ✅ Clear hierarchical relationships in metadata
4. ✅ Backward compatible with single-experiment mode
5. ✅ Scalable to many experiments

**Best Practices:**
- Use descriptive experiment IDs
- Document parameter differences clearly
- Maintain consistent file organization
- Link related experiments in same crate
- Keep unrelated experiments separate
