import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { Tabs } from "./Tabs";

const TABS = [
  { id: "facts", label: "Facts", content: <p>Facts content</p> },
  { id: "analysis", label: "Analysis", content: <p>Analysis content</p> },
];

describe("Tabs", () => {
  it("switches the active tab with the arrow keys (keyboard operability, §5.5)", async () => {
    const user = userEvent.setup();
    render(<Tabs tabs={TABS} />);

    const factsTab = screen.getByRole("tab", { name: "Facts" });
    const analysisTab = screen.getByRole("tab", { name: "Analysis" });
    expect(factsTab).toHaveAttribute("aria-selected", "true");

    factsTab.focus();
    await user.keyboard("{ArrowRight}");

    expect(analysisTab).toHaveAttribute("aria-selected", "true");
    expect(analysisTab).toHaveFocus();
  });

  it("hides the inactive tab panel", () => {
    render(<Tabs tabs={TABS} />);
    expect(screen.getByText("Facts content")).toBeVisible();
    expect(screen.getByText("Analysis content")).not.toBeVisible();
  });
});
