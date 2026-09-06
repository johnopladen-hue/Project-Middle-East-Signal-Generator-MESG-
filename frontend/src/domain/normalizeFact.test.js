import { describe, expect, it } from "vitest";
import { normalizeFact } from "./normalizeFact";

describe("normalizeFact", () => {
  it("marks a fact with no raw_item_ids as unverified", () => {
    const fact = normalizeFact({ text: "Claim with no source", raw_item_ids: [] });
    expect(fact.unverified).toBe(true);
  });

  it("marks a fact with raw_item_ids as verified", () => {
    const fact = normalizeFact({ text: "Sourced claim", raw_item_ids: [1, 2] });
    expect(fact.unverified).toBe(false);
    expect(fact.rawItemIds).toEqual([1, 2]);
  });
});
