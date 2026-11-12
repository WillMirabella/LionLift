import Ionicons from "@expo/vector-icons/Ionicons";
import { Tabs } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { colors } from "../../constants/colors";

// NavBar from the UML. Each name matches a screen file in this folder.
export default function NavBar() {
  const insets = useSafeAreaInsets();

  return (
    <Tabs
      screenOptions={{
        headerTintColor: colors.primary,
        headerShadowVisible: false,
        tabBarActiveTintColor: colors.secondary,
        tabBarInactiveTintColor: colors.secondary,
        tabBarLabelPosition: "below-icon",
        tabBarStyle: { height: 56 + insets.bottom, backgroundColor: "#FFFFFF" },
        tabBarIconStyle: {
          flex: 1,
          alignItems: 'center',
          justifyContent: 'center',
          margin: 0,
        },
        tabBarLabelStyle: {
          fontSize: 10,
          fontWeight: 'bold',
        },
      }}
    >
      <Tabs.Screen name="index" options={{ href: null }} />
      <Tabs.Screen
        name="browse"
        options={{
          title: "Browse",
          tabBarAccessibilityLabel: "Browse",
          tabBarIcon: ({ focused, color, size }) => (
            <Ionicons name={focused ? "people" : "people-outline"} color={String(color)} size={size} />
          ),
        }}
      />
      <Tabs.Screen
        name="map"
        options={{
          title: "Map",
          headerShown: false,
          tabBarAccessibilityLabel: "Map",
          tabBarIcon: ({ focused, color, size }) => (
            <Ionicons name={focused ? "map" : "map-outline"} color={String(color)} size={size} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          headerShown: false,
          tabBarAccessibilityLabel: "Profile",
          tabBarIcon: ({ focused, color, size }) => (
            <Ionicons name={focused ? "person" : "person-outline"} color={String(color)} size={size} />
          ),
        }}
      />
    </Tabs>
  );
}
