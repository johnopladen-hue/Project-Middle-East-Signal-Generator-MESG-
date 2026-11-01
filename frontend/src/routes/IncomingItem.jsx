import { ArrowLeft, MapPin } from "lucide-react";
import PropTypes from "prop-types";
import { Link, useLocation, useParams } from "react-router-dom";
import { Card } from "../components/primitives/Card";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { useRawItem } from "../domain/useRawItems";
import { ItemCard } from "./Incoming";

/** Where the map put this item, and the item's own words that put it there
 * (D-023). Machine-matched from the original text; never from the triage
 * translation, and never presented as verified. */
function LocationNote({ location }) {
  if (location == null) {
    return <p className="text-xs text-ink-muted">Not checked for a place name yet.</p>;
  }
  if (location.status !== "located") {
    return <p className="text-xs text-ink-muted">No place name found in the original text, so this item is not on the map.</p>;
  }
  return (
    <p className="flex flex-wrap items-center gap-1 text-xs text-ink-muted">
      <MapPin size={14} aria-hidden="true" />
      <span>
        On the map at <span className="font-medium text-ink">{location.place_name}</span>, {location.country} ({location.precision}{" "}
        level), from the words{" "}
        <span dir="auto" className="font-medium text-ink">
          “{location.matched_text}”
        </span>{" "}
        in the original text. Machine-matched, not verified.
      </span>
    </p>
  );
}

LocationNote.propTypes = {
  location: PropTypes.shape({
    status: PropTypes.oneOf(["located", "none"]).isRequired,
    place_name: PropTypes.string,
    country: PropTypes.string,
    precision: PropTypes.string,
    matched_text: PropTypes.string,
  }),
};

/** The item page a map dot opens (D-023): the same card as /incoming, plus where it was placed. */
export function IncomingItem() {
  const { id } = useParams();
  const fromMap = useLocation().state?.from === "map";
  const itemQuery = useRawItem(id);

  return (
    <div className="mx-auto max-w-3xl space-y-3 p-4">
      <Link
        to={fromMap ? "/map" : "/incoming"}
        className="inline-flex items-center gap-1 text-sm text-accent hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        <ArrowLeft size={16} aria-hidden="true" />
        {fromMap ? "Back to the map" : "All incoming items"}
      </Link>

      {itemQuery.isLoading ? (
        <Card>
          <Skeleton lines={4} />
        </Card>
      ) : itemQuery.isError ? (
        <ErrorState message="Couldn't load this item." onRetry={() => itemQuery.refetch()} />
      ) : (
        <>
          <ItemCard item={itemQuery.data} />
          <LocationNote location={itemQuery.data.location} />
        </>
      )}
    </div>
  );
}
