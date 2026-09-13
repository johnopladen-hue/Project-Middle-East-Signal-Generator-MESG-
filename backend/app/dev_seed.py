"""Synthetic dev-only seed data (D-011 first article, O-3).

Populates every built screen with fabricated Stories/Signals/Briefs/Sources/
Recipients themed to the v1 scope (D-008: Levantine Arabic + Iranian
Persian) so the app reads as MESG rather than an empty shell. Every row this
script creates is tagged with TAG below — no real data, no scraped content,
no real contact details. Run with `python -m app.dev_seed` from `backend/`
(idempotent: skips if already seeded; pass --reset to wipe and reseed).
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal, init_db, seed_dev_user
from app.grading import probability_grade
from app.models import (
    Analysis,
    Brief,
    Divergence,
    RawItem,
    Recipient,
    Signal,
    Source,
    SourceAccessLevel,
    SourceAssessment,
    Story,
    StoryItem,
)

TAG = "[SYNTHETIC — DEV SEED]"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _already_seeded(session) -> bool:
    return session.query(Source).filter(Source.name.like(f"{TAG}%")).first() is not None


def _wipe(session) -> None:
    for model in (Signal, Divergence, SourceAssessment, Analysis, StoryItem, Story, RawItem, Source, Brief, Recipient):
        session.query(model).delete()
    session.commit()


def seed(session, reset: bool = False) -> None:
    if reset:
        _wipe(session)
    elif _already_seeded(session):
        print(f"Dev seed already present (found a Source tagged {TAG!r}); skipping. Use --reset to wipe and reseed.")
        return

    now = _now()

    src_ar_direct = Source(
        name=f"{TAG} Damascus Telegram channel",
        url="https://example.test/dmz-channel",
        language="Arabic",
        dialect="Levantine",
        type="discussion",
        region="Syria",
        credibility_prior=0.6,
        last_seen_at=now,
        active=True,
    )
    src_fa_one_step = Source(
        name=f"{TAG} Persian-language forum",
        url="https://example.test/fa-forum",
        language="Persian",
        dialect="Iranian",
        type="discussion",
        region="Iran",
        credibility_prior=0.55,
        last_seen_at=now,
        active=True,
    )
    src_ar_aggregator = Source(
        name=f"{TAG} Beirut news aggregator",
        url="https://example.test/beirut-agg",
        language="Arabic",
        dialect="Levantine",
        type="aggregator",
        region="Lebanon",
        credibility_prior=0.5,
        last_seen_at=now,
        active=True,
    )
    src_en_direct = Source(
        name=f"{TAG} English wire service",
        url="https://example.test/en-wire",
        language="English",
        dialect=None,
        type="rss",
        region=None,
        credibility_prior=0.7,
        last_seen_at=now,
        active=True,
    )
    src_silent = Source(
        name=f"{TAG} Silent regional blog",
        url="https://example.test/silent-blog",
        language="Arabic",
        dialect="Levantine",
        type="scraper",
        region="Syria",
        credibility_prior=0.3,
        last_seen_at=now - timedelta(hours=30),
        active=True,
    )
    session.add_all([src_ar_direct, src_fa_one_step, src_ar_aggregator, src_en_direct, src_silent])
    session.flush()

    # --- Story 1: corroborated, high-severity, imminent (grade 5) ---------
    ri_ar1 = RawItem(
        source_id=src_ar_direct.id,
        fetched_at=now - timedelta(hours=3),
        original_lang="ar",
        original_text=f"{TAG} نقل مراقبون محليون تحرّكًا عسكريًا ملحوظًا قرب الحدود الشمالية منذ مساء الثلاثاء.",
        working_text=f"{TAG} Local monitors reported a noticeable military buildup near the northern border since Wednesday evening.",
        url="https://example.test/dmz-channel/post-1",
        content_hash="synthdev0001",
    )
    ri_fa1 = RawItem(
        source_id=src_fa_one_step.id,
        fetched_at=now - timedelta(hours=2),
        original_lang="fa",
        original_text=f"{TAG} کاربران در تالار این منطقه از حرکت وسیع تقویتها در نزدیکی مرز خبر می‌دهند.",
        working_text=f"{TAG} Forum users in the region report a large movement of forces near the border.",
        url="https://example.test/fa-forum/thread-42",
        content_hash="synthdev0002",
    )
    ri_en1 = RawItem(
        source_id=src_en_direct.id,
        fetched_at=now - timedelta(hours=1),
        original_lang="en",
        original_text=f"{TAG} Officials described the deployment as a routine, previously scheduled exercise.",
        working_text=f"{TAG} Officials described the deployment as a routine, previously scheduled exercise.",
        url="https://example.test/en-wire/story-1",
        content_hash="synthdev0003",
    )
    session.add_all([ri_ar1, ri_fa1, ri_en1])
    session.flush()

    story1 = Story(
        title=f"{TAG} Military buildup reported near northern border",
        event_type="military_event",
        status="open",
        first_seen_at=now - timedelta(hours=3),
        last_updated_at=now,
        location_country="Syria",
        location_precision="city",
        latitude=36.2021,
        longitude=37.1343,
    )
    session.add(story1)
    session.flush()
    session.add_all(
        [
            StoryItem(story_id=story1.id, raw_item_id=ri_ar1.id),
            StoryItem(story_id=story1.id, raw_item_id=ri_fa1.id),
            StoryItem(story_id=story1.id, raw_item_id=ri_en1.id),
        ]
    )

    grade1 = probability_grade(
        num_independent_sources=2,
        max_access_level=SourceAccessLevel.DIRECT,
        has_corroborating_artefact=True,
    )
    analysis1 = Analysis(
        story_id=story1.id,
        facts_json=[
            {
                "text": f"{TAG} Two independent in-region sources report increased military movement near the northern border.",
                "raw_item_ids": [ri_ar1.id, ri_fa1.id],
            },
        ],
        analysis_text=(
            f"{TAG} Corroborated by a direct-access Telegram channel and a one-step forum report, both describing "
            "unusual troop movement in the same window. English-language wire coverage frames the same activity as "
            "a routine exercise — see divergence below."
        ),
        probability_grade=grade1,
        contrary_evidence=None,
        generated_at=now,
    )
    session.add(analysis1)
    session.flush()
    session.add_all(
        [
            SourceAssessment(
                analysis_id=analysis1.id,
                source_id=src_ar_direct.id,
                access_level=SourceAccessLevel.DIRECT.value,
                reliability=0.8,
                rationale=f"{TAG} Channel operator posts firsthand photos/video from within the affected area.",
            ),
            SourceAssessment(
                analysis_id=analysis1.id,
                source_id=src_fa_one_step.id,
                access_level=SourceAccessLevel.ONE_STEP.value,
                reliability=0.6,
                rationale=f"{TAG} Forum users relaying accounts from residents one step removed from the scene.",
            ),
        ]
    )
    session.add(
        Divergence(
            story_id=story1.id,
            in_region_summary=f"{TAG} In-region sources describe active, unscheduled military mobilization.",
            english_media_summary=f"{TAG} English-language wire coverage calls the same activity a routine, previously scheduled exercise.",
            divergence_points=[f"{TAG} 'Unscheduled buildup' (in-region) vs. 'routine exercise' (English media)"],
            convergence_points=[f"{TAG} Both describe increased military presence in the same border area and window"],
        )
    )
    signal1 = Signal(
        story_id=story1.id,
        type="military_event",
        severity="critical",
        is_imminent=True,
        created_at=now,
        status="new",
    )
    session.add(signal1)

    # --- Story 2: single-source, uncorroborated (grade 3) -----------------
    ri_fa2 = RawItem(
        source_id=src_fa_one_step.id,
        fetched_at=now - timedelta(hours=5),
        original_lang="fa",
        original_text=f"{TAG} کاربری فرهنگی محلی بازداشت شد.",
        working_text=f"{TAG} A local cultural writer was reportedly detained, according to a single forum post.",
        url="https://example.test/fa-forum/thread-51",
        content_hash="synthdev0004",
    )
    session.add(ri_fa2)
    session.flush()

    story2 = Story(
        title=f"{TAG} Unconfirmed report of a local writer's detention",
        event_type="arrest_cultural_figure",
        status="open",
        first_seen_at=now - timedelta(hours=5),
        last_updated_at=now - timedelta(hours=4),
        # Country-level only, deliberately less precise than story1 - the source
        # doesn't name a city, and Principle 11 says not to invent one.
        location_country="Iran",
        location_precision="country",
        latitude=32.5750,
        longitude=54.2741,
    )
    session.add(story2)
    session.flush()
    session.add(StoryItem(story_id=story2.id, raw_item_id=ri_fa2.id))

    grade2 = probability_grade(
        num_independent_sources=1,
        max_access_level=SourceAccessLevel.ONE_STEP,
        has_corroborating_artefact=False,
    )
    analysis2 = Analysis(
        story_id=story2.id,
        facts_json=[
            {
                "text": f"{TAG} A single forum post claims a local cultural figure was detained; no corroborating artefact yet.",
                "raw_item_ids": [ri_fa2.id],
            },
        ],
        analysis_text=(
            f"{TAG} One-step forum report only; no second independent source or direct artefact (photo, official "
            "statement, second witness) has surfaced. Grade is capped pending corroboration, not because the claim "
            "looks false."
        ),
        probability_grade=grade2,
        contrary_evidence=None,
        generated_at=now - timedelta(hours=4),
    )
    session.add(analysis2)
    session.flush()
    session.add(
        SourceAssessment(
            analysis_id=analysis2.id,
            source_id=src_fa_one_step.id,
            access_level=SourceAccessLevel.ONE_STEP.value,
            reliability=0.5,
            rationale=f"{TAG} Single forum account, one step removed; no second source yet.",
        )
    )
    session.add(
        Signal(
            story_id=story2.id,
            type="arrest_cultural_figure",
            severity="elevated",
            is_imminent=False,
            created_at=now - timedelta(hours=4),
            status="reviewed",
        )
    )

    # --- Story 3: contradicted by better evidence (grade 1) ---------------
    ri_ar3 = RawItem(
        source_id=src_ar_aggregator.id,
        fetched_at=now - timedelta(hours=8),
        original_lang="ar",
        original_text=f"{TAG} تداولت حسابات تزعم وفاة مسؤول محلي.",
        working_text=f"{TAG} An aggregator account circulated an unverified claim that a local official had died.",
        url="https://example.test/beirut-agg/item-9",
        content_hash="synthdev0005",
    )
    ri_en3 = RawItem(
        source_id=src_en_direct.id,
        fetched_at=now - timedelta(hours=6),
        original_lang="en",
        original_text=f"{TAG} A wire photographer captured the official speaking at a public event this morning, in good health.",
        working_text=f"{TAG} A wire photographer captured the official speaking at a public event this morning, in good health.",
        url="https://example.test/en-wire/story-7",
        content_hash="synthdev0006",
    )
    session.add_all([ri_ar3, ri_en3])
    session.flush()

    story3 = Story(
        title=f"{TAG} Unverified death claim, contradicted by same-day footage",
        event_type=None,
        status="closed",
        first_seen_at=now - timedelta(hours=8),
        last_updated_at=now - timedelta(hours=5),
        # Deliberately left unlocated (location_precision stays NULL) - no
        # city/country is named in the sourced facts, so none is invented.
    )
    session.add(story3)
    session.flush()
    session.add_all(
        [
            StoryItem(story_id=story3.id, raw_item_id=ri_ar3.id),
            StoryItem(story_id=story3.id, raw_item_id=ri_en3.id),
        ]
    )

    grade3 = probability_grade(
        num_independent_sources=1,
        max_access_level=SourceAccessLevel.AGGREGATOR,
        has_corroborating_artefact=False,
        contradicted_by_better_evidence=True,
    )
    analysis3 = Analysis(
        story_id=story3.id,
        facts_json=[
            {
                "text": f"{TAG} An aggregator account claimed a local official had died.",
                "raw_item_ids": [ri_ar3.id],
            },
        ],
        analysis_text=(
            f"{TAG} Contradicted same-day by a direct-access wire photo of the official speaking publicly. "
            "Treated as false pending any retraction or correction."
        ),
        probability_grade=grade3,
        contrary_evidence=f"{TAG} Same-day wire photo/video shows the official alive and speaking publicly.",
        generated_at=now - timedelta(hours=5),
    )
    session.add(analysis3)
    session.flush()
    session.add_all(
        [
            SourceAssessment(
                analysis_id=analysis3.id,
                source_id=src_ar_aggregator.id,
                access_level=SourceAccessLevel.AGGREGATOR.value,
                reliability=0.3,
                rationale=f"{TAG} Aggregator relaying an unsourced claim, no original reporting.",
            ),
            SourceAssessment(
                analysis_id=analysis3.id,
                source_id=src_en_direct.id,
                access_level=SourceAccessLevel.DIRECT.value,
                reliability=0.85,
                rationale=f"{TAG} Wire photographer present at the event; direct firsthand evidence.",
            ),
        ]
    )
    session.add(
        Signal(
            story_id=story3.id,
            type="none",
            severity="critical",
            is_imminent=False,
            created_at=now - timedelta(hours=8),
            status="suppressed",
        )
    )

    session.flush()

    # --- Briefs -------------------------------------------------------------
    def _brief_item(story: Story, analysis: Analysis, raw_item_ids: list[int]) -> dict:
        return {
            "story_id": story.id,
            "title": story.title,
            "event_type": story.event_type,
            "facts": analysis.facts_json,
            "analysis_text": analysis.analysis_text,
            "probability_grade": analysis.probability_grade,
            "contrary_evidence": analysis.contrary_evidence,
            "has_corroborating_artefact": analysis.probability_grade >= 4,
        }

    def _raw_item_entry(raw_item: RawItem) -> dict:
        return {
            "id": raw_item.id,
            "source_name": raw_item.source.name,
            "access_level": None,
            "url": raw_item.url,
            "fetched_at": raw_item.fetched_at.isoformat(),
            "original_lang": raw_item.original_lang,
            "content_hash": raw_item.content_hash,
            "original_text": raw_item.original_text,
            "working_text": raw_item.working_text,
        }

    daily_items = [
        _brief_item(story1, analysis1, [ri_ar1.id, ri_fa1.id]),
        _brief_item(story2, analysis2, [ri_fa2.id]),
    ]
    daily_raw_items = {
        str(ri.id): _raw_item_entry(ri) for ri in (ri_ar1, ri_fa1, ri_fa2)
    }
    session.add(
        Brief(
            type="daily",
            for_date=now,
            content_json={"items": daily_items, "raw_items": daily_raw_items},
            generated_at=now,
        )
    )
    session.add(
        Brief(
            type="weekly",
            for_date=now,
            content_json={
                "title": f"{TAG} What Mattered This Week",
                "body": (
                    f"{TAG}\n\nBorder-area military activity (see the buildup story) was the most consequential "
                    "item this week, corroborated by two independent in-region sources despite English-language "
                    "coverage framing it as routine. A widely-circulated death claim about a local official was "
                    "contradicted the same day by direct wire footage and should be treated as false. One cultural-"
                    "figure detention report remains uncorroborated and is being watched for a second source."
                ),
            },
            generated_at=now,
        )
    )

    # --- Recipients ---------------------------------------------------------
    session.add_all(
        [
            Recipient(
                name=f"{TAG} Owner (test)",
                email="owner@example.test",
                phone=None,
                channels=["email"],
                active=True,
                approved_by="Owner (dev seed)",
            ),
            Recipient(
                name=f"{TAG} Analyst (test)",
                email="analyst2@example.test",
                phone="+10000000000",
                channels=["email", "sms"],
                active=True,
                approved_by="Owner (dev seed)",
            ),
            Recipient(
                name=f"{TAG} Pending reviewer (test)",
                email="pending@example.test",
                phone=None,
                channels=["email"],
                active=False,
                approved_by=None,
            ),
        ]
    )

    session.commit()
    print(
        f"Seeded {TAG}: 5 sources (1 silent), 3 stories/analyses (grades {grade1}/{grade2}/{grade3}), "
        "1 divergence, 3 signals (new/reviewed/suppressed), 2 briefs (daily/weekly), 3 recipients."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Wipe existing seed rows before reseeding.")
    args = parser.parse_args()

    init_db()
    seed_dev_user()
    with SessionLocal() as session:
        seed(session, reset=args.reset)


if __name__ == "__main__":
    main()
