import { Eye, EyeOff } from "lucide-react";
import PropTypes from "prop-types";
import { useState } from "react";
import { Badge } from "../../components/primitives/Badge";
import { Button } from "../../components/primitives/Button";
import { ErrorState } from "../../components/primitives/ErrorState";
import { FormField } from "../../components/primitives/FormField";
import { IconButton } from "../../components/primitives/IconButton";
import { Skeleton } from "../../components/primitives/Skeleton";
import { Table } from "../../components/primitives/Table";
import { useCreateRecipient, useRecipients, useUpdateRecipient } from "../../domain/useAdmin";

function maskEmail(email) {
  if (!email) return "—";
  const [local, domain] = email.split("@");
  return `${local[0] ?? ""}${"•".repeat(Math.max(local.length - 1, 3))}@${domain}`;
}

function maskPhone(phone) {
  if (!phone) return "—";
  return `${"•".repeat(Math.max(phone.length - 4, 3))}${phone.slice(-4)}`;
}

function MaskedField({ value, mask }) {
  const [revealed, setRevealed] = useState(false);
  if (!value) return <span>—</span>;
  return (
    <span className="inline-flex items-center gap-1 font-mono text-xs">
      {revealed ? value : mask(value)}
      <IconButton
        label={revealed ? "Hide" : "Reveal"}
        icon={revealed ? EyeOff : Eye}
        onClick={() => setRevealed((v) => !v)}
      />
    </span>
  );
}

MaskedField.propTypes = {
  value: PropTypes.string,
  mask: PropTypes.func.isRequired,
};

export function AdminRecipients() {
  const query = useRecipients();
  const createMutation = useCreateRecipient();
  const updateMutation = useUpdateRecipient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", phone: "", channels: [] });

  async function handleCreate(event) {
    event.preventDefault();
    const channels = [form.email ? "email" : null, form.phone ? "sms" : null].filter(Boolean);
    await createMutation.mutateAsync({ ...form, channels, active: false });
    setForm({ name: "", email: "", phone: "", channels: [] });
    setShowForm(false);
  }

  if (query.isLoading) return <Skeleton lines={4} />;
  if (query.isError) return <ErrorState message="Couldn't load recipients." onRetry={() => query.refetch()} />;

  return (
    <div>
      <div className="mb-3 rounded-lg border border-grade-2/30 bg-grade-2/5 p-3 text-sm text-ink">
        Recipient email/phone is real user data. The moment real recipient data lands, this repository flips to
        Private (Keel Principle 10) — plan for that flip; don&apos;t be surprised by it.
      </div>

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">Recipients (whitelist)</h2>
        <Button variant="secondary" onClick={() => setShowForm((value) => !value)}>
          {showForm ? "Cancel" : "Add recipient"}
        </Button>
      </div>

      {showForm ? (
        <form onSubmit={handleCreate} className="mb-4 grid grid-cols-2 gap-3 rounded-lg border border-rule p-4">
          <FormField label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <FormField label="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <FormField label="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
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
          { key: "email", header: "Email", render: (row) => <MaskedField value={row.email} mask={maskEmail} /> },
          { key: "phone", header: "Phone", render: (row) => <MaskedField value={row.phone} mask={maskPhone} /> },
          {
            key: "active",
            header: "Approved",
            render: (row) => (
              <button
                type="button"
                onClick={() => updateMutation.mutate({ id: row.id, active: !row.active, approved_by: "owner" })}
                className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
              >
                <Badge tone={row.active ? "neutral" : "grade-2"}>{row.active ? "Active" : "Pending"}</Badge>
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
