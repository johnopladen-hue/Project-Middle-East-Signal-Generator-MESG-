"""Item geolocation from place names in the original text (D-023, map item geolocation).

Pure and offline: `locate_text` matches an item's ORIGINAL-language text
against the committed GeoNames-derived gazetteer (`gazetteer.json`, built by
`build_gazetteer.py`). It never reads NLLB output: the 2026-10-11 spot-check
found NLLB gets place names wrong (findings.md), and a wrong place on a map
is worse than none. No match means no location - the item stays unlocated,
never a guessed pin (Keel P11).

Matching, in order:
- Normalise per script: Arabic/Persian letter variants and diacritics,
  Hebrew niqqud and geresh, Latin case and accents.
- Slide 3-, 2- and 1-word windows over the words, longest first, so
  "خان يونس" beats a bare "يونس" and "Tel Aviv" beats "Aviv".
- Arabic and Hebrew attach one-letter prefixes to the next word (Arabic
  "بغزة" = "in Gaza", Hebrew "בעזה" = "in Gaza"). The first word of a window
  may drop one of them, or two when the first is "and"; a window only counts
  if what remains is a gazetteer name, and a stripped match only counts for a
  major place (see Place.major).
- Latin names match only when the text capitalises them ("Gaza", not "gaza"),
  since lower-case Latin alternates collide with ordinary English words.

Choosing one place per item: the headline (first line) beats the body;
within each, a city beats a province beats a country; ties go to the first
mention. The matched words are returned so the UI can show exactly why an
item sits where it does.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

GAZETTEER_PATH = Path(__file__).resolve().parent / "gazetteer.json"

PRECISION_RANK = {"city": 0, "province": 1, "country": 2}

# Explicit escapes throughout (findings.md 2026-11-01: a pasted range lost its
# end character and matched hyphens).
_ARABIC_DIACRITICS = re.compile("[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")  # harakat, Quranic marks, tatweel
_HEBREW_MARKS = re.compile("[\u0591-\u05C7\u05F3\u05F4'\"\u2019]")  # niqqud, geresh, gershayim, quotes
_ARABIC_MAP = str.maketrans({
    "\u0623": "\u0627", "\u0625": "\u0627", "\u0622": "\u0627", "\u0671": "\u0627",  # alef variants -> bare alef
    "\u0649": "\u064A", "\u06CC": "\u064A",  # alef maqsura, Persian yeh -> Arabic yeh
    "\u06A9": "\u0643",  # Persian keheh -> Arabic kaf
    "\u0629": "\u0647",  # teh marbuta -> heh
})
_ZWNJ = "\u200C"
# Letters plus the marks that sit inside words (Arabic harakat, tatweel, Hebrew
# niqqud), but not Arabic punctuation or Arabic-Indic digits.
_WORD = re.compile(
    "[\u0621-\u065F\u0670-\u06D3\u06FA-\u06FF\u0640\u0750-\u077F"
    "\u05D0-\u05EA\u0591-\u05C7"
    "A-Za-z\u00C0-\u024F]+"
)
_ARABIC_LETTER = re.compile("[\u0621-\u06FF\u0750-\u077F]")
_HEBREW_LETTER = re.compile("[\u05D0-\u05EA]")

# Kaf ("like") is left out: rare as a prefix in news Arabic, and Persian words
# beginning with keheh (normalised to kaf) lost it and matched Egypt.
ARABIC_PREFIXES = "\u0648\u0641\u0628\u0644"  # waw, feh, beh, lam
HEBREW_PREFIXES = "\u05D5\u05D4\u05D1\u05DC\u05DE\u05E9\u05DB"  # vav, he, bet, lamed, mem, shin, kaf
_AL = "\u0627\u0644"  # the article al-
_LIL = "\u0644\u0644"  # li- + al- with the alef dropped

MIN_LETTERS = {"arabic": 3, "hebrew": 3, "latin": 4}
MAX_WINDOW = 3


def script_of(word: str) -> str:
    if _ARABIC_LETTER.search(word):
        return "arabic"
    if _HEBREW_LETTER.search(word):
        return "hebrew"
    return "latin"


def normalize(text: str) -> str:
    """One normal form for both gazetteer names and item text."""
    text = text.replace(_ZWNJ, "")
    text = _ARABIC_DIACRITICS.sub("", text).translate(_ARABIC_MAP)
    text = _HEBREW_MARKS.sub("", text)
    text = unicodedata.normalize("NFKD", text)
    # NFKD splits e.g. waw-with-hamza into waw + hamza above, and e-acute into
    # e + accent: drop every combining mark that remains.
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.casefold()


def name_key(name: str) -> str | None:
    """Gazetteer-side key: normalised words joined by single spaces, or None
    if the name is too short to match safely."""
    words = _WORD.findall(normalize(name))
    if not words or len(words) > MAX_WINDOW:
        return None
    letters = sum(len(w) for w in words)
    if letters < MIN_LETTERS[script_of(words[0])]:
        return None
    return " ".join(words)


def _prefix_variants(word: str) -> list[str]:
    """`word` itself, then `word` with up to two attached one-letter prefixes
    removed (Arabic and Hebrew only). Arabic "لل" before a name restores the
    article: "للخليل" -> "الخليل"."""
    variants = [word]
    script = script_of(word)
    if script == "arabic":
        prefixes = ARABIC_PREFIXES
    elif script == "hebrew":
        prefixes = HEBREW_PREFIXES
    else:
        return variants
    conjunction = prefixes[0]  # Arabic waw / Hebrew vav: "and"
    frontier = [word]
    for step in range(2):
        nxt = []
        for w in frontier:
            # A second prefix only after "and" ("and-in-Gaza"); two arbitrary
            # letters off a word made Hebrew "that submitted" into Jish.
            if step == 1 and word[0] != conjunction:
                break
            if len(w) > 3 and w[0] in prefixes:
                nxt.append(w[1:])
            if script == "arabic" and w.startswith(_LIL) and len(w) > 4:
                nxt.append(_AL + w[2:])
        variants.extend(nxt)
        frontier = nxt
    return variants


@dataclass(frozen=True)
class Place:
    geonameid: int
    name: str  # GeoNames primary name (Latin)
    country: str  # MESG country name, as in country_centroids.json / AorMembership
    lat: float
    lon: float
    precision: str  # city | province | country
    major: bool = True  # pop >= 15,000, an administrative seat, a province or a country


@dataclass(frozen=True)
class Match:
    place: Place
    matched_text: str  # the item's own words that matched, as written
    in_headline: bool
    position: int  # word index in the whole text


class Gazetteer:
    def __init__(self, places: list[Place], names: dict[str, int], stop_keys: frozenset[str] = frozenset()):
        self.places = places
        self.names = names
        self.stop_keys = stop_keys

    @classmethod
    def from_json(cls, data: dict) -> Gazetteer:
        places = [Place(*row) for row in data["places"]]
        return cls(places, data["names"], frozenset(data.get("stop_keys", [])))

    def find(self, text: str) -> list[Match]:
        """Every non-overlapping match in `text`, longest window first."""
        text = text.replace(_ZWNJ, "")
        # The headline is the first line with words, skipping Telegram's own
        # "Forwarded from <name>" attribution line.
        headline_start = headline_end = offset = 0
        for line in text.splitlines():
            count = len(_WORD.findall(line))
            if count and not line.strip().startswith("Forwarded from"):
                headline_start, headline_end = offset, offset + count
                break
            offset += count

        raw_words = _WORD.findall(text)
        norm_words = [normalize(w) for w in raw_words]
        taken = [False] * len(raw_words)
        matches: list[Match] = []
        for size in range(MAX_WINDOW, 0, -1):
            for start in range(len(raw_words) - size + 1):
                if any(taken[start:start + size]):
                    continue
                first_raw = raw_words[start]
                if script_of(first_raw) == "latin" and not first_raw[0].isupper():
                    continue
                rest = norm_words[start + 1:start + size]
                for variant_number, first in enumerate(_prefix_variants(norm_words[start])):
                    key = " ".join([first, *rest])
                    if key in self.stop_keys:
                        # A stop phrase consumes its words, so "Iran International"
                        # (an outlet) is never re-read as "Iran".
                        for i in range(start, start + size):
                            taken[i] = True
                        break
                    index = self.names.get(key)
                    if index is not None and variant_number and not self.places[index].major:
                        # Only major places match with a prefix stripped: small
                        # villages named like common words did otherwise.
                        continue
                    if index is not None:
                        for i in range(start, start + size):
                            taken[i] = True
                        matches.append(
                            Match(
                                place=self.places[index],
                                matched_text=" ".join(raw_words[start:start + size]),
                                in_headline=headline_start <= start < headline_end,
                                position=start,
                            )
                        )
                        break
        matches.sort(key=lambda m: m.position)
        return matches

    def locate(self, text: str) -> Match | None:
        """The one place an item is put on the map, or None."""
        matches = self.find(text)
        if not matches:
            return None
        return min(matches, key=lambda m: (not m.in_headline, PRECISION_RANK[m.place.precision], m.position))


@lru_cache(maxsize=1)
def load_gazetteer(path: Path = GAZETTEER_PATH) -> Gazetteer:
    return Gazetteer.from_json(json.loads(path.read_text(encoding="utf-8")))


def locate_text(text: str) -> Match | None:
    return load_gazetteer().locate(text)
