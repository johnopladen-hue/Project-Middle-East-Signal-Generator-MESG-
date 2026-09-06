import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { Badge } from "../components/primitives/Badge";
import { Tag } from "../components/primitives/Tag";
import { ImminentPill } from "./ImminentPill";
import { SeverityMark } from "./SeverityMark";

export function SignalRow({ signal }) {
  return (
    <Link
      to={`/alerts/${signal.id}`}
      className="flex items-center gap-3 rounded-md border border-rule bg-surface-raised p-3 text-sm
        hover:border-accent
        focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
    >
      <SeverityMark severity={signal.severity} />
      {signal.is_imminent ? <ImminentPill /> : null}
      <Tag>{signal.type}</Tag>
      <span className="flex-1 text-ink">{signal.story_title}</span>
      <Badge>{signal.status}</Badge>
      <time className="font-mono text-xs text-ink-muted" dateTime={signal.created_at}>
        {new Date(signal.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
      </time>
    </Link>
  );
}

SignalRow.propTypes = {
  signal: PropTypes.shape({
    id: PropTypes.number.isRequired,
    story_title: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    severity: PropTypes.string.isRequired,
    is_imminent: PropTypes.bool.isRequired,
    status: PropTypes.string.isRequired,
    created_at: PropTypes.string.isRequired,
  }).isRequired,
};
