import CampusMap from './campus-map';

// react-native-maps can't load on web, so the web build skips the drivers and
// shows the same message as the campus map. Metro picks this file for web.
export default function DriverMap() {
  return <CampusMap />;
}
