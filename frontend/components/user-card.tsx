/*
 * Component for the user card that will be displayed in the "market place"
 * This should be able to showcase the pfp of the user but also have a fallback
 * in case they do not have one. Maybe the fallback should be on the user profile side.
 */

import { View, StyleSheet, Text } from "react-native";
import { colors } from "../constants/colors";
import DaySchedule from "./schedule/day-schedule";
import { shadowStyles } from "../constants/shadow";

type Props = {
  expanded?: boolean;
};

export default function UserCard({ expanded=false }: Props) {
  return (
    <View style={styles.card} accessibilityRole="button">
        <View style={{ flexDirection: "row" }}>
            <View style={styles.profilePicture}/>
            <View style={{ flex: 1, justifyContent: "space-between", marginVertical: 8 }}>
                <Text style={styles.heading}>Placeholder Name</Text>
                <Text style={styles.subheading}>4 miles away</Text> 
                <Text style={styles.subheading}>99% match</Text>     
            </View>
        </View>

        <DaySchedule></DaySchedule>
        
        {expanded && <View style={styles.map}></View>}
        
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.background,
    borderWidth: 0,
    borderColor: colors.secondary,
    padding: 16,
    borderRadius: 24,
    marginVertical: 12,
    ...shadowStyles
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

