import type { ReactNode } from 'react';
import { StyleSheet } from 'react-native';
import MapView, { Marker, type Region } from 'react-native-maps';
import { CAMPUS, CAMPUS_REGION } from '../constants/campus';
import { colors } from '../constants/colors';

type Props = {
  // Where the map starts, campus by default
  initialRegion?: Region;
  // Extra markers, circles and lines drawn on top of the map
  children?: ReactNode;
};

// Map centered on campus, with a marker for campus itself
export default function CampusMap({ initialRegion = CAMPUS_REGION, children }: Props) {
  return (
    <MapView
      style={styles.map}
      initialRegion={initialRegion}
      // Keep the map clean so our own markers stand out
      showsPointsOfInterests={false}
      showsBuildings={false}
      toolbarEnabled={false}
      accessibilityLabel="Map of rides to Penn State Abington"
    >
      <Marker
        coordinate={{ latitude: CAMPUS.latitude, longitude: CAMPUS.longitude }}
        title={CAMPUS.name}
        description="Campus"
        pinColor={colors.primary}
      />
      {children}
    </MapView>
  );
}

const styles = StyleSheet.create({
  map: { flex: 1 },
});
