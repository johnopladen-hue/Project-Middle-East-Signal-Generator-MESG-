/** Probability-of-truth scale — TDD §9.2, mirrored from backend/app/grading.py. */
export const GRADE_WORDS = {
  5: "Confirmed",
  4: "Probably true",
  3: "Unconfirmed",
  2: "Doubtful",
  1: "Likely false",
};

export function gradeReason(grade, hasCorroboratingArtefact) {
  if (!hasCorroboratingArtefact) {
    return "single credible source, not yet corroborated (ceiling without corroboration)";
  }
  if (grade === 5) return "multiple independent, high-access sources; no credible contradiction";
  if (grade === 4) return "two+ sources or one high-access source; minor gaps";
  if (grade === 2) return "low-access source, thin corroboration, or partial contradiction";
  return "contradicted by better evidence, or a single low-credibility source against contrary indicators";
}
