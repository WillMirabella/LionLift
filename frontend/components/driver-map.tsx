import { StyleSheet, View } from 'react-native';
import { Circle, Marker, Polyline } from 'react-native-maps';
import CampusMap from './campus-map';
import DriverMapPanel from './driver-map-panel';
import { APPROXIMATE_AREA_MILES, matchColor, useDriverMap, type NearbyDriver } from './use-driver-map';
import { colors } from '../constants/colors';
import { milesToMeters } from '../utils/geo';

// Phone version: drivers near the rider, their approximate areas, and the
// route to campus for the selected driver. driver-map.web.tsx is the web version.
export default function DriverMap() {
  const map = useDriverMap();

  return (
    <View style={styles.screen}>
      <CampusMap initialRegion={map.initialRegion}>
        {/* Search radius around the rider */}
        <Circle
          center={map.rider}
          radius={milesToMeters(map.radius)}
          strokeColor={colors.secondary}
          strokeWidth={2}
          fillColor="rgba(150, 190, 230, 0.12)"
        />
        <Marker coordinate={map.rider} title="You" description="Your approximate area" pinColor={colors.accent} />

        {map.drivers.map((driver) => (
          <DriverOnMap
            key={driver.id}
            driver={driver}
            isSelected={driver.id === map.selected?.id}
            onPress={() => map.select(driver.id)}
          />
        ))}

        {/* Route for the selected driver: their area, then the rider, then campus */}
        {map.route && (
          <Polyline coordinates={map.route} strokeColor={colors.primary} strokeWidth={4} lineDashPattern={[12, 8]} />
        )}
      </CampusMap>

      <DriverMapPanel
        radius={map.radius}
        setRadius={map.setRadius}
        drivers={map.drivers}
        selected={map.selected}
        routeMiles={map.routeMiles}
      />
    </View>
  );
}

type DriverProps = {
  driver: NearbyDriver;
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
});
