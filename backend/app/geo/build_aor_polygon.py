"""Regenerates app/geo/aor_centcom.geojson (D-015, O-6): the CENTCOM AOR
polygon as the union of its member countries' borders, from Natural Earth's
1:50m admin-0 country boundaries (public domain, no attribution required -
see findings.md, 2026-09-13). Not run automatically; the precomputed output
is committed. Re-run after downloading data/naturalearth/ne_50m_admin_0_countries.geojson
(https://github.com/nvkelso/natural-earth-vector) if D-015's membership list changes.

    python -m app.geo.build_aor_polygon
"""

from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

# CENTCOM v1 membership per D-015 (CRS IF11428 v3, 2022-03-30). Natural
# Earth's admin-0 layer names the West Bank & Gaza territory "Palestine".
CENTCOM_MEMBERS = {
    "Afghanistan", "Bahrain", "Egypt", "Iran", "Iraq", "Israel", "Jordan",
    "Kazakhstan", "Kuwait", "Kyrgyzstan", "Lebanon", "Oman", "Pakistan",
    "Qatar", "Saudi Arabia", "Syria", "Tajikistan", "Turkmenistan",
    "United Arab Emirates", "Uzbekistan", "Yemen", "Palestine",
}

SOURCE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "naturalearth" / "ne_50m_admin_0_countries.geojson"
OUTPUT_PATH = Path(__file__).resolve().parent / "aor_centcom.geojson"


def build() -> None:
    data = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    geoms = []
    found = set()
    for feature in data["features"]:
        name = feature["properties"]["NAME"]
        if name in CENTCOM_MEMBERS:
            geoms.append(shape(feature["geometry"]))
            found.add(name)

    missing = CENTCOM_MEMBERS - found
    if missing:
        raise SystemExit(f"Missing countries in source data: {missing}")

    union = unary_union(geoms).simplify(0.01, preserve_topology=True)

    output = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "aor": "CENTCOM",
                    "member_count": len(geoms),
                    "source": "Natural Earth 1:50m admin-0 countries (public domain)",
                },
                "geometry": mapping(union),
            }
        ],
    }
    OUTPUT_PATH.write_text(json.dumps(output), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(geoms)} member countries)")


if __name__ == "__main__":
    build()
