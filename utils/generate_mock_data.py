from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "measurements.csv"


def generate_measurements(samples: int = 200, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    center_lat = 41.9028
    center_lon = 12.4964

    latitudes = center_lat + rng.uniform(-0.045, 0.045, samples)
    longitudes = center_lon + rng.uniform(-0.06, 0.06, samples)

    measurement_points = np.column_stack((latitudes, longitudes))

    base_stations = np.array(
        [
            [center_lat + 0.01, center_lon - 0.015],
            [center_lat - 0.018, center_lon + 0.022],
            [center_lat + 0.025, center_lon + 0.008],
            [center_lat - 0.03, center_lon - 0.028],
            [center_lat + 0.002, center_lon + 0.04],
        ]
    )

    df = pd.DataFrame(
        {
            "LATITUDE": latitudes,
            "LONGITUDE": longitudes,
        }
    )

    terrain_profile = (
        3.5 * np.sin((latitudes - center_lat) * 120)
        + 2.8 * np.cos((longitudes - center_lon) * 100)
    )

    for idx, station in enumerate(base_stations, start=1):
        delta = measurement_points - station
        distance_km = np.sqrt((delta[:, 0] * 111.0) ** 2 + (delta[:, 1] * 85.0) ** 2)
        distance_km = np.clip(distance_km, 0.08, None)
        distance_m = distance_km * 1000.0

        large_scale_rsrp = -46.0 - 22.0 * np.log10(distance_m)
        site_bias = rng.normal(0, 2.0)
        shadowing = rng.normal(0, 4.5, samples)
        fast_fading = (
            2.2 * np.sin(distance_km * 13 + idx)
            + 1.8 * np.cos(distance_km * 17 - idx / 2)
            + rng.normal(0, 1.2, samples)
        )

        rsrp = large_scale_rsrp + terrain_profile + site_bias + shadowing + fast_fading
        df[f"RSRP_{idx}"] = np.clip(rsrp, -140, -65).round(2)

    return df.round({"LATITUDE": 6, "LONGITUDE": 6})


def main() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_measurements()
    df.to_csv(DATA_PATH, index=False)
    print(f"Generated {len(df)} samples at {DATA_PATH}")


if __name__ == "__main__":
    main()
