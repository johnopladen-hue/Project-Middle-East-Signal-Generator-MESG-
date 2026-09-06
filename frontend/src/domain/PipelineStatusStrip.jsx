import { AlertTriangle } from "lucide-react";
import PropTypes from "prop-types";

/** Source liveness is itself a signal (TDD §4.1) — shown in every header. */
export function PipelineStatusStrip({ lastRunAt, silentSourceCount }) {
  const lastRunText = lastRunAt
    ? `Last pipeline run: ${new Date(lastRunAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    : "Last pipeline run: never";

  return (
    <div className="flex items-center gap-2 text-sm text-ink-muted">
      <span>{lastRunText}</span>
      {silentSourceCount > 0 ? (
        <span className="flex items-center gap-1 text-grade-2">
          <AlertTriangle size={14} aria-hidden="true" />
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
