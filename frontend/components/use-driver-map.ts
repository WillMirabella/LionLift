import { useMemo, useState } from 'react';
import { CAMPUS } from '../constants/campus';
import { SAMPLE_DRIVERS, SAMPLE_RIDER_AREA, type MapDriver } from '../constants/sample-drivers';
import { distanceMiles, regionAround } from '../utils/geo';

// Shared by the phone map (driver-map.tsx) and the web map (driver-map.web.tsx),
// so both show the same drivers, radius and route.

// Search radius choices around the rider, in miles
export const RADIUS_CHOICES = [5, 10, 15];

// Each driver's location is only known to about this many miles
export const APPROXIMATE_AREA_MILES = 1;

// A driver with their distance from the rider, in miles
export type NearbyDriver = MapDriver & { miles: number };

// Pin color from how well the driver's schedule matches the rider's
export function matchColor(match: number) {
  if (match >= 75) return '#2E7D4F';
  if (match >= 50) return '#B88A00';
  return '#6B7280';
}

export function useDriverMap() {
  const [radius, setRadius] = useState(RADIUS_CHOICES[1]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Drivers inside the search radius, closest first
  const drivers: NearbyDriver[] = useMemo(() => {
    return SAMPLE_DRIVERS
      .map((driver) => ({ ...driver, miles: distanceMiles(SAMPLE_RIDER_AREA, driver) }))
      .filter((driver) => driver.miles <= radius)
      .sort((a, b) => a.miles - b.miles);
  }, [radius]);

  // A driver outside the new radius can't stay selected
  const selected = drivers.find((driver) => driver.id === selectedId) ?? null;

  // Start zoomed to fit the rider, campus and the widest search radius
  const initialRegion = useMemo(() => {
    const reach = Math.max(...RADIUS_CHOICES) / 69;
    return regionAround([
      CAMPUS,
      { latitude: SAMPLE_RIDER_AREA.latitude + reach, longitude: SAMPLE_RIDER_AREA.longitude },
      { latitude: SAMPLE_RIDER_AREA.latitude - reach, longitude: SAMPLE_RIDER_AREA.longitude },
    ], 1.1);
  }, []);

  // Straight-line pickup route: driver's area, then the rider, then campus
  const route = selected ? [selected, SAMPLE_RIDER_AREA, CAMPUS] : null;
  const routeMiles = selected ? selected.miles + distanceMiles(SAMPLE_RIDER_AREA, CAMPUS) : 0;

  return {
    radius, setRadius, drivers, selected, select: setSelectedId,
    initialRegion, route, routeMiles, rider: SAMPLE_RIDER_AREA,
  };
}
