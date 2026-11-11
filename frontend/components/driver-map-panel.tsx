import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors } from '../constants/colors';
import { RADIUS_CHOICES, type NearbyDriver } from './use-driver-map';

type Props = {
  radius: number;
  setRadius: (miles: number) => void;
  drivers: NearbyDriver[];
  selected: NearbyDriver | null;
  routeMiles: number;
};

// Panel over the bottom of the map: radius choices, driver count, and the
// selected driver's details. Same on phone and web.
export default function DriverMapPanel({ radius, setRadius, drivers, selected, routeMiles }: Props) {
  return (
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
            Pickup route to campus: about {routeMiles.toFixed(1)} mi in a straight line
          </Text>
        </View>
      ) : (
        <Text style={styles.hint}>Tap a driver to see their route to campus.</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    position: 'absolute',
    left: 12,
    right: 12,
    bottom: 12,
    // Above the web map's own layers
    zIndex: 1000,
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
