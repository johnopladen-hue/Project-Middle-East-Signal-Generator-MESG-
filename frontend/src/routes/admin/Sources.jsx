import { AlertTriangle } from "lucide-react";
import { useState } from "react";
import { Badge } from "../../components/primitives/Badge";
import { Button } from "../../components/primitives/Button";
import { ErrorState } from "../../components/primitives/ErrorState";
import { FormField } from "../../components/primitives/FormField";
import { Skeleton } from "../../components/primitives/Skeleton";
import { Table } from "../../components/primitives/Table";
import { useCreateSource, useSources, useUpdateSource } from "../../domain/useAdmin";

const SILENCE_THRESHOLD_MS = 6 * 60 * 60 * 1000;

function isSilent(lastSeenAt) {
  if (!lastSeenAt) return true;
  return Date.now() - new Date(lastSeenAt).getTime() > SILENCE_THRESHOLD_MS;
}

export function AdminSources() {
  const query = useSources();
  const createMutation = useCreateSource();
  const updateMutation = useUpdateSource();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", url: "", language: "", type: "rss" });

  async function handleCreate(event) {
    event.preventDefault();
    await createMutation.mutateAsync(form);
    setForm({ name: "", url: "", language: "", type: "rss" });
    setShowForm(false);
  }

  if (query.isLoading) return <Skeleton lines={4} />;
  if (query.isError) return <ErrorState message="Couldn't load sources." onRetry={() => query.refetch()} />;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">Sources</h2>
        <Button variant="secondary" onClick={() => setShowForm((value) => !value)}>
          {showForm ? "Cancel" : "Add source"}
        </Button>
      </div>

      {showForm ? (
        <form onSubmit={handleCreate} className="mb-4 grid grid-cols-2 gap-3 rounded-lg border border-rule p-4">
          <FormField label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <FormField label="URL" value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} />
          <FormField
            label="Language"
            value={form.language}
            onChange={(e) => setForm({ ...form, language: e.target.value })}
          />
          <FormField label="Type" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })} />
          <div className="col-span-2">
            <Button type="submit" busy={createMutation.isPending}>
              Save
            </Button>
          </div>
        </form>
      ) : null}

      <Table
        columns={[
          { key: "name", header: "Name" },
          { key: "language", header: "Language" },
          { key: "type", header: "Type" },
          { key: "credibility_prior", header: "Credibility" },
          {
            key: "last_seen_at",
            header: "Last seen",
            render: (row) =>
              isSilent(row.last_seen_at) ? (
                <span className="flex items-center gap-1 text-grade-2">
                  <AlertTriangle size={14} aria-hidden="true" /> Silent
                </span>
              ) : (
                new Date(row.last_seen_at).toLocaleString()
              ),
          },
          {
            key: "active",
            header: "Active",
            render: (row) => (
              <button
                type="button"
                onClick={() => updateMutation.mutate({ id: row.id, active: !row.active })}
                className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
              >
                <Badge tone={row.active ? "neutral" : "grade-2"}>{row.active ? "Active" : "Inactive"}</Badge>
              </button>
            ),
          },
        ]}
        rows={query.data}
        getRowKey={(row) => row.id}
      />
    </div>
  );
}
