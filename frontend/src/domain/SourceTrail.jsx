import PropTypes from "prop-types";
import { Badge } from "../components/primitives/Badge";
import { ProvenanceChip } from "./ProvenanceChip";

/** The ordered set of ProvenanceChips behind a claim — or "unverified" if it has none (TDD §8). */
export function SourceTrail({ fact, rawItems }) {
  if (fact.unverified) {
    return <Badge tone="grade-2">Unverified</Badge>;
  }

  return (
    <div className="flex flex-wrap gap-1">
      {rawItems.map((rawItem) => (
        <ProvenanceChip key={rawItem.id} rawItem={rawItem} />
      ))}
    </div>
  );
}

SourceTrail.propTypes = {
  fact: PropTypes.shape({
    unverified: PropTypes.bool.isRequired,
    rawItemIds: PropTypes.arrayOf(PropTypes.number).isRequired,
  }).isRequired,
  rawItems: PropTypes.arrayOf(PropTypes.object).isRequired,
};
