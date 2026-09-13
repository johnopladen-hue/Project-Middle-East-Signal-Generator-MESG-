import { Link } from "react-router-dom";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { Table } from "../components/primitives/Table";
import { useOrganizationsList } from "../domain/useOrganizations";

/** Actor register directory - the actor-network layer's first visible surface (D-012, O-8). */
export function Organizations() {
  const query = useOrganizationsList();

  if (query.isLoading) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <Skeleton lines={4} />
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <ErrorState message="Couldn't load organizations." onRetry={() => query.refetch()} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="mb-4 text-lg font-semibold text-ink">Organizations</h1>
      <Table
        columns={[
          {
            key: "name",
            header: "Name",
            render: (row) => (
              <Link
                to={`/organizations/${row.id}`}
                className="text-accent hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
              >
                {row.name}
              </Link>
            ),
          },
          { key: "theatre", header: "Theatre", render: (row) => row.theatre ?? "—" },
          { key: "source_dataset", header: "Source" },
        ]}
        rows={query.data}
        getRowKey={(row) => row.id}
      />
    </div>
  );
}
