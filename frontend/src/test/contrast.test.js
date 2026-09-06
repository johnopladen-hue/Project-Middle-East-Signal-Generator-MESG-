import { describe, expect, it } from "vitest";
import { WCAG_AA_NORMAL_TEXT, blend, contrastRatio } from "./contrast";

// Mirrors the @theme tokens in src/index.css. Kept as plain literals here
// (not imported from CSS) so this test has no build-tool dependency and
// runs in plain Node under Vitest.
const SURFACE = [247, 248, 250];
const SURFACE_RAISED = [255, 255, 255];
const INK = [26, 29, 36];
const INK_MUTED = [91, 98, 110];
const ACCENT = [14, 110, 119];
const WHITE = [255, 255, 255];

const GRADE = {
  5: [27, 127, 91],
  4: [107, 163, 104],
  3: [200, 145, 42],
  2: [197, 106, 46],
  1: [178, 58, 52],
};

describe("baseline text colors (sanity check on the token palette)", () => {
  it("ink on surface passes AA", () => {
    expect(contrastRatio(INK, SURFACE)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL_TEXT);
  });

  it("ink-muted on surface passes AA (used for metadata, severity labels)", () => {
    expect(contrastRatio(INK_MUTED, SURFACE)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL_TEXT);
  });

  it("accent on surface passes AA (links)", () => {
    expect(contrastRatio(ACCENT, SURFACE)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL_TEXT);
  });

  it("white on accent passes AA (primary button text)", () => {
    expect(contrastRatio(WHITE, ACCENT)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL_TEXT);
  });
});

describe("grade badge text — the actual fix (Badge.jsx: text-ink, not text-grade-N)", () => {
  it.each([5, 4, 3, 2, 1])("grade %i: ink text on its own /15 tint passes AA", (grade) => {
    const tintedBackground = blend(GRADE[grade], SURFACE_RAISED, 0.15);
    expect(contrastRatio(INK, tintedBackground)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL_TEXT);
  });
});

describe("proof the guard can fail (Keel Principle 6) — the bug this test exists to catch", () => {
  it.each([4, 3, 2])(
    "grade %i: colored text-grade-N on its own /15 tint FAILS AA — this is the exact regression found and fixed during Order 11's accessibility pass",
    (grade) => {
      const tintedBackground = blend(GRADE[grade], SURFACE_RAISED, 0.15);
      expect(contrastRatio(GRADE[grade], tintedBackground)).toBeLessThan(WCAG_AA_NORMAL_TEXT);
    },
  );

  it("grade 5 colored text on its own tint is borderline-fails AA too (4.3:1)", () => {
    const tintedBackground = blend(GRADE[5], SURFACE_RAISED, 0.15);
    expect(contrastRatio(GRADE[5], tintedBackground)).toBeLessThan(WCAG_AA_NORMAL_TEXT);
  });

  it("grade 1 is the one grade where colored text on its own tint happens to pass", () => {
    const tintedBackground = blend(GRADE[1], SURFACE_RAISED, 0.15);
    expect(contrastRatio(GRADE[1], tintedBackground)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL_TEXT);
  });
});
