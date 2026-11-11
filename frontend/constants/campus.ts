import type { Region } from 'react-native-maps';

// Penn State Abington, 1600 Woodland Road, Abington, PA
export const CAMPUS = {
  name: 'Penn State Abington',
  latitude: 40.1175,
  longitude: -75.1091,
};

// About 15 miles across, enough to see most commutes to campus
export const CAMPUS_REGION: Region = {
  latitude: CAMPUS.latitude,
  longitude: CAMPUS.longitude,
  latitudeDelta: 0.22,
  longitudeDelta: 0.22,
};
