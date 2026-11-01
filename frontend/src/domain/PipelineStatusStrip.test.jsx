import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { pipelineStatus } from "../test/fixtures";
import { PipelineStatusStrip } from "./PipelineStatusStrip";

describe("PipelineStatusStrip", () => {
  it("shows this month's LLM spend against its cap (D-016, O-2)", () => {
    render(
      <PipelineStatusStrip
        silentSourceCount={0}
        llmMonthlySpendUsd={0.42}
        llmMonthlyCapUsd={20}
      />,
    );
    expect(screen.getByText("LLM spend: $0.42 / $20.00 this month")).toBeInTheDocument();
  });

  it("flags the budget visibly, not just by color, once the monthly cap is reached (KEEL: never rely on color alone)", () => {
    render(
      <PipelineStatusStrip
        silentSourceCount={0}
        llmMonthlySpendUsd={20}
        llmMonthlyCapUsd={20}
      />,
    );
    expect(screen.getByText("LLM spend: $20.00 / $20.00 this month")).toBeInTheDocument();
  });

  it("still shows silent-source count alongside spend", () => {
    render(
      <PipelineStatusStrip
        silentSourceCount={2}
        llmMonthlySpendUsd={1}
        llmMonthlyCapUsd={20}
      />,
    );
    expect(screen.getByText("2 sources silent")).toBeInTheDocument();
  });
});

// U-3 contract: the consumer side of IngestRun -> GET /pipeline/status. The
// fixture is a captured real response (scripts/capture_frontend_fixtures.py),
// not hand-written: Telegram's last success 2h old, translate failed, no scheduler.

function renderFromStatus(status) {
  return render(
    <PipelineStatusStrip
      lastRunAt={status.last_run_at}
      silentSourceCount={status.silent_source_count}
      llmMonthlySpendUsd={status.llm_monthly_spend_usd}
      llmMonthlyCapUsd={status.llm_monthly_cap_usd}
      schedulerRunning={status.scheduler_running}
      paused={status.paused}
      jobs={status.jobs}
      collectionGaps={status.collection_gaps}
    />,
  );
}

describe("PipelineStatusStrip — scheduler state (U-3, D-019)", () => {
  it("says in words that the scheduler is off", () => {
    renderFromStatus(pipelineStatus);
    expect(screen.getByText("Scheduler off")).toBeInTheDocument();
  });

  it("shows an open collection gap rather than hiding it (D-019)", () => {
    renderFromStatus(pipelineStatus);
    expect(screen.getByText(/^Collection gap since /)).toBeInTheDocument();
  });

  it("names the failing job", () => {
    renderFromStatus(pipelineStatus);
    expect(screen.getByText("translate failing")).toBeInTheDocument();
  });

  it("shows none of the scheduler flags when it is running cleanly with no gaps", () => {
    renderFromStatus({
      ...pipelineStatus,
      scheduler_running: true,
      collection_gaps: [],
      jobs: pipelineStatus.jobs.map((j) => ({ ...j, last_status: "ok" })),
    });
    expect(screen.queryByText("Scheduler off")).not.toBeInTheDocument();
    expect(screen.queryByText(/Collection gap/)).not.toBeInTheDocument();
    expect(screen.queryByText(/failing$/)).not.toBeInTheDocument();
  });

  it("shows a pause in words", () => {
    renderFromStatus({ ...pipelineStatus, paused: true });
    expect(screen.getByText("Ingestion paused")).toBeInTheDocument();
  });

  it("counts closed gaps from the last 7 days when none is open", () => {
    const closed = { ...pipelineStatus.collection_gaps[0], end: pipelineStatus.jobs[0].last_run_at, ongoing: false };
    renderFromStatus({ ...pipelineStatus, collection_gaps: [closed] });
    expect(screen.getByText("1 collection gap (7 days)")).toBeInTheDocument();
  });
});
