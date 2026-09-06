import { useParams } from "react-router-dom";
import { EmptyState } from "../components/primitives/EmptyState";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { Tag } from "../components/primitives/Tag";
import { DivergencePanel } from "../domain/DivergencePanel";
import { GradeBlock } from "../domain/GradeBlock";
import { normalizeFact } from "../domain/normalizeFact";
import { ProvenanceChip } from "../domain/ProvenanceChip";
import { resolveRawItem } from "../domain/resolveRawItem";
import { SourceAssessmentTable } from "../domain/SourceAssessmentTable";
import { SourceTrail } from "../domain/SourceTrail";
import { useStory } from "../domain/useStory";

export function Story() {
  const { id } = useParams();
  const query = useStory(Number(id));

  if (query.isLoading) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <Skeleton lines={8} />
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <ErrorState message="Couldn't load this story." onRetry={() => query.refetch()} />
      </div>
    );
  }

  const story = query.data;
  const rawItemsById = story.raw_items ?? {};
  const facts = (story.facts ?? []).map(normalizeFact);

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <header>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-semibold text-ink">{story.title}</h1>
          {story.event_type ? <Tag>{story.event_type}</Tag> : null}
        </div>
        {story.probability_grade != null ? (
          <div className="mt-2">
            <GradeBlock
              grade={story.probability_grade}
              hasCorroboratingArtefact={story.has_corroborating_artefact}
              contraryEvidence={story.contrary_evidence}
            />
          </div>
        ) : null}
      </header>

      <section>
        <h2 className="mb-2 text-sm font-semibold text-ink">Facts</h2>
        {facts.length === 0 ? (
          <EmptyState message="No facts recorded for this story yet." />
        ) : (
          <div className="space-y-2">
            {facts.map((fact, index) => {
              const rawItems = fact.rawItemIds
                .map((rid) => rawItemsById[String(rid)])
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
        )}
      </section>

      {story.analysis_text ? (
        <section>
          <h2 className="mb-2 text-sm font-semibold text-ink">Analysis</h2>
          <p className="reading-measure text-sm text-ink">{story.analysis_text}</p>
        </section>
      ) : null}

      {story.source_assessments.length > 0 ? (
        <section>
          <h2 className="mb-2 text-sm font-semibold text-ink">Source assessment</h2>
          <SourceAssessmentTable assessments={story.source_assessments} />
        </section>
      ) : null}

      {story.divergence ? (
        <section>
          <h2 className="mb-2 text-sm font-semibold text-ink">In-region vs. English media</h2>
          <DivergencePanel divergence={story.divergence} />
        </section>
      ) : null}

      {story.timeline.length > 0 ? (
        <section>
          <h2 className="mb-2 text-sm font-semibold text-ink">Related items timeline</h2>
          <div className="flex flex-wrap gap-1">
            {story.timeline.map((rawItemId) => (
              <ProvenanceChip
                key={rawItemId}
                rawItem={resolveRawItem(rawItemsById[String(rawItemId)])}
              />
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
