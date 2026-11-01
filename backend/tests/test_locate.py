"""locate_pending (D-023): one ItemLocation per RawItem, "located" or "none",
re-checked when the gazetteer changes. Isolated temp SQLite; item texts are
genuine captured t.me fixture posts and collected excerpts."""

from __future__ import annotations

from pathlib import Path

from app.database import SessionLocal, init_db
from app.geo.locate import locate_pending
from app.models import ItemLocation, RawItem, Source

init_db()

QABATIYA = 'عاجل| قوة خاصة من جيش الاحتلال تحاصر منزلا في بلدة قباطية بجنين وتطلق تجاهه قذائف "إنيرجا".'  # PIC, item 2817
NO_PLACE = (
    "Iran International establishes scholarship in memory of presenter Farahnaz Espad\n\n"
    "Iran International has established an annual postgraduate scholarship in memory of Farahnaz Espad."
)  # Iran International English, item 226 (first sentence of the body)


def _items(db, texts):
    source = Source(name="locate-test source", url="https://example.invalid/locate", language="ar", type="rss", kind="rss", active=False)
    db.add(source)
    db.flush()
    rows = [
        RawItem(source_id=source.id, original_lang="ar", original_text=t, url=f"https://example.invalid/locate/{i}", content_hash=f"locate-{i}-{id(t)}")
        for i, t in enumerate(texts)
    ]
    db.add_all(rows)
    db.commit()
    return [r.id for r in rows]


def _row(db, item_id):
    return db.query(ItemLocation).filter_by(raw_item_id=item_id).one()


def test_located_and_none_are_both_recorded():
    with SessionLocal() as db:
        located_id, none_id = _items(db, [QABATIYA, NO_PLACE])
        locate_pending(db, version="test-v1")
        located, none = _row(db, located_id), _row(db, none_id)
        assert (located.status, located.country, located.precision, located.matched_text) == ("located", "Palestine", "city", "قباطية")
        assert (none.status, none.place_name, none.latitude) == ("none", None, None)


def test_a_second_run_checks_nothing_new():
    with SessionLocal() as db:
        _items(db, [QABATIYA])
        locate_pending(db, version="test-v2")
        assert locate_pending(db, version="test-v2").checked == 0


def test_a_new_gazetteer_version_rechecks_every_item_in_place():
    with SessionLocal() as db:
        (item_id,) = _items(db, [QABATIYA])
        locate_pending(db, version="test-v3")
        result = locate_pending(db, version="test-v4")
        assert result.checked >= 1
        assert db.query(ItemLocation).filter_by(raw_item_id=item_id).count() == 1
        assert _row(db, item_id).gazetteer_version == "test-v4"
