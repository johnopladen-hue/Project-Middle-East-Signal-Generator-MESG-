import { Link, useParams } from "react-router-dom";
import { EmptyState } from "../components/primitives/EmptyState";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { useBrief, useWeeklyBriefsList } from "../domain/useBriefs";

function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

/** "What mattered this week" — TDD §4.6. Latest by default; a past one loads by id (§7). */
export function Weekly() {
  const { id } = useParams();
  const listQuery = useWeeklyBriefsList();
  const weeklies = listQuery.data ?? [];
  const selectedId = id ? Number(id) : weeklies[0]?.id;
  const briefQuery = useBrief(selectedId);

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
        <ErrorState message="Couldn't load the weekly summaries." onRetry={() => listQuery.refetch()} />
      </div>
    );
  }

  if (weeklies.length === 0) {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <EmptyState message="No weekly summary yet — the first lands this Friday afternoon." />
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-3xl gap-8 p-6">
      <nav className="w-40 shrink-0 space-y-1">
        {weeklies.map((weekly) => (
          <Link
            key={weekly.id}
            to={`/weekly/${weekly.id}`}
            className={`block rounded px-2 py-1 text-sm
              focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent
              ${weekly.id === selectedId ? "bg-accent-weak text-accent" : "text-ink-muted hover:text-ink"}`}
          >
            {formatDate(weekly.for_date)}
          </Link>
        ))}
      </nav>

      <div className="flex-1">
        {briefQuery.isLoading ? (
          <Skeleton lines={6} />
        ) : briefQuery.isError ? (
          <ErrorState message="Couldn't load this weekly summary." onRetry={() => briefQuery.refetch()} />
        ) : (
          <article>
            <h1 className="mb-4 text-xl font-semibold text-ink">{briefQuery.data.content.title}</h1>
            <p className="reading-measure whitespace-pre-wrap text-sm text-ink">
              {briefQuery.data.content.body}
            </p>
          </article>
        )}
      </div>
    </div>
  );
}
