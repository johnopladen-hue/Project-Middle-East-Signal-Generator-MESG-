import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { normalizeFact } from "./normalizeFact";
import { SourceTrail } from "./SourceTrail";

describe("SourceTrail", () => {
  it("renders 'Unverified' for a fact with no artefact — never as a graded finding (TDD §8)", () => {
    const fact = normalizeFact({ text: "Unsourced claim", raw_item_ids: [] });
    render(<SourceTrail fact={fact} rawItems={[]} />);

    expect(screen.getByText("Unverified")).toBeInTheDocument();
  });

  it("renders a provenance chip per cited raw item when verified", () => {
    const fact = normalizeFact({ text: "Sourced claim", raw_item_ids: [1] });
    const rawItems = [{ id: 1, sourceName: "Al Jazeera", accessLevel: "direct" }];
    render(<SourceTrail fact={fact} rawItems={rawItems} />);

    expect(screen.getByRole("button", { name: /Al Jazeera/ })).toBeInTheDocument();
  });
});
