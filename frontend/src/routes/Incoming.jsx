import { AlertTriangle } from "lucide-react";
import PropTypes from "prop-types";
import { useState } from "react";
import { Badge } from "../components/primitives/Badge";
import { Card } from "../components/primitives/Card";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { useRawItems } from "../domain/useRawItems";

const RTL_LANGUAGES = new Set(["ar", "fa", "he"]);

const LANGUAGE_OPTIONS = [
  { value: "", label: "All languages" },
  { value: "ar", label: "Arabic" },
  { value: "fa", label: "Persian" },
  { value: "he", label: "Hebrew" },
  { value: "en", label: "English" },
];

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

      <p dir={isRtl ? "rtl" : "ltr"} lang={item.original_lang} className="text-sm text-ink">
        {item.original_text}
      </p>

      {item.working_text ? (
        <div className="mt-2 border-t border-rule pt-2">
          <p className="text-xs text-ink-muted">Machine translation</p>
          <p className="text-sm text-ink-muted">{item.working_text}</p>
        </div>
      ) : item.original_lang !== "en" ? (
        <p className="mt-2 text-xs text-ink-muted">Awaiting translation</p>
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
    original_lang: PropTypes.string.isRequired,
    original_text: PropTypes.string.isRequired,
    working_text: PropTypes.string,
    url: PropTypes.string.isRequired,
  }).isRequired,
};

/** The Incoming page - real collected items on screen (D-018, S-5/I-5).
 * No stories, grades or brief here yet; that's the Analysis order. */
export function Incoming() {
  const [language, setLanguage] = useState("");
  const [sourceClass, setSourceClass] = useState("");

  const query = useRawItems({ language: language || undefined, sourceClass: sourceClass || undefined });

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="mb-4 text-lg font-semibold text-ink">Incoming</h1>

      <div className="mb-4 flex flex-wrap gap-2">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="rounded-md border border-rule bg-surface px-2 py-1 text-sm text-ink"
          aria-label="Filter by language"
        >
          {LANGUAGE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <select
          value={sourceClass}
          onChange={(e) => setSourceClass(e.target.value)}
          className="rounded-md border border-rule bg-surface px-2 py-1 text-sm text-ink"
          aria-label="Filter by source class"
        >
          {CLASS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

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
            translation. {query.data.silent_sources.length} source
            {query.data.silent_sources.length === 1 ? "" : "s"} returned nothing this run
            {query.data.silent_sources.length > 0 ? `: ${query.data.silent_sources.join(", ")}` : "."}
          </p>

          {query.data.items.length === 0 ? (
            <p className="text-sm text-ink-muted">
              No items collected yet — run <code className="text-xs">python -m app.ingest --once</code>.
            </p>
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
