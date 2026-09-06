import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FormField } from "./FormField";

describe("FormField", () => {
  it("links the error message to the input via aria-describedby", () => {
    render(<FormField label="Password" type="password" error="Required" />);
    const input = screen.getByLabelText("Password");
    const error = screen.getByText("Required");

    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(input.getAttribute("aria-describedby")).toBe(error.id);
  });

  it("has no aria-describedby when there is no error", () => {
    render(<FormField label="Username" />);
    expect(screen.getByLabelText("Username")).not.toHaveAttribute("aria-describedby");
  });
});
