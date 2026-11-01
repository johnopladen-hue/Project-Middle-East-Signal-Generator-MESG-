"""Regenerates app/geo/gazetteer.json (D-023, map item geolocation): the
offline place-name index `app/geo/gazetteer.py` matches item text against.

Source: the GeoNames per-country dumps for the 22 CENTCOM AOR countries
(https://download.geonames.org/export/dump/<CC>.zip, CC BY 4.0 - attribution
"GeoNames, geonames.org" is carried in the output and shown on the map).
Download them into backend/data/geonames/ (gitignored) first; this script
does not fetch anything. Not run automatically; the output is committed,
like country_centroids.json.

    python -m app.geo.build_gazetteer

What is kept, and why:
- Country names (PCL*), placed on the existing country centroid so a
  country-level item sits where the map's organizations already do.
- First-level provinces (ADM1).
- Populated places (P), excluding sections, abandoned, destroyed and
  historical ones. In the core theatre (CORE_COUNTRIES) every such place is
  kept, because small border villages are exactly where events get named
  (Arab al-Aramshe, 2026-10-11) and GeoNames often records population 0 even
  for district seats (Nabatieh). Elsewhere only places of MIN_POPULATION or
  more, plus capitals and provincial seats.
- Per place: every Arabic-script and Hebrew-script name, the primary and
  ASCII names, and Latin alternates that are capitalised, 4+ letters, not
  all-caps (airport codes) and digit-free.

When two places share a name key, the more important one wins: capital,
then country, then provincial seat, then province, then other places, then
by population. So a country name never resolves to a namesake village.
Keys in STOP_KEYS are never matched (see findings.md for the evidence that
put each one there).
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from pathlib import Path

from app.geo.gazetteer import GAZETTEER_PATH, name_key, script_of

DUMP_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "geonames"
CENTROIDS_PATH = Path(__file__).resolve().parent / "country_centroids.json"

COUNTRIES = {
    "AF": "Afghanistan", "BH": "Bahrain", "EG": "Egypt", "IR": "Iran", "IQ": "Iraq",
    "IL": "Israel", "JO": "Jordan", "KZ": "Kazakhstan", "KW": "Kuwait", "KG": "Kyrgyzstan",
    "LB": "Lebanon", "OM": "Oman", "PK": "Pakistan", "PS": "Palestine", "QA": "Qatar",
    "SA": "Saudi Arabia", "SY": "Syria", "TJ": "Tajikistan", "TM": "Turkmenistan",
    "AE": "United Arab Emirates", "UZ": "Uzbekistan", "YE": "Yemen",
}
CORE_COUNTRIES = {"IL", "PS", "LB", "SY", "JO", "IQ"}
MIN_POPULATION = 15000
CORE_MIN_POPULATION = 1000
EXCLUDED_PPL = {"PPLX", "PPLQ", "PPLW", "PPLH", "PPLCH"}
ADMIN_SEATS = {"PPLC", "PPLA", "PPLA2"}

# Words that collide with GeoNames names often enough to mislocate items,
# each with the ordinary meaning that made it a false match.
# Filled from the evidence in findings.md (D-023 build), never by guess.
STOP_WORDS: dict[str, str] = {
    'سال': 'year',
    'خبر': 'news (also Khobar)',
    'مهر': 'Mehr agency / seal',
    'فارس': 'Fars agency (also Fars Province)',
    'کامل': 'complete',
    'برابر': 'equal / against',
    'مرکزی': 'central',
    'پیشین': 'previous',
    'میزان': 'rate / Mizan agency',
    'آستانه': 'threshold (also Astana)',
    'داریم': 'we have',
    'سنگین': 'heavy',
    'صحنه': 'scene',
    'جرم': 'crime',
    'باران': 'rain',
    'گلستان': 'Golestan Province, but resolves to Guliston (Uzbekistan)',
    'عاجل': 'urgent',
    'مدينة': 'city',
    'المدينة': 'the city',
    'الميادين': 'Al Mayadeen channel signature (also Mayadin)',
    'الأحد': 'Sunday',
    'وقف': 'halt / ceasefire',
    'جديدة': 'new',
    'الجديدة': 'the new',
    'الثورة': 'the revolution',
    'الحكومة': 'the government',
    'البلاد': 'the country',
    'العاصمة': 'the capital',
    'رصد': 'monitoring',
    'سند': 'document (also Sindh)',
    'كشفت': 'revealed',
    'صرفاً': 'merely',
    'الشهداء': 'the martyrs',
    'الاتحاد': 'the union',
    'جاسم': 'given name',
    'وزارة': 'ministry',
    'فيديو': 'video',
    'محمد': 'given name',
    'صور': 'photos (also Tyre and Sur: lost on purpose, see findings)',
    'عمان': 'Amman or Oman, same spelling',
    'בחירות': 'elections',
    'מחמד': 'given name',
    'מוחמד': 'given name',
    'מקום': 'place / instead',
    'אזור': 'area',
    'מלחמה': 'war',
    'מתן': 'giving',
    'שהם': 'that they',
    'לשלם': 'to pay',
    'לפיד': 'Lapid (politician)',
    'Israeli': 'adjective',
    'Saudi': 'adjective',
    'Yemeni': 'adjective',
    'Abbas': 'Mahmoud Abbas (Fort Abbas)',
    'Hamas': 'movement (Hamis)',
    'לכאורה': 'allegedly',
    'סגור': 'closed',
    'משמרות': 'shifts',
    'שחורה': 'black',
    'ניצן': 'bud / given name',
    'מכה': 'a blow (also Mecca)',
    'الجمعة': 'Friday',
    'الهجرة': 'migration',
    'بلد': 'country',
    'سالم': 'healthy / given name',
    'الشرقية': 'the eastern (Saudi or Egyptian)',
    'نور': 'light / given name',
    'اوج': 'peak',
    'بدهی': 'debt',
    'خواهان': 'seeking',
    'Naim': 'given name',
    'Gazan': 'adjective (also a Latin alternate of Jizan)',
    'רמה': 'level (also Rama)',
    'Iran International': 'outlet name',
    'ایران اینترنشنال': 'outlet name',
    'Al Jazeera': 'outlet name',
    'الجزيرة': 'Al Jazeera (also Al Jazirah)',
    'ישראל ביתנו': 'party name (Yisrael Beiteinu)',
    'ولایت': 'guardianship (also Jam)',
    'המודיעין': "the intelligence services (Modi'in itself still matches as במודיעין)",
    'רחובות': 'streets (also Rehovot: lost on purpose)',
    'الخميس': 'Thursday',
    'الاثنين': 'Monday',
    'الثلاثاء': 'Tuesday',
    'الأربعاء': 'Wednesday',
    'السبت': 'Saturday',
    'شنبه': 'Saturday',
    'یکشنبه': 'Sunday',
    'دوشنبه': 'Monday (also Dushanbe)',
    'سه\u200cشنبه': 'Tuesday',
    'چهارشنبه': 'Wednesday',
    'پنجشنبه': 'Thursday',
    'جمعه': 'Friday',
    'יקיר': 'dear / surname (also Yaqqir)',
    'دوراً': 'a role',
    'دورا': 'a role (also Dura)',
    'المصدر': 'the source',
    'قدس': 'Quds News Network (Jerusalem is still matched as القدس)',
    'مقر': 'headquarters',
    'הגיש': 'submitted',
    'North': 'direction (Latin alternate of North Lebanon)',
    'South': 'direction',
    'East': 'direction',
    'West': 'direction',
    'معبر': "a crossing (also Ma'bar)",
    'ساري': 'in effect (also Sari)',
    'הגבלה': 'restriction (also Jablah)',
    'הגבלות': 'restrictions',
}
STOP_KEYS: set[str] = {key for key in map(name_key, STOP_WORDS) if key is not None}

_DIGIT = re.compile(r"\d")


def _priority(feature_class: str, feature_code: str) -> int:
    if feature_code == "PPLC":
        return 0
    if feature_code.startswith("PCL"):
        return 1
    if feature_code == "PPLA":
        return 2
    if feature_code == "ADM1":
        return 3
    if feature_code == "PPLA2":
        return 4
    return 5


def _names(row: list[str]) -> set[str]:
    primary, ascii_name, alternates = row[1], row[2], row[3]
    names = {primary, ascii_name}
    for alt in alternates.split(",") if alternates else []:
        alt = alt.strip()
        if not alt or _DIGIT.search(alt):
            continue
        if script_of(alt) in ("arabic", "hebrew"):
            names.add(alt)
        elif alt[:1].isupper() and not alt.isupper() and len(alt) >= 4:
            names.add(alt)
    return names


def _rows(code: str):
    with zipfile.ZipFile(DUMP_DIR / f"{code}.zip") as zf:
        with zf.open(f"{code}.txt") as f:
            yield from csv.reader(io.TextIOWrapper(f, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)


def build() -> dict:
    centroids = json.loads(CENTROIDS_PATH.read_text(encoding="utf-8"))
    places: list[list] = []
    best: dict[str, tuple[tuple[int, int], int]] = {}  # key -> (rank, place index)
    counts = {"country": 0, "province": 0, "city": 0}

    for code, country in COUNTRIES.items():
        for row in _rows(code):
            feature_class, feature_code = row[6], row[7]
            population = int(row[14] or 0)
            if feature_class == "A" and feature_code.startswith("PCL"):
                precision = "country"
                lon, lat = centroids[country]
            elif feature_class == "A" and feature_code == "ADM1":
                precision = "province"
                lat, lon = float(row[4]), float(row[5])
            elif feature_class == "P" and feature_code not in EXCLUDED_PPL:
                floor = CORE_MIN_POPULATION if code in CORE_COUNTRIES else MIN_POPULATION
                if population < floor and feature_code not in ADMIN_SEATS:
                    continue
                precision = "city"
                lat, lon = float(row[4]), float(row[5])
            else:
                continue

            index = len(places)
            major = precision != "city" or population >= MIN_POPULATION or feature_code in ADMIN_SEATS
            places.append([int(row[0]), row[1], country, round(lat, 4), round(lon, 4), precision, major])
            counts[precision] += 1
            rank = (_priority(feature_class, feature_code), -population)
            for name in _names(row):
                key = name_key(name)
                if key is None or key in STOP_KEYS:
                    continue
                if key not in best or rank < best[key][0]:
                    best[key] = (rank, index)

    used = sorted({index for _, index in best.values()})
    remap = {old: new for new, old in enumerate(used)}
    return {
        "attribution": "Place names: GeoNames (geonames.org), CC BY 4.0",
        "built_from": sorted(COUNTRIES),
        "counts": counts,
        "places": [places[i] for i in used],
        "names": {key: remap[index] for key, (_, index) in sorted(best.items())},
        "stop_keys": sorted(STOP_KEYS),
    }


def main() -> None:
    data = build()
    GAZETTEER_PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(
        f"Wrote {GAZETTEER_PATH}: {len(data['places'])} places with at least one usable name, "
        f"{len(data['names'])} name keys ({data['counts']} considered); "
        f"{GAZETTEER_PATH.stat().st_size / 1e6:.1f} MB"
    )


if __name__ == "__main__":
    main()
