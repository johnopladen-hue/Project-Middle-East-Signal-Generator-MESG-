"""Synthetic dev-only seed data (D-011 first article, O-3).

Populates every built screen with fabricated Stories/Signals/Briefs/Sources/
Recipients themed to the v1 scope (D-008: Levantine Arabic + Iranian
Persian) so the app reads as MESG rather than an empty shell. Every row this
script creates is tagged with TAG below - no real data, no scraped content,
no real contact details. Run with `python -m app.dev_seed` from `backend/`
(idempotent: skips if already seeded; pass --reset to wipe and reseed).

Eight stories spread across the last five days (so the Dashboard's day
paging and the Weekly nav list both have more than one entry to page
through), spanning eight of the ten event-taxonomy types
(backend/app/signals.py), with grades computed by the real
`grading.probability_grade` rather than hand-picked.
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

AR = "أفاد مراقبون محليون بأن {event} في {location} يوم {day}."
FA = "ناظران محلی گزارش دادند که {event} در {location} روز {day} رخ داد."


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _already_seeded(session) -> bool:
    return session.query(Source).filter(Source.name.like(f"{TAG}%")).first() is not None


def _wipe(session) -> None:
    for model in (Signal, Divergence, SourceAssessment, Analysis, StoryItem, Story, RawItem, Source, Brief, Recipient):
        session.query(model).delete()
    session.commit()


class Seeder:
    """Small stateful helper so each story definition below reads as data,
    not thirty lines of session.add() boilerplate repeated eight times."""

    def __init__(self, session, now: datetime):
        self.session = session
        self.now = now
        self.sources: dict[str, Source] = {}
        self.days: dict[int, list[dict]] = {}  # day_offset -> list of brief items
        self.days_raw_items: dict[int, dict] = {}  # day_offset -> raw_items map

    def source(self, key: str, **kwargs) -> Source:
        src = Source(name=f"{TAG} {kwargs.pop('name')}", last_seen_at=self.now, active=True, **kwargs)
        self.session.add(src)
        self.session.flush()
        self.sources[key] = src
        return src

    def raw_item(self, source_key: str, lang: str, native: str, english: str, url: str, hours_ago: float) -> RawItem:
        src = self.sources[source_key]
        ri = RawItem(
            source_id=src.id,
            fetched_at=self.now - timedelta(hours=hours_ago),
            original_lang=lang,
            original_text=f"{TAG} {native}",
            working_text=f"{TAG} {english}",
            url=url,
            content_hash=f"synthdev{len(self.session.new) + hash(url) % 10000:04d}",
        )
        self.session.add(ri)
        self.session.flush()
        return ri

    def story(
        self,
        *,
        day_offset: int,
        title: str,
        event_type: str | None,
        status: str,
        facts: list[tuple[str, list[RawItem]]],
        all_raw_items: list[RawItem],
        analysis_text: str,
        grade_kwargs: dict,
        contrary_evidence: str | None,
        assessments: list[tuple[str, SourceAccessLevel, float, str]],
        signal_severity: str,
        signal_is_imminent: bool,
        signal_status: str,
        divergence: dict | None = None,
    ) -> tuple[Story, Analysis]:
        first_seen = self.now - timedelta(days=day_offset, hours=1)
        story = Story(
            title=f"{TAG} {title}",
            event_type=event_type,
            status=status,
            first_seen_at=first_seen,
            last_updated_at=self.now - timedelta(days=day_offset),
        )
        self.session.add(story)
        self.session.flush()
        self.session.add_all(StoryItem(story_id=story.id, raw_item_id=ri.id) for ri in all_raw_items)

        grade = probability_grade(**grade_kwargs)
        analysis = Analysis(
            story_id=story.id,
            facts_json=[{"text": f"{TAG} {text}", "raw_item_ids": [ri.id for ri in ris]} for text, ris in facts],
            analysis_text=f"{TAG} {analysis_text}",
            probability_grade=grade,
            contrary_evidence=f"{TAG} {contrary_evidence}" if contrary_evidence else None,
            generated_at=self.now - timedelta(days=day_offset),
        )
        self.session.add(analysis)
        self.session.flush()

        for source_key, access_level, reliability, rationale in assessments:
            self.session.add(
                SourceAssessment(
                    analysis_id=analysis.id,
                    source_id=self.sources[source_key].id,
                    access_level=access_level.value,
                    reliability=reliability,
                    rationale=f"{TAG} {rationale}",
                )
            )

        if divergence:
            self.session.add(
                Divergence(
                    story_id=story.id,
                    in_region_summary=f"{TAG} {divergence['in_region']}",
                    english_media_summary=f"{TAG} {divergence['english_media']}",
                    divergence_points=[f"{TAG} {p}" for p in divergence["divergence_points"]],
                    convergence_points=[f"{TAG} {p}" for p in divergence["convergence_points"]],
                )
            )

        self.session.add(
            Signal(
                story_id=story.id,
                type=event_type or "none",
                severity=signal_severity,
                is_imminent=signal_is_imminent,
                created_at=first_seen,
                status=signal_status,
            )
        )

        item = {
            "story_id": story.id,
            "title": story.title,
            "event_type": story.event_type,
            "facts": analysis.facts_json,
            "analysis_text": analysis.analysis_text,
            "probability_grade": analysis.probability_grade,
            "contrary_evidence": analysis.contrary_evidence,
            "has_corroborating_artefact": analysis.probability_grade >= 4,
        }
        self.days.setdefault(day_offset, []).append(item)
        raw_map = self.days_raw_items.setdefault(day_offset, {})
        for ri in all_raw_items:
            raw_map[str(ri.id)] = {
                "id": ri.id,
                "source_name": ri.source.name,
                "access_level": None,
                "url": ri.url,
                "fetched_at": ri.fetched_at.isoformat(),
                "original_lang": ri.original_lang,
                "content_hash": ri.content_hash,
                "original_text": ri.original_text,
                "working_text": ri.working_text,
            }
        return story, analysis


def seed(session, reset: bool = False) -> None:
    if reset:
        _wipe(session)
    elif _already_seeded(session):
        print(f"Dev seed already present (found a Source tagged {TAG!r}); skipping. Use --reset to wipe and reseed.")
        return

    now = _now()
    s = Seeder(session, now)

    # --- Sources -------------------------------------------------------------
    s.source("ar_direct_1", name="Damascus Telegram channel", url="https://example.test/dmz-channel",
              language="Arabic", dialect="Levantine", type="discussion", region="Syria", credibility_prior=0.6)
    s.source("ar_direct_2", name="Aleppo eyewitness network", url="https://example.test/aleppo-eyewitness",
              language="Arabic", dialect="Levantine", type="discussion", region="Syria", credibility_prior=0.65)
    s.source("fa_direct_1", name="Tehran state wire", url="https://example.test/tehran-wire",
              language="Persian", dialect="Iranian", type="rss", region="Iran", credibility_prior=0.5)
    s.source("fa_one_step_1", name="Persian-language forum", url="https://example.test/fa-forum",
              language="Persian", dialect="Iranian", type="discussion", region="Iran", credibility_prior=0.55)
    s.source("ar_agg_1", name="Beirut news aggregator", url="https://example.test/beirut-agg",
              language="Arabic", dialect="Levantine", type="aggregator", region="Lebanon", credibility_prior=0.5)
    s.source("ar_agg_2", name="Amman regional aggregator", url="https://example.test/amman-agg",
              language="Arabic", dialect="Levantine", type="aggregator", region="Jordan", credibility_prior=0.45)
    s.source("en_direct_1", name="English wire service", url="https://example.test/en-wire",
              language="English", dialect=None, type="rss", region=None, credibility_prior=0.7)
    s.source("en_direct_2", name="International NGO field report feed", url="https://example.test/ngo-feed",
              language="English", dialect=None, type="rss", region=None, credibility_prior=0.75)
    s.source("silent", name="Silent regional blog", url="https://example.test/silent-blog",
              language="Arabic", dialect="Levantine", type="scraper", region="Syria", credibility_prior=0.3)
    s.sources["silent"].last_seen_at = now - timedelta(hours=30)

    # --- Day 0 (today) --------------------------------------------------------
    ri1 = s.raw_item("ar_direct_1", "ar", AR.format(event="تحرّكًا عسكريًا ملحوظًا", location="الحدود الشمالية", day="الثلاثاء"),
                      "Local monitors reported a noticeable military buildup near the northern border.",
                      "https://example.test/dmz-channel/post-1", hours_ago=3)
    ri2 = s.raw_item("fa_one_step_1", "fa", FA.format(event="حرکت وسیع تقویت‌ها", location="نزدیکی مرز", day="سه‌شنبه"),
                      "Forum users report a large movement of forces near the border.",
                      "https://example.test/fa-forum/thread-42", hours_ago=2)
    ri3 = s.raw_item("en_direct_1", "en", "N/A",
                      "Officials described the deployment as a routine, previously scheduled exercise.",
                      "https://example.test/en-wire/story-1", hours_ago=1)
    s.story(
        day_offset=0, title="Military buildup reported near northern border", event_type="military_event",
        status="open", facts=[("Two independent in-region sources report increased military movement near the northern border.", [ri1, ri2])],
        all_raw_items=[ri1, ri2, ri3],
        analysis_text="Corroborated by a direct-access channel and a one-step forum report describing unusual troop movement in the same window. English-language wire coverage frames the same activity as a routine exercise.",
        grade_kwargs=dict(num_independent_sources=2, max_access_level=SourceAccessLevel.DIRECT, has_corroborating_artefact=True),
        contrary_evidence=None,
        assessments=[("ar_direct_1", SourceAccessLevel.DIRECT, 0.8, "Channel operator posts firsthand photos/video from the affected area."),
                     ("fa_one_step_1", SourceAccessLevel.ONE_STEP, 0.6, "Forum users relaying accounts one step removed from the scene.")],
        signal_severity="critical", signal_is_imminent=True, signal_status="new",
        divergence={"in_region": "In-region sources describe active, unscheduled military mobilization.",
                    "english_media": "English-language wire coverage calls the same activity a routine, previously scheduled exercise.",
                    "divergence_points": ["'Unscheduled buildup' (in-region) vs. 'routine exercise' (English media)"],
                    "convergence_points": ["Both describe increased military presence in the same border area and window"]},
    )

    ri4 = s.raw_item("fa_one_step_1", "fa", FA.format(event="بازداشت یک نویسنده فرهنگی", location="شهر", day="سه‌شنبه"),
                      "A local cultural writer was reportedly detained, according to a single forum post.",
                      "https://example.test/fa-forum/thread-51", hours_ago=5)
    s.story(
        day_offset=0, title="Unconfirmed report of a local writer's detention", event_type="arrest_cultural_figure",
        status="open", facts=[("A single forum post claims a local cultural figure was detained; no corroborating artefact yet.", [ri4])],
        all_raw_items=[ri4],
        analysis_text="One-step forum report only; no second independent source or direct artefact has surfaced. Grade is capped pending corroboration, not because the claim looks false.",
        grade_kwargs=dict(num_independent_sources=1, max_access_level=SourceAccessLevel.ONE_STEP, has_corroborating_artefact=False),
        contrary_evidence=None,
        assessments=[("fa_one_step_1", SourceAccessLevel.ONE_STEP, 0.5, "Single forum account, one step removed; no second source yet.")],
        signal_severity="elevated", signal_is_imminent=False, signal_status="reviewed",
    )

    # --- Day 1 (yesterday) -----------------------------------------------------
    ri5 = s.raw_item("ar_agg_1", "ar", AR.format(event="وفاة مسؤول محلي", location="المدينة", day="الاثنين"),
                      "An aggregator account circulated an unverified claim that a local official had died.",
                      "https://example.test/beirut-agg/item-9", hours_ago=32)
    ri6 = s.raw_item("en_direct_1", "en", "N/A",
                      "A wire photographer captured the official speaking at a public event, in good health.",
                      "https://example.test/en-wire/story-7", hours_ago=30)
    s.story(
        day_offset=1, title="Unverified death claim, contradicted by same-day footage", event_type=None,
        status="closed", facts=[("An aggregator account claimed a local official had died.", [ri5])],
        all_raw_items=[ri5, ri6],
        analysis_text="Contradicted same-day by a direct-access wire photo of the official speaking publicly. Treated as false pending any retraction or correction.",
        grade_kwargs=dict(num_independent_sources=1, max_access_level=SourceAccessLevel.AGGREGATOR, has_corroborating_artefact=False, contradicted_by_better_evidence=True),
        contrary_evidence="Same-day wire photo/video shows the official alive and speaking publicly.",
        assessments=[("ar_agg_1", SourceAccessLevel.AGGREGATOR, 0.3, "Aggregator relaying an unsourced claim, no original reporting."),
                     ("en_direct_1", SourceAccessLevel.DIRECT, 0.85, "Wire photographer present at the event; direct firsthand evidence.")],
        signal_severity="critical", signal_is_imminent=False, signal_status="suppressed",
    )

    ri7 = s.raw_item("ar_direct_2", "ar", AR.format(event="محاولة سيطرة عسكرية", location="العاصمة", day="الاثنين"),
                      "An eyewitness network reports an attempted takeover of a government building in the capital, with video.",
                      "https://example.test/aleppo-eyewitness/post-3", hours_ago=28)
    s.story(
        day_offset=1, title="Rumors of an attempted takeover in the capital", event_type="coup",
        status="open", facts=[("A direct-access eyewitness network reports an attempted takeover of a government building, with video evidence.", [ri7])],
        all_raw_items=[ri7],
        analysis_text="Single source, but direct access with video artefact - not yet corroborated by a second independent source.",
        grade_kwargs=dict(num_independent_sources=1, max_access_level=SourceAccessLevel.DIRECT, has_corroborating_artefact=True),
        contrary_evidence=None,
        assessments=[("ar_direct_2", SourceAccessLevel.DIRECT, 0.7, "Eyewitness network posted video from the scene; single source so far.")],
        signal_severity="critical", signal_is_imminent=True, signal_status="new",
    )

    # --- Day 2 --------------------------------------------------------------
    ri8 = s.raw_item("ar_direct_2", "ar", AR.format(event="زلزال قوي", location="المنطقة الحدودية", day="الأحد"),
                      "A strong earthquake struck the border region; local networks report significant casualties.",
                      "https://example.test/aleppo-eyewitness/post-8", hours_ago=54)
    ri9 = s.raw_item("en_direct_2", "en", "N/A",
                      "An NGO field feed confirms the earthquake and an initial, lower casualty estimate pending assessment teams.",
                      "https://example.test/ngo-feed/report-3", hours_ago=50)
    s.story(
        day_offset=2, title="Earthquake strikes border region; casualty figures diverge", event_type="natural_disaster",
        status="open", facts=[("Two independent direct-access sources confirm a significant earthquake in the border region.", [ri8, ri9])],
        all_raw_items=[ri8, ri9],
        analysis_text="Confirmed by two independent direct-access sources. In-region networks report a higher casualty estimate than the initial NGO field figure, likely reflecting access to areas assessment teams haven't reached yet.",
        grade_kwargs=dict(num_independent_sources=2, max_access_level=SourceAccessLevel.DIRECT, has_corroborating_artefact=True),
        contrary_evidence=None,
        assessments=[("ar_direct_2", SourceAccessLevel.DIRECT, 0.75, "Eyewitness network with photos from multiple affected neighborhoods."),
                     ("en_direct_2", SourceAccessLevel.DIRECT, 0.8, "NGO field team on the ground, early in the assessment.")],
        signal_severity="high", signal_is_imminent=False, signal_status="new",
        divergence={"in_region": "In-region networks report a substantially higher casualty count from areas not yet reached by assessment teams.",
                    "english_media": "International coverage cites the NGO's initial, lower figure as the assessment is still underway.",
                    "divergence_points": ["Casualty estimate: in-region higher vs. international initial-figure lower"],
                    "convergence_points": ["Both confirm the earthquake and its general location"]},
    )

    ri10 = s.raw_item("ar_agg_2", "ar", AR.format(event="انتشار مرض", location="مخيم على الحدود", day="الأحد"),
                       "An aggregator relays unverified whispers of illness spreading in a border refugee camp.",
                       "https://example.test/amman-agg/item-14", hours_ago=48)
    s.story(
        day_offset=2, title="Whispered reports of illness spreading in a border camp", event_type="outbreak",
        status="open", facts=[("An aggregator relays a single, unverified report of illness spreading in a border camp.", [ri10])],
        all_raw_items=[ri10],
        analysis_text="Single aggregator source relaying an unsourced claim; no direct report or health-authority statement yet.",
        grade_kwargs=dict(num_independent_sources=1, max_access_level=SourceAccessLevel.AGGREGATOR, has_corroborating_artefact=False),
        contrary_evidence=None,
        assessments=[("ar_agg_2", SourceAccessLevel.AGGREGATOR, 0.35, "Aggregator with no original reporting or named source.")],
        signal_severity="elevated", signal_is_imminent=False, signal_status="new",
    )

    # --- Day 3 ----------------------------------------------------------------
    ri11 = s.raw_item("ar_direct_1", "ar", AR.format(event="بازداشت سياسي مؤكّد", location="المدينة", day="السبت"),
                       "Direct-access channel confirms the arrest of a political figure, with a photo of the detention.",
                       "https://example.test/dmz-channel/post-20", hours_ago=76)
    ri12 = s.raw_item("fa_direct_1", "fa", FA.format(event="بازداشت یک چهره سیاسی", location="پایتخت", day="شنبه"),
                       "State wire independently confirms the same arrest via an official statement.",
                       "https://example.test/tehran-wire/item-33", hours_ago=74)
    s.story(
        day_offset=3, title="Political figure's arrest confirmed by two independent accounts", event_type="arrest_political_figure",
        status="closed", facts=[("Two independent direct-access sources confirm the arrest of a political figure.", [ri11, ri12])],
        all_raw_items=[ri11, ri12],
        analysis_text="Confirmed by a direct-access channel with photo evidence and an independent official statement from a state wire - two independent, direct-access sources.",
        grade_kwargs=dict(num_independent_sources=2, max_access_level=SourceAccessLevel.DIRECT, has_corroborating_artefact=True),
        contrary_evidence=None,
        assessments=[("ar_direct_1", SourceAccessLevel.DIRECT, 0.8, "Channel posted a photo from the scene of the detention."),
                     ("fa_direct_1", SourceAccessLevel.DIRECT, 0.65, "Official statement from a state wire service, independent of the first source.")],
        signal_severity="high", signal_is_imminent=False, signal_status="released",
    )

    # --- Day 4 ------------------------------------------------------------------
    ri13 = s.raw_item("fa_one_step_1", "fa", FA.format(event="سکوت یک وبلاگ منطقه‌ای", location="آنلاین", day="جمعه"),
                       "Forum users note that a regional blog we monitor hasn't posted in over a day, with no explanation.",
                       "https://example.test/fa-forum/thread-60", hours_ago=98)
    s.story(
        day_offset=4, title="A monitored regional blog goes dark without explanation", event_type="source_disappearance",
        status="open", facts=[("Forum users noticed a monitored regional blog has gone silent, with no explanation offered.", [ri13])],
        all_raw_items=[ri13],
        analysis_text="A source going silent is itself a signal (TDD §4.1) - this pipeline's own silent-source indicator independently flags the same blog as overdue; see the Admin Sources screen.",
        grade_kwargs=dict(num_independent_sources=1, max_access_level=SourceAccessLevel.ONE_STEP, has_corroborating_artefact=False),
        contrary_evidence=None,
        assessments=[("fa_one_step_1", SourceAccessLevel.ONE_STEP, 0.4, "Forum users noticing the silence, one step removed from the source itself.")],
        signal_severity="info", signal_is_imminent=False, signal_status="new",
    )

    session.flush()

    # --- Briefs: one daily brief per seeded day, plus two weekly summaries ---
    for day_offset, items in s.days.items():
        session.add(
            Brief(
                type="daily",
                for_date=now - timedelta(days=day_offset),
                content_json={"items": items, "raw_items": s.days_raw_items[day_offset]},
                generated_at=now - timedelta(days=day_offset),
            )
        )

    session.add(
        Brief(
            type="weekly",
            for_date=now,
            content_json={
                "title": f"{TAG} What Mattered This Week",
                "body": (
                    f"{TAG}\n\nFour items stood out this week. Border-area military activity (Day 0) was corroborated "
                    "by two independent in-region sources despite English-language coverage framing it as routine. "
                    "A rumored takeover attempt in the capital (Day 1) is backed by direct video from a single "
                    "source, not yet a second one. An earthquake in the border region (Day 2) is confirmed, though "
                    "in-region and international casualty estimates diverge. A political figure's arrest (Day 3) is "
                    "fully confirmed by two independent direct sources. A widely-circulated death claim (Day 1) was "
                    "contradicted the same day and should be treated as false. Two lower-confidence items - a "
                    "cultural-figure detention report and camp-illness whispers - remain single-source and are "
                    "being watched for a second one."
                ),
            },
            generated_at=now,
        )
    )
    session.add(
        Brief(
            type="weekly",
            for_date=now - timedelta(days=7),
            content_json={
                "title": f"{TAG} What Mattered Last Week",
                "body": (
                    f"{TAG}\n\nBorder tensions eased following a short deployment earlier in the week; no confirmed "
                    "high-grade events. Two single-source claims were logged and later dropped for lack of a second "
                    "source. Included here only to populate the weekly-summary history."
                ),
            },
            generated_at=now - timedelta(days=7),
        )
    )

    # --- Recipients ---------------------------------------------------------
    session.add_all(
        [
            Recipient(name=f"{TAG} Owner (test)", email="owner@example.test", phone=None,
                      channels=["email"], active=True, approved_by="Owner (dev seed)"),
            Recipient(name=f"{TAG} Analyst (test)", email="analyst2@example.test", phone="+10000000000",
                      channels=["email", "sms"], active=True, approved_by="Owner (dev seed)"),
            Recipient(name=f"{TAG} Pending reviewer (test)", email="pending@example.test", phone=None,
                      channels=["email"], active=False, approved_by=None),
        ]
    )

    session.commit()
    total_stories = sum(len(v) for v in s.days.values())
    print(
        f"Seeded {TAG}: {len(s.sources)} sources (1 silent), {total_stories} stories/analyses across "
        f"{len(s.days)} days, {len(s.days)} daily briefs + 2 weekly briefs, 3 recipients."
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
