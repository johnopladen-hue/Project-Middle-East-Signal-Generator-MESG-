import PropTypes from "prop-types";
import { Table } from "../components/primitives/Table";

/** Per-source access + reliability + rationale (TDD §9.1). */
export function SourceAssessmentTable({ assessments }) {
  return (
    <Table
      columns={[
        { key: "source_name", header: "Source" },
        { key: "access_level", header: "Access" },
        {
          key: "reliability",
          header: "Reliability",
          render: (row) => `${Math.round(row.reliability * 100)}%`,
        },
        { key: "rationale", header: "Rationale" },
      ]}
      rows={assessments}
      getRowKey={(row) => row.source_id}
    />
  );
}

SourceAssessmentTable.propTypes = {
  assessments: PropTypes.arrayOf(
    PropTypes.shape({
      source_id: PropTypes.number.isRequired,
      source_name: PropTypes.string.isRequired,
      access_level: PropTypes.string.isRequired,
      reliability: PropTypes.number.isRequired,
      rationale: PropTypes.string.isRequired,
    }),
  ).isRequired,
};
