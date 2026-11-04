import { StyleSheet, Text, View } from "react-native";
import { colors } from "../../constants/colors";
import DayChip from "./day-chip";

export default function DaySchedule() {
  return (
    <View
      style={{
        flexDirection: "row",
        justifyContent: "space-between",
        marginRight: -8,
        marginTop: 16,
      }}
      accessibilityRole="button"
    >
      <DayChip isOn={true}>M</DayChip>
      <DayChip isOn={false}>T</DayChip>
      <DayChip isOn={true}>W</DayChip>
      <DayChip isOn={true}>Th</DayChip>
      <DayChip isOn={false}>F</DayChip>
    </View>
  );
}