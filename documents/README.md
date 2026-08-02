# Documents — Project MESG

This is the project's permanent record, per Keel v5/v6. Two rules govern everything in this directory:

1. **Every design decision gets written down in `documents/decisions/` BEFORE the work it describes is finished.** One file per decision, numbered `D-NNN-slug.md`, in the order resolved. `decisions.md` at the root of this folder is an index only — see [D-001](decisions/D-001-decision-log-structure.md) for why the folder is named `documents/` rather than Keel's literal `docs/`.
2. **Every claim records the artefact it came from** — the log line, the query output, the run link. A summary is not knowing (Keel Principle 8).

## Layout

- `architecture.md` — current system architecture; kept in sync with implementation.
- `decisions.md` — index of all decisions; the decisions themselves live in `decisions/`.
- `decisions/` — one numbered file per decision (`D-001`, `D-002`, …).
- `findings.md` — lessons learned; dated entries, newest last.
- `test_plan.md` — all tests, in tabular format.
- `keel-v5/`, `keel-v6/` — the governing discipline documents this project follows.
- `sessions/` — Planner session close-outs and pre-work docs (`MESG-close-out-YYYY-MM-DD.md`, `MESG-pre-work-next-session.md`).

Ground on `architecture.md`, `decisions.md`, `findings.md`, `test_plan.md`, and the most recent files in `sessions/` at the start of every work session.
