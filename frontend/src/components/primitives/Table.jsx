import PropTypes from "prop-types";

export function Table({ columns, rows, getRowKey }) {
  return (
    <table className="w-full border-collapse text-sm">
      <thead>
        <tr className="border-b border-rule text-left text-ink-muted">
          {columns.map((column) => (
            <th key={column.key} scope="col" className="px-3 py-2 font-medium">
              {column.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={getRowKey(row)} className="border-b border-rule last:border-0">
            {columns.map((column) => (
              <td key={column.key} className="px-3 py-2 text-ink">
                {column.render ? column.render(row) : row[column.key]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

Table.propTypes = {
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      header: PropTypes.string.isRequired,
      render: PropTypes.func,
    }),
  ).isRequired,
  rows: PropTypes.arrayOf(PropTypes.object).isRequired,
  getRowKey: PropTypes.func.isRequired,
};
