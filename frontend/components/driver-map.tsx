import { useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Circle, Marker, Polyline } from 'react-native-maps';
import CampusMap from './campus-map';
import { CAMPUS } from '../constants/campus';
import { colors } from '../constants/colors';
import { SAMPLE_DRIVERS, SAMPLE_RIDER_AREA, type MapDriver } from '../constants/sample-drivers';
import { distanceMiles, milesToMeters, regionAround } from '../utils/geo';

// Search radius choices around the rider, in miles
const RADIUS_CHOICES = [5, 10, 15];

// Each driver's location is only known to about this many miles
const APPROXIMATE_AREA_MILES = 1;

// Pin color from how well the driver's schedule matches the rider's
function matchColor(match: number) {
  if (match >= 75) return '#2E7D4F';
  if (match >= 50) return '#B88A00';
  return '#6B7280';
}

// Drivers near the rider, their approximate areas, and the route to campus
// for the selected driver
export default function DriverMap() {
  const [radius, setRadius] = useState(RADIUS_CHOICES[1]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Drivers inside the search radius, closest first
  const drivers = useMemo(() => {
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

  return (
    <View style={styles.screen}>
      <CampusMap initialRegion={initialRegion}>
        {/* Search radius around the rider */}
        <Circle
          center={SAMPLE_RIDER_AREA}
          radius={milesToMeters(radius)}
          strokeColor={colors.secondary}
          strokeWidth={2}
          fillColor="rgba(150, 190, 230, 0.12)"
        />
        <Marker coordinate={SAMPLE_RIDER_AREA} title="You" description="Your approximate area" pinColor={colors.accent} />

        {drivers.map((driver) => (
          <DriverOnMap
            key={driver.id}
            driver={driver}
            isSelected={driver.id === selected?.id}
            onPress={() => setSelectedId(driver.id)}
          />
        ))}

        {/* Route for the selected driver: their area, then the rider, then campus */}
        {selected && (
          <Polyline
            coordinates={[selected, SAMPLE_RIDER_AREA, CAMPUS]}
            strokeColor={colors.primary}
            strokeWidth={4}
            lineDashPattern={[12, 8]}
          />
        )}
      </CampusMap>

      <View style={styles.panel}>
        <Text style={styles.panelTitle}>Search radius</Text>
        <View style={styles.chips}>
          {RADIUS_CHOICES.map((miles) => (
            <Pressable
              key={miles}
              onPress={() => setRadius(miles)}
              style={[styles.chip, miles === radius && styles.chipActive]}
              accessibilityRole="button"
              accessibilityState={{ selected: miles === radius }}
            >
              <Text style={[styles.chipText, miles === radius && styles.chipTextActive]}>{miles} mi</Text>
            </Pressable>
          ))}
          <Text style={styles.count}>
            {drivers.length} {drivers.length === 1 ? 'driver' : 'drivers'}
          </Text>
        </View>

        {selected ? (
          <View style={styles.details}>
            <Text style={styles.name}>{selected.name}</Text>
            <Text style={styles.line}>
              {selected.match}% schedule match · {selected.miles.toFixed(1)} mi away · {selected.days}
            </Text>
            <Text style={styles.line}>
              Pickup route to campus: about {(selected.miles + distanceMiles(SAMPLE_RIDER_AREA, CAMPUS)).toFixed(1)} mi in a straight line
            </Text>
          </View>
        ) : (
          <Text style={styles.hint}>Tap a driver to see their route to campus.</Text>
        )}
      </View>
    </View>
  );
}

type DriverProps = {
  driver: MapDriver;
  isSelected: boolean;
  onPress: () => void;
};

// One driver: a pin, plus a circle showing the area they could be anywhere in
function DriverOnMap({ driver, isSelected, onPress }: DriverProps) {
  const color = matchColor(driver.match);
  return (
    <>
      <Circle
        center={driver}
        radius={milesToMeters(APPROXIMATE_AREA_MILES)}
        strokeColor={color}
        strokeWidth={isSelected ? 2 : 1}
        fillColor={isSelected ? 'rgba(0, 30, 68, 0.15)' : 'rgba(0, 0, 0, 0.05)'}
      />
      <Marker
        coordinate={driver}
        title={driver.name}
        description={`${driver.match}% schedule match`}
        pinColor={color}
        onPress={onPress}
      />
    </>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  panel: {
    position: 'absolute',
    left: 12,
    right: 12,
    bottom: 12,
    backgroundColor: colors.background,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 14,
    padding: 14,
    gap: 8,
  },
  panelTitle: { color: colors.primary, fontSize: 14, fontWeight: '600' },
  chips: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  chip: {
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 999,
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.primary, fontSize: 14 },
  chipTextActive: { color: colors.background },
  count: { marginLeft: 'auto', color: '#526477', fontSize: 14 },
  details: { gap: 2 },
  name: { color: colors.primary, fontSize: 16, fontWeight: '600' },
  line: { color: '#526477', fontSize: 13 },
  hint: { color: '#526477', fontSize: 13 },
});
