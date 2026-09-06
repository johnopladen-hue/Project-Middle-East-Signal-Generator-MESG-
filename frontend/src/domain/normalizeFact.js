/** Boundary normalization (TDD §8): a fact with no raw_item_id(s) becomes
 * explicit unverified:true — it must never arrive at GradeBlock/SourceTrail
 * looking like a corroborated finding. */
export function normalizeFact(rawFact) {
  const rawItemIds = rawFact.raw_item_ids ?? rawFact.rawItemIds ?? [];
  return {
    text: rawFact.text,
    rawItemIds,
    unverified: rawItemIds.length === 0,
  };
}
