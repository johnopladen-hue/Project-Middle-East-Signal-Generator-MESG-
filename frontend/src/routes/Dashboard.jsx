import { ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";
import { IconButton } from "../components/primitives/IconButton";
import { Skeleton } from "../components/primitives/Skeleton";
import { EmptyState } from "../components/primitives/EmptyState";
import { ErrorState } from "../components/primitives/ErrorState";
import { BriefItemCard } from "../domain/BriefItemCard";
import { useBrief, useDailyBriefsList } from "../domain/useBriefs";

function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString(undefined, {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function Dashboard() {
  const [index, setIndex] = useState(0);
  const listQuery = useDailyBriefsList();
  const briefs = listQuery.data ?? [];
  const current = briefs[index];
  const briefQuery = useBrief(current?.id);

  if (listQuery.isLoading) {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <Skeleton lines={4} />
      </div>
    );
  }

  if (listQuery.isError) {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <ErrorState message="Couldn't load the daily brief." onRetry={() => listQuery.refetch()} />
      </div>
    );
  }

  if (briefs.length === 0) {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <EmptyState message="No brief yet today — the morning run posts around 09:00." />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-ink">Daily brief — {formatDate(current.for_date)}</h1>
        <div className="flex items-center gap-1">
          <IconButton
            label="Previous day"
            icon={ChevronLeft}
            disabled={index >= briefs.length - 1}
            onClick={() => setIndex((value) => value + 1)}
          />
          <IconButton
            label="Next day"
            icon={ChevronRight}
            disabled={index <= 0}
            onClick={() => setIndex((value) => value - 1)}
          />
        </div>
      </div>

      {briefQuery.isLoading ? (
        <Skeleton lines={6} />
      ) : briefQuery.isError ? (
        <ErrorState message="Couldn't load this brief." onRetry={() => briefQuery.refetch()} />
      ) : (
        <div className="space-y-3">
          {(briefQuery.data.content.items ?? []).map((item) => (
            <BriefItemCard
              key={item.story_id}
              item={item}
              rawItemsById={briefQuery.data.content.raw_items ?? {}}
            />
          ))}
        </div>
      )}
    </div>
  );
}
