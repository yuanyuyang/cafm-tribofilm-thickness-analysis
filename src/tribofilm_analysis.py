"""
tribofilm_analysis.py

Python workflow for estimating nanoscale tribofilm thickness from
conductive-AFM force/current curves.

The original research workflow extracts force, current and height curves from
Gwyddion-compatible .spm files using the `gwy` module. A CSV-based example is
also provided to make the core analysis method easier to inspect and test
outside the Gwyddion environment.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd


def calculate_derivatives(
    force: np.ndarray,
    current: np.ndarray,
    height: np.ndarray,
) -> Dict[str, np.ndarray]:
    """
    Calculate force and current derivatives with respect to height.

    Parameters
    ----------
    force : np.ndarray
        Force signal extracted from the force curve.
    current : np.ndarray
        Current signal extracted from the current curve.
    height : np.ndarray
        Height or displacement signal, normally extracted from the current
        curve x-data in the Gwyddion workflow.

    Returns
    -------
    dict
        Dictionary containing force, current, height, d_force_d_height and
        d_current_d_height.
    """
    force = np.asarray(force, dtype=float)
    current = np.asarray(current, dtype=float)
    height = np.asarray(height, dtype=float)

    if not (len(force) == len(current) == len(height)):
        raise ValueError("force, current and height must have the same length.")

    if len(height) < 3:
        raise ValueError("At least three data points are required.")

    diff_height = np.diff(height)

    if np.any(diff_height == 0):
        raise ValueError("Height data contains repeated values, causing division by zero.")

    diff_force = np.diff(force) / diff_height
    diff_current = np.diff(current) / diff_height

    # Match the original workflow: append one value so derivative arrays have
    # the same length as the original curves.
    diff_force = np.append(diff_force, 0.0)
    diff_current = np.append(diff_current, 0.0)

    return {
        "force": force,
        "current": current,
        "height": height,
        "d_force_d_height": diff_force,
        "d_current_d_height": diff_current,
    }


def find_first_threshold_crossing(
    signal: np.ndarray,
    threshold: float,
    direction: str = "above",
) -> Optional[int]:
    """
    Find the first index where a signal crosses a threshold.

    This replaces the original np.argmax(signal > threshold) approach, because
    np.argmax returns 0 even when no threshold crossing exists.
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
    force: np.ndarray,
    current: np.ndarray,
    height: np.ndarray,
    force_threshold: float = 25.0,
    current_threshold: float = 0.015,
    current_direction: str = "above",
    height_to_nm_factor: float = 1e9,
) -> Dict[str, float]:
    """
    Estimate apparent tribofilm thickness from force/current curves.

    This function preserves the logic of the original Gwyddion-based script:

    - force transition: first dForce/dHeight > force_threshold
    - current transition: first dCurrent/dHeight > current_threshold
    - raw thickness: height_force - height_current
    - if raw thickness is positive, film thickness is set to 0
    - otherwise, absolute thickness is converted to nm

    Parameters
    ----------
    force : np.ndarray
        Force signal.
    current : np.ndarray
        Current signal.
    height : np.ndarray
        Height or displacement signal.
    force_threshold : float
        Threshold for detecting the force-gradient transition.
    current_threshold : float
        Threshold for detecting the current-gradient transition.
    current_direction : str
        Direction for current-gradient threshold crossing.
    height_to_nm_factor : float
        Conversion factor from the height unit to nm. The original script uses
        1e9, assuming height is in metres.

    Returns
    -------
    dict
        Transition indices, transition heights and estimated film thickness.
    """
    processed = calculate_derivatives(force=force, current=current, height=height)

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

    raw_thickness = height_force - height_current

    # Preserve the original logic:
    # if height_force is greater than height_current, the film thickness is set to 0.
    if raw_thickness > 0:
        thickness = 0.0
    else:
        thickness = abs(raw_thickness)

    thickness_nm = thickness * height_to_nm_factor

    return {
        "force_index": force_index,
        "current_index": current_index,
        "height_force": float(height_force),
        "height_current": float(height_current),
        "raw_thickness": float(raw_thickness),
        "thickness_nm": float(thickness_nm),
    }


def extract_curves_from_gwyddion_container(container) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Extract force, current and height curves from a Gwyddion data container.

    This follows the original workflow:
    - use the minimum container key for the force curve;
    - use the next key, min_key + 1, for the current curve;
    - use current_curve.get_xdata() as the height/displacement signal.

    The exact container key structure may depend on how the .spm files were
    generated or imported into Gwyddion.
    """
    min_key = min(container.keys())

    force_curve = container[min_key].get_curve(0)
    current_curve = container[min_key + 1].get_curve(0)

    force = force_curve.get_ydata()
    current = current_curve.get_ydata()
    height = current_curve.get_xdata()

    return np.asarray(force), np.asarray(current), np.asarray(height)


def analyse_spm_file(
    spm_file: str | Path,
    force_threshold: float = 25.0,
    current_threshold: float = 0.015,
    current_direction: str = "above",
) -> Dict[str, float]:
    """
    Analyse one .spm file using the Gwyddion Python module.

    This function requires the `gwy` module and should be run inside an
    environment where Gwyddion's Python interface is available.
    """
    try:
        import gwy
    except ImportError as exc:
        raise ImportError(
            "The `gwy` module is required to analyse .spm files. "
            "Run this script in a Gwyddion Python environment."
        ) from exc

    spm_file = Path(spm_file)
    container = gwy.gwy_file_load(str(spm_file))

    force, current, height = extract_curves_from_gwyddion_container(container)

    result = estimate_tribofilm_thickness(
        force=force,
        current=current,
        height=height,
        force_threshold=force_threshold,
        current_threshold=current_threshold,
        current_direction=current_direction,
    )

    result["file"] = spm_file.name
    return result


def analyse_curve_csv(
    input_csv: str | Path,
    force_threshold: float = 25.0,
    current_threshold: float = 0.015,
    current_direction: str = "above",
) -> Dict[str, float]:
    """
    Analyse a CSV file containing force, current and height columns.

    This function is included for demonstration and testing outside the
    Gwyddion environment. The original research workflow uses .spm files.
    """
    input_csv = Path(input_csv)
    data = pd.read_csv(input_csv)

    required_columns = {"height", "force", "current"}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    result = estimate_tribofilm_thickness(
        force=data["force"].to_numpy(),
        current=data["current"].to_numpy(),
        height=data["height"].to_numpy(),
        force_threshold=force_threshold,
        current_threshold=current_threshold,
        current_direction=current_direction,
    )

    result["file"] = input_csv.name
    return result


def batch_analyse_spm_folder(
    input_folder: str | Path,
    output_csv: str | Path,
    force_threshold: float = 25.0,
    current_threshold: float = 0.015,
    current_direction: str = "above",
) -> pd.DataFrame:
    """
    Batch analyse all .spm files in a folder and export thickness results.
    """
    input_folder = Path(input_folder)
    output_csv = Path(output_csv)

    results = []

    for spm_file in sorted(input_folder.glob("*.spm")):
        try:
            result = analyse_spm_file(
                spm_file,
                force_threshold=force_threshold,
                current_threshold=current_threshold,
                current_direction=current_direction,
            )
            results.append(result)
        except Exception as exc:
            results.append({
                "file": spm_file.name,
                "error": str(exc),
            })

    result_table = pd.DataFrame(results)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result_table.to_csv(output_csv, index=False)

    return result_table


if __name__ == "__main__":
    # CSV example for users who do not have access to the Gwyddion Python module.
    example_file = Path("data/example_force_current_curve.csv")

    result = analyse_curve_csv(
        example_file,
        force_threshold=25.0,
        current_threshold=0.015,
        current_direction="above",
    )

    print("Estimated tribofilm thickness analysis")
    print("--------------------------------------")
    for key, value in result.items():
        print(f"{key}: {value}")
