/**
 * Captured API responses - NOT hand-written. Produced by
 * `python scripts/capture_frontend_fixtures.py` running the real UCDP/OFAC
 * harvesters over the genuine excerpts in backend/tests/fixtures/ and calling
 * the real endpoints ("harvest, never generate", D-012/D-013). Stories in
 * geo_items_centcom.json come from the repo's own labelled synthetic seed
 * (app.dev_seed, "[SYNTHETIC — DEV SEED]").
 *
 * Look records up by name via these helpers rather than hard-coding ids -
 * ids are autoincrement and can shift on re-capture.
 */
import geoItemsCentcom from "./geo_items_centcom.json";
import organizationDetails from "./organization_details.json";
import organizations from "./organizations.json";
import regions from "./regions.json";

export { geoItemsCentcom, organizationDetails, organizations, regions };

export function orgSummaryByName(name) {
  const org = organizations.find((o) => o.name === name);
  if (!org) throw new Error(`No captured organization named ${name}`);
  return org;
}

export function orgDetailByName(name) {
  const detail = Object.values(organizationDetails).find((o) => o.name === name);
  if (!detail) throw new Error(`No captured organization profile named ${name}`);
  return detail;
}
