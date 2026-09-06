import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { GradeBlock } from "./GradeBlock";

describe("GradeBlock", () => {
  it("never displays above 3 without a corroborating artefact, even if the grade prop says 5 (TDD §9.2 guardrail)", () => {
    render(<GradeBlock grade={5} hasCorroboratingArtefact={false} />);
    expect(screen.getByText("3 · Unconfirmed")).toBeInTheDocument();
    expect(screen.queryByText(/5 · Confirmed/)).not.toBeInTheDocument();
  });

  it("displays the true grade when corroborated", () => {
    render(<GradeBlock grade={5} hasCorroboratingArtefact />);
    expect(screen.getByText("5 · Confirmed")).toBeInTheDocument();
  });

  it("shows corroborating artefacts on click for grade >= 4", async () => {
    const user = userEvent.setup();
    render(
      <GradeBlock
        grade={4}
        hasCorroboratingArtefact
        corroboratingItems={[{ id: 1, sourceName: "IRNA", accessLevel: "direct" }]}
      />,
    );

    expect(screen.queryByRole("button", { name: /IRNA/ })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /corroborating artefacts/ }));

    expect(screen.getByRole("button", { name: /IRNA/ })).toBeInTheDocument();
  });

  it("does not offer to expand when there are no corroborating items", () => {
    render(<GradeBlock grade={4} hasCorroboratingArtefact corroboratingItems={[]} />);
    expect(screen.queryByRole("button", { name: /corroborating artefacts/ })).not.toBeInTheDocument();
  });
});
