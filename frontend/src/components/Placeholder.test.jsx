import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Placeholder } from "./Placeholder";

describe("Placeholder", () => {
  it("renders the given label", () => {
    render(<Placeholder label="MESG frontend scaffold OK" />);
    expect(screen.getByText("MESG frontend scaffold OK")).toBeInTheDocument();
  });
});
