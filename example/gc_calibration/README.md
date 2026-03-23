# GC Calibration Example

This directory will contain a complete example of gas chromatography calibration data with:

- Calibration curve data files
- Measurement data files
- DEXPI P&ID excerpt
- Complete RO-Crate metadata

## Planned Contents

```
gc_calibration/
├── README.md (this file)
├── ro-crate-metadata.json
├── data/
│   ├── raw/
│   │   ├── gc_calibration_butanol.csv
│   │   ├── gc_calibration_acetone.csv
│   │   └── gc_sample_t*.csv
│   └── engineering/
│       └── process_excerpt.xml (DEXPI)
└── experiment_parameters.yaml
```

## Status

📝 **Planned for Version 1.1**

This example will demonstrate:
- Multi-point calibration curves
- Sample measurements
- Linking calibration to measurements
- Quality control checks

## Contributing

To add this example:
1. Prepare anonymized GC data files
2. Create minimal DEXPI excerpt
3. Run OPSEE workflow
4. Document in this README
