# C-AFM Tribofilm Thickness Analysis

This repository demonstrates a Python-based workflow for estimating nanoscale tribofilm thickness from conductive-AFM force/current curves.

The workflow is based on research data analysis developed during PhD work on tribochemistry-enabled film formation. It demonstrates data manipulation, derivative-based transition detection, numerical analysis, and structured output using Python.

## Project aims

This repository demonstrates:

- Python-based scientific data analysis
- Processing of force/current curve data
- Derivative-based detection of mechanical and electrical transitions
- Estimation of apparent nanoscale film thickness
- Clear code structure and documentation

## Scientific background

In conductive-AFM thickness analysis, the force signal can be used to identify the mechanical contact response, while the current signal can indicate the onset of electrical conduction through the film/substrate system.

The apparent tribofilm thickness is estimated from the height difference between the detected mechanical transition and electrical transition.

## Original data workflow

The original workflow analyses conductive-AFM data stored in `.spm` files. These files are read using the Gwyddion Python module (`gwy`). The script extracts force and current curves from a Gwyddion data container, calculates the derivatives of force and current with respect to height, and estimates the apparent tribofilm thickness from the detected mechanical and electrical transitions.

A CSV example is included only to demonstrate the core calculation without requiring users to install Gwyddion or access unpublished raw `.spm` files.

## Data note

The original experimental data were stored as `.spm` files and are not included in this repository because they may contain unpublished research data and instrument-specific metadata. The included CSV file is a simplified example dataset used only to demonstrate the analysis workflow.

## Repository structure

```text
cafm-tribofilm-thickness-analysis/
│
├── README.md
├── requirements.txt
├── data/
│   └── example_force_current_curve.csv
├── src/
│   └── tribofilm_analysis.py
└── outputs/
    └── .gitkeep
```

## Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Example usage

Run the example script from the repository root:

```bash
python src/tribofilm_analysis.py
```

The script reads:

```text
data/example_force_current_curve.csv
```

and prints the estimated tribofilm thickness.

## Input data format

The example CSV file contains three columns:

```text
height, force, current
```

where:

- `height` is the height or displacement signal;
- `force` is the force signal;
- `current` is the current signal.

The original `.spm` workflow extracts these signals from Gwyddion-compatible data containers.

## Notes on Gwyddion

The original research workflow analyses conductive-AFM data stored in `.spm` files. These files are read using the Gwyddion Python module (`gwy`).

The `gwy` module is not included in `requirements.txt` because it is not a standard pip package and usually needs to be run within a Gwyddion-compatible Python environment.

The CSV example is provided so that the core numerical analysis can be inspected and tested without access to Gwyddion or unpublished raw AFM files.

## Notes on thresholds

The default threshold values are example values based on the original analysis workflow:

```python
force_threshold = 25.0
current_threshold = 0.015
```

These values should be adjusted for different materials, probes, signal scales and instrument settings.

## Limitations

This repository is intended to demonstrate a clear scientific data analysis workflow. The threshold-based transition detection method is simple and interpretable, but more robust approaches could include smoothing, uncertainty estimation, automated threshold selection, or model-based transition detection.
