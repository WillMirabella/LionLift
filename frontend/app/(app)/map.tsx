import { View } from 'react-native';
import CampusMap from '../../components/campus-map';

// Map tab: shows the area around campus
export default function MapScreen() {
  return (
    <View style={{ flex: 1 }}>
      <CampusMap />
    </View>
  );
}
