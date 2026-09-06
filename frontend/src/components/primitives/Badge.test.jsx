import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge } from "./Badge";

describe("Badge", () => {
  it("always renders text content alongside its tone — never color alone (KEEL: never rely on color alone)", () => {
    render(<Badge tone="grade-3">3 · Unconfirmed</Badge>);
    expect(screen.getByText("3 · Unconfirmed")).toBeInTheDocument();
  });
});
