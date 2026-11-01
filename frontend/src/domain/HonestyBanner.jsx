import { Info } from "lucide-react";
import { useCapabilities } from "./useCapabilities";

/** U-5: one plain line on what MESG does today, driven by real state
 * (GET /capabilities reads it from the data), never hard-coded copy, so it
 * changes on its own as each track lands. Non-dismissable on purpose. */
const FEEDS = [
  ["rss", "RSS"],
  ["telegram", "Telegram"],
];
const OTHERS = [
  ["triage_translation", "machine triage translation"],
  ["graded_analysis", "graded analysis"],
  ["daily_brief", "daily brief"],
  ["alert_delivery", "alerts by email/SMS"],
];

// D-022: a standing statement of what MESG measures - not state, so not derived.
export const SCOPE_LINE =
  "Scope: public in-region channels, outlets and named voices compared with English media, not population opinion or private conversation.";

export function describeCapabilities(caps) {
  const feeds = FEEDS.filter(([key]) => caps[key]).map(([, label]) => label);
  const others = OTHERS.filter(([key]) => caps[key]).map(([, label]) => label);
  const missing = [...FEEDS, ...OTHERS].filter(([key]) => !caps[key]).map(([, label]) => label);

  const sentences = [];
  if (feeds.length > 0) {
    sentences.push(`Live feed: ${[feeds.join(" + "), ...others].join(", ")}.`);
  } else if (others.length > 0) {
    sentences.push(`Running: ${others.join(", ")}.`);
  } else {
    sentences.push("Not collecting yet.");
  }
  if (missing.length > 0) sentences.push(`Not yet running: ${missing.join(", ")}.`);
  if (caps.synthetic_data_present) {
    sentences.push("Briefs and grades on the Dashboard are synthetic dev-seed data, not analysis.");
  }
  sentences.push(SCOPE_LINE);
  return sentences.join(" ");
}

export function HonestyBanner() {
  const { data, isError } = useCapabilities();
  const text = data
    ? describeCapabilities(data)
    : isError
      ? `Couldn't check what MESG is running right now. ${SCOPE_LINE}`
      : "Checking what MESG is running…";

  return (
    <div
      role="note"
      aria-label="What MESG is doing today"
      className="mb-4 flex items-start gap-2 rounded-md border border-rule bg-surface-raised px-3 py-2 text-sm text-ink"
    >
      <Info size={16} aria-hidden="true" className="mt-0.5 shrink-0 text-ink-muted" />
      <span>{text}</span>
    </div>
  );
}
