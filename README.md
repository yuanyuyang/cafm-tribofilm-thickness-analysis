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
