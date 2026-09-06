import { AlertTriangle, Trash2 } from "lucide-react";
import { useState } from "react";
import { Badge } from "../components/primitives/Badge";
import { Button } from "../components/primitives/Button";
import { Card } from "../components/primitives/Card";
import { Drawer } from "../components/primitives/Drawer";
import { EmptyState } from "../components/primitives/EmptyState";
import { ErrorState } from "../components/primitives/ErrorState";
import { FormField } from "../components/primitives/FormField";
import { IconButton } from "../components/primitives/IconButton";
import { Modal } from "../components/primitives/Modal";
import { Skeleton } from "../components/primitives/Skeleton";
import { Table } from "../components/primitives/Table";
import { Tabs } from "../components/primitives/Tabs";
import { Tag } from "../components/primitives/Tag";
import { useToast } from "../components/primitives/Toast";

const GRADES = [
  { grade: 5, word: "Confirmed" },
  { grade: 4, word: "Probably true" },
  { grade: 3, word: "Unconfirmed" },
  { grade: 2, word: "Doubtful" },
  { grade: 1, word: "Likely false" },
];

function Section({ title, children }) {
  return (
    <section className="mb-10">
      <h2 className="mb-3 text-lg font-semibold text-ink">{title}</h2>
      <div className="flex flex-wrap items-start gap-4">{children}</div>
    </section>
  );
}

/** Dev-only component gallery (Order 2 PROOF). Not part of the shipped app routes. */
export function Gallery() {
  const [modalOpen, setModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const showToast = useToast();

  return (
    <main className="mx-auto max-w-3xl p-8">
      <h1 className="mb-1 text-2xl font-semibold text-ink">Component gallery</h1>
      <p className="mb-8 text-sm text-ink-muted">Dev-only — every primitive, every state (Order 2).</p>

      <Section title="Button">
        <Button>Release to recipients</Button>
        <Button variant="secondary">Suppress</Button>
        <Button variant="danger">Delete source</Button>
        <Button busy>Working</Button>
        <Button disabled>Disabled</Button>
      </Section>

      <Section title="IconButton">
        <IconButton label="Delete" icon={Trash2} />
        <IconButton label="Warning" icon={AlertTriangle} />
      </Section>

      <Section title="Card">
        <Card className="w-64">Card content sits here, with a rule border, no shadow.</Card>
      </Section>

      <Section title="Badge / Tag — grade scale (numeral + word, never color alone)">
        {GRADES.map(({ grade, word }) => (
          <Badge key={grade} tone={`grade-${grade}`}>
            {grade} · {word}
          </Badge>
        ))}
        <Tag>military_event</Tag>
        <Tag>coup</Tag>
      </Section>

      <Section title="Skeleton (loading state)">
        <div className="w-64">
          <Skeleton />
        </div>
      </Section>

      <Section title="EmptyState">
        <EmptyState message="No brief yet today — the morning run posts around 09:00." />
      </Section>

      <Section title="ErrorState">
        <ErrorState message="Couldn't load the daily brief." onRetry={() => {}} />
      </Section>

      <Section title="Toast">
        <Button variant="secondary" onClick={() => showToast("Released.")}>
          Trigger toast
        </Button>
      </Section>

      <Section title="FormField">
        <div className="w-64 space-y-3">
          <FormField label="Username" name="username" />
          <FormField label="Password" type="password" name="password" error="Required" />
        </div>
      </Section>

      <Section title="Table">
        <Table
          columns={[
            { key: "name", header: "Name" },
            { key: "language", header: "Language" },
          ]}
          rows={[
            { id: 1, name: "Al Jazeera", language: "Arabic" },
            { id: 2, name: "IRNA", language: "Persian" },
          ]}
          getRowKey={(row) => row.id}
        />
      </Section>

      <Section title="Tabs">
        <Tabs
          tabs={[
            { id: "facts", label: "Facts", content: <p>Facts panel content.</p> },
            { id: "analysis", label: "Analysis", content: <p>Analysis panel content.</p> },
          ]}
        />
      </Section>

      <Section title="Modal / Drawer">
        <Button variant="secondary" onClick={() => setModalOpen(true)}>
          Open modal
        </Button>
        <Button variant="secondary" onClick={() => setDrawerOpen(true)}>
          Open drawer
        </Button>
      </Section>

      <Modal title="Release to recipients" isOpen={modalOpen} onClose={() => setModalOpen(false)}>
        This sends to 4 active recipients (3 email, 1 SMS). This cannot be recalled.
      </Modal>
      <Drawer title="Navigation" isOpen={drawerOpen} onClose={() => setDrawerOpen(false)}>
        Drawer content.
      </Drawer>
    </main>
  );
}
