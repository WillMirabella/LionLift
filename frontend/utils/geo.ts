// Distance helpers for the map. Same formula as the backend (user_search.py).

export type Point = { latitude: number; longitude: number };

// Mean radius of the Earth in miles, same value as the backend
export const EARTH_RADIUS_MILES = 3958.8;

// Map circles take their radius in meters
export const METERS_PER_MILE = 1609.344;

const toRadians = (degrees: number) => (degrees * Math.PI) / 180;

// Great-circle (haversine) distance in miles between two points
export function distanceMiles(a: Point, b: Point): number {
  const latA = toRadians(a.latitude);
  const latB = toRadians(b.latitude);
  const dLat = latB - latA;
  const dLon = toRadians(b.longitude - a.longitude);

  const h = Math.sin(dLat / 2) ** 2 + Math.cos(latA) * Math.cos(latB) * Math.sin(dLon / 2) ** 2;
  // Rounding can push h slightly past 1 for points on opposite sides of the Earth
  return 2 * EARTH_RADIUS_MILES * Math.asin(Math.sqrt(Math.min(1, Math.max(0, h))));
}

export function milesToMeters(miles: number): number {
  return miles * METERS_PER_MILE;
}

// Smallest map region that shows every point, with some space around the edges
export function regionAround(points: Point[], padding = 1.3) {
  const lats = points.map((p) => p.latitude);
  const lons = points.map((p) => p.longitude);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);

  return {
    latitude: (minLat + maxLat) / 2,
    longitude: (minLon + maxLon) / 2,
    // Never zoom in closer than about a mile
    latitudeDelta: Math.max((maxLat - minLat) * padding, 0.02),
    longitudeDelta: Math.max((maxLon - minLon) * padding, 0.02),
  };
}
