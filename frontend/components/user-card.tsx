/*
 * Component for the user card that will be displayed in the "market place"
 * This should be able to showcase the pfp of the user but also have a fallback
 * in case they do not have one. Maybe the fallback should be on the user profile side.
 */

import { View, StyleSheet, Text } from "react-native";
import { colors } from "../constants/colors";
import DaySchedule from "./schedule/day-schedule";
import { shadowStyles } from "../constants/shadow";
import { map } from "../eslint.config";

type Props = {
  expanded?: boolean;
  mapMode?: boolean;
};


export default function UserCard({ expanded=false, mapMode=false}: Props) {

  const isMapMode = mapMode ?? false;

  return (
    <View style={styles(mapMode).card} accessibilityRole="button">
        <View style={{ flexDirection: "row" }}>
            <View style={styles(mapMode).profilePicture}/>
            <View style={{ flex: 1, justifyContent: "space-between", marginVertical: 8 }}>
                <Text style={styles(mapMode).heading}>Placeholder Name</Text>
                <Text style={styles(mapMode).subheading}>4 miles away</Text> 
                <Text style={styles(mapMode).subheading}>99% match</Text>     
            </View>
        </View>

        <DaySchedule></DaySchedule>
        
        {expanded && <View style={styles(mapMode).map}></View>}
        
    </View>
  );
}

const styles = (mapMode: boolean | undefined) => StyleSheet.create({
  card: {
    backgroundColor: (mapMode ?? false) ? "transparent" : colors.background,
    borderWidth: 0,
    borderColor: (mapMode ?? false) ? "transparent" : colors.secondary,
    padding: (mapMode ?? false) ? 0 : 16,
    borderRadius: (mapMode ?? false) ? 0 : 24,
    marginVertical: (mapMode ?? false) ? 0 : 12,
    ...(!(mapMode ?? false) && shadowStyles),
  },
  profilePicture: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.border,
    marginRight: 16
  },
  map: {
    minHeight: 300,
    borderRadius: 8,
    marginTop: 16,
    backgroundColor: colors.border,
  },
  heading: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.primary
  },
  subheading: {
    fontSize: 18,
    fontWeight: "500",
    color: colors.secondary
  }
});

