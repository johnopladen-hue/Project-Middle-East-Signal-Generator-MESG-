import { Link, useParams } from "react-router-dom";
import { Card } from "../components/primitives/Card";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { Tag } from "../components/primitives/Tag";
import { useOrganization } from "../domain/useOrganizations";

/** Organization profile (D-012, O-8): designations render as parallel sourced
 * characterizations, never a resolved verdict - each names who said it, on what
 * list, and when. Relationship edges are followable to the other organization. */
export function OrganizationDetail() {
  const { id } = useParams();
  const query = useOrganization(Number(id));

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
        <ErrorState message="Couldn't load this organization." onRetry={() => query.refetch()} />
      </div>
    );
  }

  const org = query.data;

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <header>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-semibold text-ink">{org.name}</h1>
          {org.theatre ? <Tag>{org.theatre}</Tag> : null}
        </div>
        {org.aliases.length > 0 ? (
          <p className="mt-1 text-sm text-ink-muted">Also known as: {org.aliases.join(", ")}</p>
        ) : null}
      </header>

      <section>
        <h2 className="mb-2 text-sm font-semibold text-ink">Designations</h2>
        {org.designations.length === 0 ? (
          <p className="text-sm text-ink-muted">No designations on record.</p>
        ) : (
          <div className="space-y-2">
            {org.designations.map((d) => (
              <Card key={d.id}>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium text-ink">{d.body}</span>
                  <span className="text-xs text-ink-muted">
                    {d.match_confidence != null ? `confidence ${(d.match_confidence * 100).toFixed(0)}%` : null}
                  </span>
                </div>
                <p className="mt-1 text-sm text-ink">{d.label}</p>
                <p className="mt-1 text-xs text-ink-muted">
                  List {d.list_id}
                  {d.date ? ` · ${new Date(d.date).toLocaleDateString()}` : null} ·{" "}
                  <a href={d.url} target="_blank" rel="noreferrer" className="text-accent hover:underline">
                    source
                  </a>
                </p>
              </Card>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-2 text-sm font-semibold text-ink">Relationships</h2>
        {org.relationships.length === 0 ? (
          <p className="text-sm text-ink-muted">No relationships on record.</p>
        ) : (
          <ul className="space-y-1">
            {org.relationships.map((rel) => (
              <li key={rel.id} className="text-sm text-ink">
                {rel.direction === "outbound" ? (
                  <>
                    {rel.kind}{" "}
                    <Link to={`/organizations/${rel.other_org_id}`} className="text-accent hover:underline">
                      {rel.other_org_name}
                    </Link>
                  </>
                ) : (
                  <>
                    <Link to={`/organizations/${rel.other_org_id}`} className="text-accent hover:underline">
                      {rel.other_org_name}
                    </Link>{" "}
                    {rel.kind} this organization
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="mb-2 text-sm font-semibold text-ink">Source & citation</h2>
        <p className="text-xs text-ink-muted">
          <a href={org.source_url} target="_blank" rel="noreferrer" className="text-accent hover:underline">
            {org.source_dataset}
          </a>
          {org.last_verified ? ` · last verified ${new Date(org.last_verified).toLocaleDateString()}` : null}
        </p>
        {org.citation ? <p className="mt-1 text-xs text-ink-muted">{org.citation}</p> : null}
      </section>
    </div>
  );
}
