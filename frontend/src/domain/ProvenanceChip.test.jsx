import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ProvenanceChip } from "./ProvenanceChip";

const RAW_ITEM = {
  id: 1,
  sourceName: "Al Jazeera",
  accessLevel: "direct",
  url: "https://example.com/item",
  fetchedAt: "2026-09-06T09:00:00Z",
  originalLang: "Arabic",
  contentHash: "abc123",
  originalText: "النص الأصلي",
  workingText: "The original text",
};

describe("ProvenanceChip", () => {
  it("reaches the raw item (original + translation) in one click (TDD §8, one hop)", async () => {
    const user = userEvent.setup();
    render(<ProvenanceChip rawItem={RAW_ITEM} />);

    expect(screen.queryByText("النص الأصلي")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Al Jazeera/ }));

    expect(screen.getByText("النص الأصلي")).toBeInTheDocument();
    expect(screen.getByText("The original text")).toBeInTheDocument();
  });
});
