import type { Point } from '../utils/geo';

// A driver as the map shows them. Locations are approximate (to about a mile),
// never a home address.
export type MapDriver = Point & {
  id: number;
  name: string;
  // Schedule match with the signed-in rider, 0 to 100
  match: number;
  days: string;
};

// Placeholder data until the map reads drivers from /api/users/
export const SAMPLE_DRIVERS: MapDriver[] = [
  { id: 1, name: 'Jordan M.', latitude: 40.0959, longitude: -75.1252, match: 92, days: 'Mon, Wed, Fri' },
  { id: 2, name: 'Priya S.', latitude: 40.144, longitude: -75.1157, match: 78, days: 'Mon to Thu' },
  { id: 3, name: 'Chris T.', latitude: 40.129, longitude: -75.0629, match: 64, days: 'Tue, Thu' },
  { id: 4, name: 'Dana K.', latitude: 40.0765, longitude: -75.1263, match: 55, days: 'Mon, Wed' },
  { id: 5, name: 'Sam R.', latitude: 40.1784, longitude: -75.1285, match: 41, days: 'Fri' },
  { id: 6, name: 'Alex P.', latitude: 40.2068, longitude: -75.0999, match: 83, days: 'Mon to Fri' },
  { id: 7, name: 'Morgan L.', latitude: 40.2415, longitude: -75.2838, match: 70, days: 'Tue, Wed, Thu' },
];

// The signed-in rider's approximate area, until it comes from /api/me
export const SAMPLE_RIDER_AREA: Point = { latitude: 40.1023, longitude: -75.1524 };
