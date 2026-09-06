from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db
from app.main import app
from app.models import Analysis, Divergence, RawItem, Source, SourceAssessment, Story, StoryItem

init_db()


def _build_full_story():
    with SessionLocal() as session:
        source = Source(name="Al Jazeera", url="https://aljazeera.com", language="Arabic", type="rss")
        session.add(source)
        session.flush()

        raw_item = RawItem(
            source_id=source.id,
            original_lang="Arabic",
            original_text="نص عربي",
            working_text="Arabic text",
            url="https://aljazeera.com/item",
            content_hash="hash123",
            fetched_at=datetime(2026, 9, 6, 8, 0, tzinfo=timezone.utc),
        )
        session.add(raw_item)
        session.flush()

        story = Story(title="Convoy movement reported", event_type="military_event", status="open")
        session.add(story)
        session.flush()

        session.add(StoryItem(story_id=story.id, raw_item_id=raw_item.id))

        analysis = Analysis(
            story_id=story.id,
            facts_json=[{"text": "Convoy observed.", "raw_item_ids": [raw_item.id]}],
            analysis_text="Multiple accounts describe convoy movement.",
            probability_grade=4,
            contrary_evidence=None,
        )
        session.add(analysis)
        session.flush()

        session.add(
            SourceAssessment(
                analysis_id=analysis.id,
                source_id=source.id,
                access_level="direct",
                reliability=0.8,
                rationale="Established outlet with on-ground stringer.",
            )
        )
        session.add(
            Divergence(
                story_id=story.id,
                in_region_summary="Local reports describe unusual convoy activity.",
                english_media_summary="English outlets have not yet reported this.",
                divergence_points=["English media silent so far"],
                convergence_points=[],
            )
        )
        session.commit()
        return story.id, raw_item.id


def test_get_missing_story_is_404():
    client = TestClient(app)
    response = client.get("/stories/999999")
    assert response.status_code == 404


def test_get_story_returns_full_detail():
    story_id, raw_item_id = _build_full_story()
    client = TestClient(app)

    response = client.get(f"/stories/{story_id}")
    assert response.status_code == 200
    body = response.json()

    assert body["title"] == "Convoy movement reported"
    assert body["probability_grade"] == 4
    assert body["has_corroborating_artefact"] is True
    assert body["facts"][0]["raw_item_ids"] == [raw_item_id]
    assert str(raw_item_id) in body["raw_items"]
    assert body["raw_items"][str(raw_item_id)]["source_name"] == "Al Jazeera"
    assert body["source_assessments"][0]["access_level"] == "direct"
    assert body["divergence"]["divergence_points"] == ["English media silent so far"]
    assert body["timeline"] == [raw_item_id]


def test_story_with_no_analysis_yet_has_null_grade():
    with SessionLocal() as session:
        story = Story(title="Unanalyzed story", status="open")
        session.add(story)
        session.commit()
        story_id = story.id

    client = TestClient(app)
    response = client.get(f"/stories/{story_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["probability_grade"] is None
    assert body["has_corroborating_artefact"] is False
    assert body["facts"] == []
