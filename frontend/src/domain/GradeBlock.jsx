import { ChevronDown, ChevronUp } from "lucide-react";
import PropTypes from "prop-types";
import { useState } from "react";
import { Badge } from "../components/primitives/Badge";
import { GRADE_WORDS, gradeReason } from "./gradeScale";
import { ProvenanceChip } from "./ProvenanceChip";

/** Numeral + word + corroboration-state line (TDD §9.2, UI-spec §3.2).
 * Defensively caps the *displayed* grade at 3 without an artefact, even if
 * an inconsistent value ever reached the client — the numeral is the
 * primary signal and must never overstate certainty. */
export function GradeBlock({ grade, hasCorroboratingArtefact, contraryEvidence, corroboratingItems = [] }) {
  const [expanded, setExpanded] = useState(false);
  const displayGrade = hasCorroboratingArtefact ? grade : Math.min(grade, 3);
  const canExpand = displayGrade >= 4 && corroboratingItems.length > 0;

  return (
    <div>
      <div className="flex items-center gap-2">
        <Badge tone={`grade-${displayGrade}`}>
          {displayGrade} · {GRADE_WORDS[displayGrade]}
        </Badge>
        {canExpand ? (
          <button
            type="button"
            onClick={() => setExpanded((value) => !value)}
            aria-expanded={expanded}
            className="inline-flex items-center gap-0.5 text-xs text-accent
              focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            corroborating artefacts
            {expanded ? <ChevronUp size={14} aria-hidden="true" /> : <ChevronDown size={14} aria-hidden="true" />}
          </button>
        ) : null}
      </div>
      <p className="mt-1 text-xs text-ink-muted">
        {displayGrade} · {GRADE_WORDS[displayGrade]} — {gradeReason(displayGrade, hasCorroboratingArtefact)}
      </p>
      {contraryEvidence ? (
        <p className="mt-1 text-xs text-ink-muted">
          <span className="font-medium">Contrary evidence:</span> {contraryEvidence}
        </p>
      ) : null}
      {expanded && canExpand ? (
        <div className="mt-2 flex flex-wrap gap-1">
          {corroboratingItems.map((rawItem) => (
            <ProvenanceChip key={rawItem.id} rawItem={rawItem} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

GradeBlock.propTypes = {
  grade: PropTypes.number.isRequired,
  hasCorroboratingArtefact: PropTypes.bool.isRequired,
  contraryEvidence: PropTypes.string,
  corroboratingItems: PropTypes.arrayOf(PropTypes.object),
};
