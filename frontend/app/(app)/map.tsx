import MapView, { Marker, Circle, Callout } from 'react-native-maps';
import { useState } from "react";
import {
  View,
  StyleSheet,
  Dimensions,
  Text
} from "react-native";
import { colors } from "../../constants/colors";
import UserCard from "../../components/user-card";
import { shadowStyles } from '../../constants/shadow';
import { Ionicons } from '@expo/vector-icons';

export default function MapScreen() {
  
  const [markers, setMarkers] = useState([
    {
      latlng: { latitude: 40.22840, longitude: -74.93234 },
    },
    {
      latlng: { latitude: 39.95287, longitude: -75.16548 },
    },
    {
      latlng: { latitude: 40.06967, longitude: -75.12552 },
    }
  ]);

  return (
    <>
      <MapView
        style={styles.map}
        showsPointsOfInterests={false}
        initialRegion={{
          latitude: 40.11533,
          longitude: -75.11078,
          latitudeDelta: 0.50,
          longitudeDelta: 0.50,
        }}
      >
        {/* User markers */}
        {markers.map((marker, index) => (
          <Marker
            key={index}
            coordinate={marker.latlng}
            tracksViewChanges={false}
          >
            <Ionicons
              name={"person"}
              size={36}
              style={{...shadowStyles}}
              color={colors.secondary}
            />
            <Callout tooltip={false}>
              <View style={styles.userCardContainer}>
                  <UserCard mapMode={true}/>
              </View>
            </Callout>
          </Marker>
        ))}

        {/* User radii */}
        {markers.map((marker, index) => (
          <Circle
            key={index}
            center={marker.latlng}
            radius={3000}
            strokeWidth={2}
            strokeColor={`${colors.secondary}80`}
            fillColor={`${colors.accent}80`}
          />
        ))}

        {/* School marker */}
        <Marker coordinate={{latitude: 40.11533, longitude: -75.11078}}>
          <Ionicons
            name={"school"}
            size={36}
            style={{...shadowStyles}}
            color={colors.secondary}
          />
          <Callout>
            <View style={styles.textContainer}>
              <Text style={styles.text}>Penn State Abington</Text>
            </View>
          </Callout>
        </Marker>
      </MapView>
    </>
  );
}

const styles = StyleSheet.create({
  sheet: {
    flex: 4,
    backgroundColor: colors.background,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    overflow: 'hidden'
  },
  map: {
    flex: 1,
  },
  userCardContainer: {
    width: Dimensions.get('window').width * 0.85,
  },
  text: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.primary,
  },
  textContainer: {
    width: Dimensions.get('window').width * 0.60,
    flexDirection:"row",
    justifyContent:"center"
  }
});
