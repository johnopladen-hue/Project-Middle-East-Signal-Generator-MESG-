"""Regenerates app/geo/country_centroids.json (O-7): a small offline
country-name -> [lon, lat] lookup for CENTCOM v1 countries, computed from
Natural Earth's public-domain admin-0 boundaries. This is what backs
country-level location precision on the geo endpoint - no live geocoder
call (D-014's "no live geocoder in the gate"). Not run automatically; the
precomputed output is committed.

    python -m app.geo.build_country_centroids
"""

from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import shape

from app.geo.build_aor_polygon import CENTCOM_MEMBERS, SOURCE_PATH

OUTPUT_PATH = Path(__file__).resolve().parent / "country_centroids.json"


def build() -> None:
    data = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    centroids: dict[str, list[float]] = {}
    for feature in data["features"]:
        name = feature["properties"]["NAME"]
        if name in CENTCOM_MEMBERS:
            centroid = shape(feature["geometry"]).centroid
            centroids[name] = [round(centroid.x, 4), round(centroid.y, 4)]

    missing = CENTCOM_MEMBERS - centroids.keys()
    if missing:
        raise SystemExit(f"Missing countries in source data: {missing}")

    OUTPUT_PATH.write_text(json.dumps(centroids, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(centroids)} countries)")


if __name__ == "__main__":
    build()
