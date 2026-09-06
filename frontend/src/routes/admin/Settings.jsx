import PropTypes from "prop-types";
import { useState } from "react";
import { Button } from "../../components/primitives/Button";
import { ErrorState } from "../../components/primitives/ErrorState";
import { FormField } from "../../components/primitives/FormField";
import { Skeleton } from "../../components/primitives/Skeleton";
import { useToast } from "../../components/primitives/Toast";
import { useSettings, useUpdateSettings } from "../../domain/useAdmin";

function SettingsForm({ initialThreshold }) {
  const updateMutation = useUpdateSettings();
  const showToast = useToast();
  const [threshold, setThreshold] = useState(initialThreshold);

  async function handleSubmit(event) {
    event.preventDefault();
    await updateMutation.mutateAsync({ alert_severity_threshold: threshold });
    showToast("Settings saved.");
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
      <FormField
        label="Minimum severity that triggers a bulletin"
        value={threshold}
        onChange={(event) => setThreshold(event.target.value)}
      />
      <p className="text-xs text-ink-muted">
        Cadence (ingest interval, brief time, weekly day) is not yet configurable here — the scheduler
        mechanism is still an open decision (documents/decisions.md).
      </p>
      <Button type="submit" busy={updateMutation.isPending}>
        Save
      </Button>
    </form>
  );
}

SettingsForm.propTypes = {
  initialThreshold: PropTypes.string.isRequired,
};

export function AdminSettings() {
  const query = useSettings();

  if (query.isLoading) return <Skeleton lines={3} />;
  if (query.isError) return <ErrorState message="Couldn't load settings." onRetry={() => query.refetch()} />;

  return (
    <div>
      <h2 className="mb-4 text-lg font-semibold text-ink">Settings</h2>
      <SettingsForm initialThreshold={query.data.values.alert_severity_threshold ?? ""} />
    </div>
  );
}
