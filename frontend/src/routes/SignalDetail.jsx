import { useParams } from "react-router-dom";
import { Badge } from "../components/primitives/Badge";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { Tag } from "../components/primitives/Tag";
import { ImminentPill } from "../domain/ImminentPill";
import { ReviewReleaseControls } from "../domain/ReviewReleaseControls";
import { SeverityMark } from "../domain/SeverityMark";
import { useSignal } from "../domain/useSignals";

export function SignalDetail() {
  const { id } = useParams();
  const query = useSignal(Number(id));

  if (query.isLoading) {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <Skeleton lines={4} />
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <ErrorState message="Couldn't load this alert." onRetry={() => query.refetch()} />
      </div>
    );
  }

  const signal = query.data;

  return (
    <div className="mx-auto max-w-2xl space-y-4 p-6">
      <div className="flex items-center gap-3">
        <SeverityMark severity={signal.severity} />
        {signal.is_imminent ? <ImminentPill /> : null}
        <Tag>{signal.type}</Tag>
        <Badge>{signal.status}</Badge>
      </div>
      <h1 className="text-xl font-semibold text-ink">{signal.story_title}</h1>

      <ReviewReleaseControls signalId={signal.id} />
    </div>
  );
}
