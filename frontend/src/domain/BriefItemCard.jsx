import { ChevronDown, ChevronRight } from "lucide-react";
import PropTypes from "prop-types";
import { useState } from "react";
import { Card } from "../components/primitives/Card";
import { Tag } from "../components/primitives/Tag";
import { GradeBlock } from "./GradeBlock";
import { normalizeFact } from "./normalizeFact";
import { resolveRawItem } from "./resolveRawItem";
import { SourceTrail } from "./SourceTrail";

/** Collapsed headline -> facts -> analysis -> grade (TDD §4.6 brief format). */
export function BriefItemCard({ item, rawItemsById }) {
  const [expanded, setExpanded] = useState(false);

  const facts = (item.facts ?? []).map(normalizeFact);
  const sourceCount = new Set(facts.flatMap((fact) => fact.rawItemIds)).size;

  return (
    <Card>
      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        aria-expanded={expanded}
        className="flex w-full items-center gap-3 text-left
          focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        {expanded ? (
          <ChevronDown size={16} aria-hidden="true" className="shrink-0 text-ink-muted" />
        ) : (
          <ChevronRight size={16} aria-hidden="true" className="shrink-0 text-ink-muted" />
        )}
        <span className="flex-1 text-sm font-medium text-ink">
          {item.title ?? `Story #${item.story_id}`}
        </span>
        {item.event_type ? <Tag>{item.event_type}</Tag> : null}
        <span className="text-xs text-ink-muted">
          {sourceCount} {sourceCount === 1 ? "source" : "sources"}
        </span>
      </button>

      {expanded ? (
        <div className="mt-4 space-y-4 border-t border-rule pt-4">
          <div className="space-y-2">
            {facts.map((fact, index) => {
              const rawItems = fact.rawItemIds
                .map((id) => rawItemsById[String(id)])
                .filter(Boolean)
                .map(resolveRawItem);
              return (
                <div key={index}>
                  <p className="text-sm text-ink">{fact.text}</p>
                  <div className="mt-1">
                    <SourceTrail fact={fact} rawItems={rawItems} />
                  </div>
                </div>
              );
            })}
          </div>

          <p className="reading-measure text-sm text-ink">{item.analysis_text}</p>

          <GradeBlock
            grade={item.probability_grade}
            hasCorroboratingArtefact={item.has_corroborating_artefact}
            contraryEvidence={item.contrary_evidence}
          />
        </div>
      ) : null}
    </Card>
  );
}

BriefItemCard.propTypes = {
  item: PropTypes.shape({
    story_id: PropTypes.number.isRequired,
    title: PropTypes.string,
    event_type: PropTypes.string,
    facts: PropTypes.array,
    analysis_text: PropTypes.string,
    probability_grade: PropTypes.number.isRequired,
    contrary_evidence: PropTypes.string,
    has_corroborating_artefact: PropTypes.bool.isRequired,
  }).isRequired,
  rawItemsById: PropTypes.object.isRequired,
};
