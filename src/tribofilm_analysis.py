"""
tribofilm_analysis.py

Python workflow for estimating nanoscale tribofilm thickness from
conductive-AFM force/current curves.

The analysis identifies:
1. a mechanical transition from the force-gradient signal;
2. an electrical transition from the current-gradient signal;
3. the apparent film thickness from the height difference.
"""

from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd


def calculate_derivatives(
    height: np.ndarray,
    force: np.ndarray,
    current: np.ndarray,
) -> Dict[str, np.ndarray]:
    """
    Calculate numerical derivatives of force and current with respect to height.
    """
    height = np.asarray(height, dtype=float)
    force = np.asarray(force, dtype=float)
    current = np.asarray(current, dtype=float)

    if not (len(height) == len(force) == len(current)):
        raise ValueError("height, force and current must have the same length.")

    if len(height) < 3:
        raise ValueError("At least three data points are required.")

    d_height = np.diff(height)

    if np.any(d_height == 0):
        raise ValueError("Height data contains repeated values.")

    d_force = np.diff(force) / d_height
    d_current = np.diff(current) / d_height

    d_force = np.append(d_force, np.nan)
    d_current = np.append(d_current, np.nan)

    return {
        "height": height,
        "force": force,
        "current": current,
        "d_force_d_height": d_force,
        "d_current_d_height": d_current,
    }


def find_first_threshold_crossing(
    signal: np.ndarray,
    threshold: float,
    direction: str = "above",
) -> Optional[int]:
    """
    Find the first index where a signal crosses a threshold.
    """
    signal = np.asarray(signal, dtype=float)

    if direction == "above":
        indices = np.where(signal > threshold)[0]
    elif direction == "below":
        indices = np.where(signal < threshold)[0]
    else:
        raise ValueError("direction must be either 'above' or 'below'.")

    if len(indices) == 0:
        return None

    return int(indices[0])


def estimate_tribofilm_thickness(
    height: np.ndarray,
    force: np.ndarray,
    current: np.ndarray,
    force_threshold: float = 25_000_000.0,
    current_threshold: float = 2_000.0,
    current_direction: str = "above",
) -> Dict[str, float]:
    """
    Estimate apparent tribofilm thickness from force and current curves.

    Parameters
    ----------
    height : np.ndarray
        Height or displacement data in metres.
    force : np.ndarray
        Force signal.
    current : np.ndarray
        Current signal.
    force_threshold : float
        Threshold used to detect the force-gradient transition.
    current_threshold : float
        Threshold used to detect the current-gradient transition.
    current_direction : str
        Direction of current-gradient threshold crossing.

    Returns
    -------
    dict
        Detected transition positions and estimated film thickness.
    """
    processed = calculate_derivatives(height, force, current)

    force_index = find_first_threshold_crossing(
        processed["d_force_d_height"],
        threshold=force_threshold,
        direction="above",
    )

    current_index = find_first_threshold_crossing(
        processed["d_current_d_height"],
        threshold=current_threshold,
        direction=current_direction,
    )

    if force_index is None:
        raise ValueError("No force-gradient transition was detected.")

    if current_index is None:
        raise ValueError("No current-gradient transition was detected.")

    height_force = processed["height"][force_index]
    height_current = processed["height"][current_index]

    thickness_m = height_current - height_force
    thickness_nm = abs(thickness_m) * 1e9

    return {
        "force_index": force_index,
        "current_index": current_index,
        "height_force_m": float(height_force),
        "height_current_m": float(height_current),
        "thickness_nm": float(thickness_nm),
    }


def analyse_curve_csv(input_csv: str | Path) -> Dict[str, float]:
    """
    Analyse a CSV file containing height, force and current columns.
    """
    input_csv = Path(input_csv)
    data = pd.read_csv(input_csv)

    required_columns = {"height_m", "force", "current"}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    result = estimate_tribofilm_thickness(
        height=data["height_m"].to_numpy(),
        force=data["force"].to_numpy(),
        current=data["current"].to_numpy(),
    )

    result["file"] = input_csv.name
    return result


if __name__ == "__main__":
    example_file = Path("data/example_force_current_curve.csv")
    result = analyse_curve_csv(example_file)

    print("Estimated tribofilm thickness analysis")
    print("--------------------------------------")
    for key, value in result.items():
        print(f"{key}: {value}")
