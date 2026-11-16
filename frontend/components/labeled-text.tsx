import { View, StyleSheet, Text } from "react-native";
import { colors } from "../constants/colors";

type Props = {
  label: string;
  value: string;
};

export default function LabeledText({
  label,
  value,
}: Props){
  return (
    <View style={styles.row}>
      <Text style={styles.heading}>{label}</Text>
      <View style={{ flex: 1 }} />
      <Text style={styles.subheading}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 12,
  },
  heading: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.primary,
  },
  subheading: {
    fontSize: 18,
    fontWeight: "500",
    color: colors.secondary,
  },
  divider: {
    height: 2,
    backgroundColor: colors.border,
    marginVertical: 12,
  },
});
