import { AlertTriangle, PauseCircle } from "lucide-react";
import PropTypes from "prop-types";

/** Source liveness is itself a signal (TDD §4.1) — shown in every header.
 * Text is `ink`, not text-grade-2: measured contrast of text-grade-2 on
 * the surface-raised header background is 3.84:1, failing WCAG AA (needs
 * 4.5:1) — see Badge.jsx for the same class of finding.
 *
 * U-3 (D-019 scheduler & runtime): collection gaps, a stopped scheduler,
 * a pause and failing jobs are each shown in words, never hidden and never
 * carried by color alone. */
function hhmm(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function Flag({ icon: Icon = AlertTriangle, children, title }) {
  return (
    <span className="flex shrink-0 items-center gap-1 text-ink" title={title}>
      <Icon size={14} aria-hidden="true" className="text-grade-2" />
      {children}
    </span>
  );
}

Flag.propTypes = {
  icon: PropTypes.elementType,
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
};

function gapTitle(gap) {
  return gap.ongoing
    ? `${gap.job}: no successful run since ${new Date(gap.start).toLocaleString()}`
    : `${gap.job}: ${new Date(gap.start).toLocaleString()} – ${new Date(gap.end).toLocaleString()}`;
}

export function PipelineStatusStrip({
  lastRunAt,
  silentSourceCount,
  llmMonthlySpendUsd,
  llmMonthlyCapUsd,
  schedulerRunning = null,
  paused = false,
  jobs = [],
  collectionGaps = [],
}) {
  const lastRunText = lastRunAt ? `Last pipeline run: ${hhmm(lastRunAt)}` : "Last pipeline run: never";

  const budgetExhausted = llmMonthlySpendUsd >= llmMonthlyCapUsd;
  const failingJobs = jobs.filter((j) => j.last_status === "failed").map((j) => j.job);
  const openGaps = collectionGaps.filter((g) => g.ongoing);
  const closedGaps = collectionGaps.filter((g) => !g.ongoing);
  const allGapsTitle = collectionGaps.map(gapTitle).join("\n");
  const earliestOpen = openGaps.map((g) => g.start).sort()[0];

  return (
    <div className="flex min-w-0 flex-wrap items-center gap-2 text-sm text-ink-muted">
      <span className="hidden truncate sm:inline">{lastRunText}</span>
      {schedulerRunning === false ? (
        <Flag title="Collection runs only when the backend is started with scripts/run.py (MESG_SCHEDULER=1)">
          Scheduler off
        </Flag>
      ) : null}
      {paused ? <Flag icon={PauseCircle}>Ingestion paused</Flag> : null}
      {failingJobs.length > 0 ? <Flag>{failingJobs.join(", ")} failing</Flag> : null}
      {openGaps.length > 0 ? (
        <Flag title={allGapsTitle}>Collection gap since {hhmm(earliestOpen)}</Flag>
      ) : closedGaps.length > 0 ? (
        <Flag title={allGapsTitle}>
          {closedGaps.length} collection {closedGaps.length === 1 ? "gap" : "gaps"} (7 days)
        </Flag>
      ) : null}
      {silentSourceCount > 0 ? (
        <Flag>
          {silentSourceCount} {silentSourceCount === 1 ? "source" : "sources"} silent
        </Flag>
      ) : null}
      <span className={`shrink-0 ${budgetExhausted ? "flex items-center gap-1 text-ink" : ""}`}>
        {budgetExhausted ? <AlertTriangle size={14} aria-hidden="true" className="text-grade-2" /> : null}
        LLM spend: ${llmMonthlySpendUsd.toFixed(2)} / ${llmMonthlyCapUsd.toFixed(2)} this month
      </span>
    </div>
  );
}

const jobShape = PropTypes.shape({
  job: PropTypes.string.isRequired,
  last_status: PropTypes.string,
});

const gapShape = PropTypes.shape({
  job: PropTypes.string.isRequired,
  start: PropTypes.string.isRequired,
  end: PropTypes.string,
  ongoing: PropTypes.bool.isRequired,
});

PipelineStatusStrip.propTypes = {
  lastRunAt: PropTypes.string,
  silentSourceCount: PropTypes.number.isRequired,
  llmMonthlySpendUsd: PropTypes.number.isRequired,
  llmMonthlyCapUsd: PropTypes.number.isRequired,
  schedulerRunning: PropTypes.bool,
  paused: PropTypes.bool,
  jobs: PropTypes.arrayOf(jobShape),
  collectionGaps: PropTypes.arrayOf(gapShape),
};
