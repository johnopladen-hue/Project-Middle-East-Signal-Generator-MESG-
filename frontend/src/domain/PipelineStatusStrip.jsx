import { AlertTriangle } from "lucide-react";
import PropTypes from "prop-types";

/** Source liveness is itself a signal (TDD §4.1) — shown in every header.
 * Text is `ink`, not text-grade-2: measured contrast of text-grade-2 on
 * the surface-raised header background is 3.84:1, failing WCAG AA (needs
 * 4.5:1) — see Badge.jsx for the same class of finding. */
export function PipelineStatusStrip({ lastRunAt, silentSourceCount }) {
  const lastRunText = lastRunAt
    ? `Last pipeline run: ${new Date(lastRunAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    : "Last pipeline run: never";

  return (
    <div className="flex min-w-0 flex-wrap items-center gap-2 text-sm text-ink-muted">
      <span className="hidden truncate sm:inline">{lastRunText}</span>
      {silentSourceCount > 0 ? (
        <span className="flex shrink-0 items-center gap-1 text-ink">
          <AlertTriangle size={14} aria-hidden="true" className="text-grade-2" />
          {silentSourceCount} {silentSourceCount === 1 ? "source" : "sources"} silent
        </span>
      ) : null}
    </div>
  );
}

PipelineStatusStrip.propTypes = {
  lastRunAt: PropTypes.string,
  silentSourceCount: PropTypes.number.isRequired,
};
