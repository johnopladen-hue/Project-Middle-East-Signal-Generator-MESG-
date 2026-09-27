import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
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
