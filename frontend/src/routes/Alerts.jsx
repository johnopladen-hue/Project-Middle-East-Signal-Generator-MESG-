import { useState } from "react";
import { EmptyState } from "../components/primitives/EmptyState";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { SignalRow } from "../domain/SignalRow";
import { useSignalsList } from "../domain/useSignals";

const STATUS_OPTIONS = ["", "new", "reviewed", "released", "suppressed"];
const SEVERITY_OPTIONS = ["", "critical", "high", "elevated", "info"];

export function Alerts() {
  const [status, setStatus] = useState("");
  const [severity, setSeverity] = useState("");
  const query = useSignalsList({ status: status || undefined, severity: severity || undefined });

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="mb-4 text-lg font-semibold text-ink">Alerts</h1>

      <div className="mb-4 flex gap-3">
        <label className="text-sm text-ink-muted">
          Status
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            className="ml-2 rounded border border-rule px-2 py-1 text-sm"
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option || "All"}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm text-ink-muted">
          Severity
          <select
            value={severity}
            onChange={(event) => setSeverity(event.target.value)}
            className="ml-2 rounded border border-rule px-2 py-1 text-sm"
          >
            {SEVERITY_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option || "All"}
              </option>
            ))}
          </select>
        </label>
      </div>

      {query.isLoading ? (
        <Skeleton lines={4} />
      ) : query.isError ? (
        <ErrorState message="Couldn't load alerts." onRetry={() => query.refetch()} />
      ) : query.data.length === 0 ? (
        <EmptyState message="No alerts match these filters." />
      ) : (
        <div className="space-y-2">
          {query.data.map((signal) => (
            <SignalRow key={signal.id} signal={signal} />
          ))}
        </div>
      )}
    </div>
  );
}
