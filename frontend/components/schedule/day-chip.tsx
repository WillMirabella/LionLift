import { StyleSheet, Text, View } from "react-native";
import { colors } from "../../constants/colors";

type Props = {
  children?: string;
  isOn: boolean;
};

export default function DayChip({ children, isOn }: Props) {
  return (
    <View style={styles(isOn).container}>
        <Text style={styles(isOn).text}>{children}</Text>
    </View>
  );
}

const styles = (isOn: boolean) => StyleSheet.create({
  container: {
    backgroundColor: isOn ? colors.accent : colors.border,
    paddingVertical: 4,
    borderRadius: 8,
    flex: 1,
    alignItems: "center",
    marginRight: 8,
  },
  text: {
    color: colors.primary,
    fontSize: 18,
    fontWeight: "bold",
  } 
});
