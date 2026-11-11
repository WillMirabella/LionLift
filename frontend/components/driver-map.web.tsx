import 'leaflet/dist/leaflet.css';
import { StyleSheet, View } from 'react-native';
import { Circle, CircleMarker, MapContainer, Polyline, TileLayer, Tooltip } from 'react-leaflet';
import DriverMapPanel from './driver-map-panel';
import { APPROXIMATE_AREA_MILES, matchColor, useDriverMap } from './use-driver-map';
import { CAMPUS } from '../constants/campus';
import { colors } from '../constants/colors';
import { milesToMeters, type Point } from '../utils/geo';

// Web version of driver-map.tsx. react-native-maps has no web support, so the
// browser draws the same map with Leaflet and OpenStreetMap. Metro picks this
// file over driver-map.tsx when building for web.

// Leaflet takes [latitude, longitude] pairs
const latLng = (p: Point): [number, number] => [p.latitude, p.longitude];

export default function DriverMap() {
  const map = useDriverMap();

  // Same starting view as the phone map
  const r = map.initialRegion;
  const bounds: [[number, number], [number, number]] = [
    [r.latitude - r.latitudeDelta / 2, r.longitude - r.longitudeDelta / 2],
    [r.latitude + r.latitudeDelta / 2, r.longitude + r.longitudeDelta / 2],
  ];

  return (
    <View style={styles.screen}>
      <MapContainer bounds={bounds} style={{ height: '100%', width: '100%' }} attributionControl>
        {/* OpenStreetMap asks for this credit on every map that uses its tiles */}
        <TileLayer
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          maxZoom={19}
        />

        {/* Search radius around the rider */}
        <Circle
          center={latLng(map.rider)}
          radius={milesToMeters(map.radius)}
          pathOptions={{ color: colors.secondary, weight: 2, fillColor: colors.accent, fillOpacity: 0.12 }}
        />
        <CircleMarker center={latLng(map.rider)} radius={8} pathOptions={{ color: colors.secondary, fillColor: colors.accent, fillOpacity: 1 }}>
          <Tooltip>You (approximate area)</Tooltip>
        </CircleMarker>

        {/* Campus */}
        <CircleMarker center={latLng(CAMPUS)} radius={10} pathOptions={{ color: colors.background, weight: 3, fillColor: colors.primary, fillOpacity: 1 }}>
          <Tooltip>{CAMPUS.name}</Tooltip>
        </CircleMarker>

        {/* Each driver: their approximate area, and a dot colored by schedule match */}
        {map.drivers.map((driver) => {
          const color = matchColor(driver.match);
          const isSelected = driver.id === map.selected?.id;
          return (
            <Circle
              key={`area-${driver.id}`}
              center={latLng(driver)}
              radius={milesToMeters(APPROXIMATE_AREA_MILES)}
              pathOptions={{ color, weight: isSelected ? 2 : 1, fillColor: isSelected ? colors.primary : '#000000', fillOpacity: isSelected ? 0.15 : 0.05 }}
            />
          );
        })}
        {map.drivers.map((driver) => {
          const isSelected = driver.id === map.selected?.id;
          return (
            <CircleMarker
              key={`pin-${driver.id}`}
              center={latLng(driver)}
              radius={isSelected ? 11 : 8}
              pathOptions={{ color: isSelected ? colors.primary : colors.background, weight: 2, fillColor: matchColor(driver.match), fillOpacity: 1 }}
              eventHandlers={{ click: () => map.select(driver.id) }}
            >
              <Tooltip>{`${driver.name} · ${driver.match}% match`}</Tooltip>
            </CircleMarker>
          );
        })}

        {/* Route for the selected driver: their area, then the rider, then campus */}
        {map.route && (
          <Polyline positions={map.route.map(latLng)} pathOptions={{ color: colors.primary, weight: 4, dashArray: '12 8' }} />
        )}
      </MapContainer>

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

const styles = StyleSheet.create({
  screen: { flex: 1 },
});
