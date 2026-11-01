import { AlertTriangle } from "lucide-react";
import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import { Badge } from "../components/primitives/Badge";
import { Card } from "../components/primitives/Card";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { HonestyBanner } from "../domain/HonestyBanner";
import { useRawItems } from "../domain/useRawItems";

const RTL_LANGUAGES = new Set(["ar", "fa", "he"]);

const LANGUAGE_OPTIONS = [
  { value: "", label: "All" },
  { value: "ar", label: "Arabic" },
  { value: "fa", label: "Persian" },
  { value: "he", label: "Hebrew" },
  { value: "en", label: "English" },
];

const KIND_OPTIONS = [
  { value: "", label: "All" },
  { value: "telegram", label: "Telegram" },
  { value: "rss", label: "RSS" },
];

// U-4: on the item's own time (publication, else fetch) - the same clock the list is sorted by.
const WINDOW_OPTIONS = [
  { value: "", label: "All time" },
  { value: "1", label: "1h" },
  { value: "6", label: "6h" },
  { value: "24", label: "24h" },
  { value: "48", label: "48h" },
];

const SEARCH_DEBOUNCE_MS = 300;

function formatTime(iso) {
  return new Date(iso).toLocaleString([], { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

/** A row of toggle buttons (aria-pressed) - quick filters visible at a glance. */
function QuickFilter({ label, options, value, onChange }) {
  return (
    <div role="group" aria-label={label} className="flex flex-wrap items-center gap-1">
      <span className="mr-1 text-xs text-ink-muted">{label}:</span>
      {options.map((opt) => {
        const active = opt.value === value;
        return (
          <button
            key={opt.value}
            type="button"
            aria-pressed={active}
            onClick={() => onChange(opt.value)}
            className={`rounded-md border px-2 py-0.5 text-xs focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
              active ? "border-accent bg-accent/10 font-medium text-ink" : "border-rule bg-surface text-ink"
            }`}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

QuickFilter.propTypes = {
  label: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.shape({ value: PropTypes.string, label: PropTypes.string })).isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
};

// D-016: NLLB output is triage, not a verified translation - say so on every line.
const TRIAGE_LABEL = "Machine triage translation (NLLB-200), not verified";

const CLASS_OPTIONS = [
  { value: "", label: "All classes" },
  { value: "native", label: "Native" },
  { value: "english_comparison", label: "English comparison" },
  { value: "pre_translated", label: "Pre-translated" },
  { value: "corroboration", label: "Corroboration" },
];

function ItemCard({ item }) {
  const isRtl = RTL_LANGUAGES.has(item.original_lang);
  const isUnconfirmed = (item.verification_note ?? "").includes("AUTHENTICITY UNCONFIRMED");

  return (
    <Card>
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <span className="font-medium text-ink">{item.source_name}</span>
        <span className="text-xs text-ink-muted">
          {item.published_at
            ? formatTime(item.published_at)
            : `Fetched ${formatTime(item.fetched_at)} (no publication time)`}
        </span>
        {item.source_class ? <Badge tone="neutral">{item.source_class}</Badge> : null}
        {item.pair_id ? <Badge tone="neutral">Pair: {item.pair_id}</Badge> : null}
        {item.designation_note ? (
          <span title={item.designation_note}>
            <Badge tone="grade-3">Designated</Badge>
          </span>
        ) : null}
        {isUnconfirmed ? (
          <span title={item.verification_note}>
            <Badge tone="grade-2">Authenticity unconfirmed</Badge>
          </span>
        ) : null}
      </div>

      {item.working_text ? (
        <div className="mb-2 border-b border-rule pb-2">
          <p className="text-xs text-ink-muted">
            {TRIAGE_LABEL}
            {item.translation?.status === "ok_truncated" ? " — first part only" : ""}
          </p>
          <p dir="ltr" lang="en" className="whitespace-pre-line text-sm text-ink">
            {item.working_text}
          </p>
        </div>
      ) : null}

      <p dir={isRtl ? "rtl" : "ltr"} lang={item.original_lang} className="whitespace-pre-line text-sm text-ink">
        {item.original_text}
      </p>

      {!item.working_text && item.original_lang !== "en" ? (
        <p className="mt-2 text-xs text-ink-muted">
          {item.translation?.status === "failed" ? "Translation failed — original shown" : "Awaiting translation"}
        </p>
      ) : null}

      <a
        href={item.url}
        target="_blank"
        rel="noreferrer"
        className="mt-2 inline-block text-xs text-accent hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        Open original →
      </a>
    </Card>
  );
}

ItemCard.propTypes = {
  item: PropTypes.shape({
    id: PropTypes.number.isRequired,
    source_name: PropTypes.string.isRequired,
    source_class: PropTypes.string,
    pair_id: PropTypes.string,
    designation_note: PropTypes.string,
    verification_note: PropTypes.string,
    fetched_at: PropTypes.string,
    published_at: PropTypes.string,
    original_lang: PropTypes.string.isRequired,
    original_text: PropTypes.string.isRequired,
    working_text: PropTypes.string,
    translation: PropTypes.shape({
      status: PropTypes.oneOf(["ok", "ok_truncated", "failed"]).isRequired,
      engine: PropTypes.string.isRequired,
      src_code: PropTypes.string.isRequired,
    }),
    url: PropTypes.string.isRequired,
  }).isRequired,
};

/** The Incoming page - real collected items on screen (D-018, S-5/I-5).
 * No stories, grades or brief here yet; that's the Analysis order. */
export function Incoming() {
  const [language, setLanguage] = useState("");
  const [kind, setKind] = useState("");
  const [sourceClass, setSourceClass] = useState("");
  const [windowHours, setWindowHours] = useState("");
  const [searchText, setSearchText] = useState("");
  const [q, setQ] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setQ(searchText.trim()), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [searchText]);

  const filters = {
    language: language || undefined,
    kind: kind || undefined,
    sourceClass: sourceClass || undefined,
    windowHours: windowHours || undefined,
    q: q || undefined,
  };
  const filtersKey = JSON.stringify(filters);

  // U-4: the newest item id when the reader opened (or last refreshed) the
  // list, for these filters. The list stays pinned to it; newer arrivals are
  // counted, not inserted. A pin made under other filters doesn't apply, so
  // any filter change re-pins on its first real (non-placeholder) response.
  const [pin, setPin] = useState({ key: filtersKey, id: null });
  const baselineId = pin.key === filtersKey ? pin.id : null;

  const query = useRawItems({ ...filters, upToId: baselineId ?? undefined });

  if (baselineId == null && query.data && !query.isPlaceholderData && query.data.max_id != null) {
    setPin({ key: filtersKey, id: query.data.max_id }); // adjust-state-during-render, no effect cascade
  }

  const filtered = Boolean(language || kind || sourceClass || windowHours || q);

  return (
    <div className="mx-auto max-w-3xl p-6">
      <HonestyBanner />
      <h1 className="mb-4 text-lg font-semibold text-ink">Incoming</h1>

      <div className="mb-4 flex flex-col gap-2">
        <input
          type="search"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          placeholder="Search English triage line or original script"
          aria-label="Search items"
          className="w-full rounded-md border border-rule bg-surface px-2 py-1 text-sm text-ink"
        />
        <QuickFilter label="Kind" options={KIND_OPTIONS} value={kind} onChange={setKind} />
        <QuickFilter label="Language" options={LANGUAGE_OPTIONS} value={language} onChange={setLanguage} />
        <QuickFilter label="Time" options={WINDOW_OPTIONS} value={windowHours} onChange={setWindowHours} />
        <select
          value={sourceClass}
          onChange={(e) => setSourceClass(e.target.value)}
          className="w-fit rounded-md border border-rule bg-surface px-2 py-1 text-sm text-ink"
          aria-label="Filter by source class"
        >
          {CLASS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {query.data?.newer_count > 0 ? (
        <button
          type="button"
          onClick={() => setPin({ key: filtersKey, id: query.data.max_id })} // max_id is the newest now, not the pin
          className="mb-3 rounded-full border border-accent bg-accent/10 px-3 py-1 text-sm text-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          {query.data.newer_count} new since you opened — show
        </button>
      ) : null}

      {query.isLoading ? <Skeleton lines={4} /> : null}

      {query.isError ? (
        <ErrorState message="Couldn't load incoming items." onRetry={() => query.refetch()} />
      ) : null}

      {query.data ? (
        <>
          <p className="mb-4 flex items-start gap-1 text-xs text-ink-muted">
            {query.data.silent_sources.length > 0 ? (
              <AlertTriangle size={14} aria-hidden="true" className="mt-0.5 shrink-0 text-grade-2" />
            ) : null}
            Showing {query.data.items.length} of {query.data.total} items. {query.data.awaiting_translation} awaiting
            translation
            {query.data.translation_failed ? `, ${query.data.translation_failed} translation failed` : ""}.{" "}
            {query.data.silent_sources.length} source
            {query.data.silent_sources.length === 1 ? "" : "s"} returned nothing this run
            {query.data.silent_sources.length > 0 ? `: ${query.data.silent_sources.join(", ")}` : "."}
          </p>

          {query.data.items.length === 0 ? (
            filtered ? (
              <p className="text-sm text-ink-muted">No items match these filters.</p>
            ) : (
              <p className="text-sm text-ink-muted">
                No items collected yet — run <code className="text-xs">python -m app.ingest --once</code>, or start{" "}
                <code className="text-xs">scripts/run.py</code> to collect on a schedule.
              </p>
            )
          ) : (
            <div className="flex flex-col gap-3">
              {query.data.items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}
