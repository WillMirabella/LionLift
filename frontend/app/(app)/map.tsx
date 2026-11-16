import MapView, { Marker, Circle, Callout, PROVIDER_GOOGLE } from 'react-native-maps';
import { useState, useEffect } from "react";
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

type userLocation = [string, string];

const API_URL = process.env.EXPO_PUBLIC_API_URL;

export default function MapScreen() {
  const [userLocations, setUsers] = useState<userLocation[]>([]);

  useEffect(() => {
    handleGetAllUsers();
  }, [])

  // Trys to verify a verification code
  const handleGetAllUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/api/users/all-locations`, {
        method: 'GET',
      });

      const result: userLocation[] = await response.json();
      setUsers(result);
    } catch (error) {
      console.error('Error submitting data:', error);
    }
  }

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
        {userLocations.map((location, index) => (
          <Marker
            key={index}
            coordinate={{
              latitude: Number(location[0]),
              longitude: Number(location[1]),
            }}
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
        {userLocations.map((location, index) => (
          <Circle
            key={index}
            center={{
              latitude: Number(location[0]),
              longitude: Number(location[1]),
            }}
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
