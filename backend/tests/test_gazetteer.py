"""Item geolocation from the original text (D-023). Pure, offline, against the
committed GeoNames-derived gazetteer. Every text is genuine: a captured t.me
fixture page (tests/fixtures/telegram_*.html) or a verbatim excerpt of an item
MESG collected on 2026-11-01 (item id and source named beside it)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.geo.gazetteer import Gazetteer, Place, _prefix_variants, load_gazetteer, normalize
from app.ingestion.telegram_collector import parse_channel_page

FIXTURES = Path(__file__).parent / "fixtures"
GAZ = load_gazetteer()


def _post(fixture: str, handle: str, post_id: int) -> str:
    html = (FIXTURES / f"telegram_{fixture}.html").read_text(encoding="utf-8")
    page = parse_channel_page(html, handle, now=datetime(2026, 10, 12, tzinfo=timezone.utc))
    return next(p.text for p in page.posts if p.post_id == post_id)


# Palestinian Information Center, item 2817 (2026-11-01), verbatim.
QABATIYA = 'عاجل| قوة خاصة من جيش الاحتلال تحاصر منزلا في بلدة قباطية بجنين وتطلق تجاهه قذائف "إنيرجا".'
# Iran International English, item 232: headline names a country, the body a city and the outlet.
IRAN_INTL_232 = (
    "Iran wrong to expect midterms to restrain Trump, former US official says\n\n"
    "Tehran is making a “total miscalculation” if it believes the US midterm elections will constrain "
    "President Donald Trump’s actions against Iran, former senior US official Morgan Ortagus told Iran International."
)
# Iran International English, item 226: the only "Iran" is the outlet's own name.
IRAN_INTL_226 = (
    "Iran International establishes scholarship in memory of presenter Farahnaz Espad\n\n"
    "Iran International has established an annual postgraduate scholarship in memory of Farahnaz Espad, "
    "one of the channel’s first presenters, who died in August after eight years with the channel."
)
# Arutz 7, item 95: "שהגיש" = "that submitted"; two arbitrary letters off it once made the village of Jish.
ARUTZ7_95 = "העתירה שהגיש מטה"  # "העתירה שהגיש מטה", from the item's body
# HaMoked News, item 5758: "ברמה" = "at a level".
HAMOKED_5758 = "הדרג המדיני ברמה"  # "הדרג המדיני ברמה"


def test_a_small_village_named_exactly_is_located_at_city_level():
    match = GAZ.locate(QABATIYA)
    assert (match.place.name, match.place.country, match.place.precision) == ("Qabāţīyah", "Palestine", "city")


def test_the_first_city_named_wins_when_two_are_in_the_headline():
    assert GAZ.locate(QABATIYA).matched_text == "قباطية"  # قباطية, before بجنين


def test_a_hebrew_prefixed_major_place_is_located():
    match = GAZ.locate(_post("abualiexpress_reply", "abualiexpress", 131721))
    assert (match.place.name, match.matched_text) == ("Gaza", "בעזה")  # בעזה, "in Gaza"


def test_a_small_border_village_in_a_real_alert_is_located():
    match = GAZ.locate(_post("pikudhaoref_he_p1", "PikudHaOref_all", 36060))
    assert (match.place.country, match.place.precision) == ("Israel", "city")
    assert match.place.name == "‘Aramsha"


def test_persian_text_locates_riyadh():
    assert GAZ.locate(_post("bbcpersian_fa", "bbcpersian", 293179)).place.name == "Riyadh"


def test_the_headline_beats_the_body_even_when_the_body_is_more_precise():
    match = GAZ.locate(IRAN_INTL_232)
    assert (match.place.precision, match.in_headline) == ("country", True)


def test_an_outlet_name_is_a_stop_phrase_and_consumes_its_words():
    assert GAZ.locate(IRAN_INTL_226) is None


def test_a_body_city_is_found_when_the_headline_names_nothing():
    matches = GAZ.find(IRAN_INTL_232)
    assert [(m.place.name, m.in_headline) for m in matches][:2] == [("Islamic Republic of Iran", True), ("Tehran", False)]


def test_a_second_prefix_is_only_stripped_after_and():
    word = normalize("שהגיש")  # שהגיש
    assert _prefix_variants(word) == [word, word[1:]]
    assert GAZ.locate(ARUTZ7_95) is None


def test_a_prefixed_match_is_refused_for_a_minor_place_and_allowed_for_a_major_one():
    # The real GeoNames row (IL.txt, geonameid 293793, pop 7,728: below the 15,000 "major" line).
    rama = dict(geonameid=293793, name="Rama", country="Israel", lat=32.9386, lon=35.3664, precision="city")
    key = normalize("רמה")  # רמה
    minor = Gazetteer([Place(**rama, major=False)], {key: 0})
    major = Gazetteer([Place(**rama, major=True)], {key: 0})
    assert minor.locate(HAMOKED_5758) is None
    assert major.locate(HAMOKED_5758).place.name == "Rama"


def test_lower_case_latin_never_matches():
    assert GAZ.locate("the gaza strip") is None
    assert GAZ.locate("the Gaza Strip").place.precision == "province"


def test_arabic_punctuation_and_digits_are_not_letters():
    assert GAZ.find("غزة، 2026")[0].matched_text == "غزة"  # "غزة،" -> "غزة"


def test_text_with_no_place_name_is_not_located():
    assert GAZ.locate(_post("farsna_fa", "farsna", 467729)) is None
