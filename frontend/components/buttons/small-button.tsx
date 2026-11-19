import { Pressable, StyleSheet, Text } from "react-native";
import { colors } from "../../constants/colors";

type Props = {
  text: string;
  onPress: () => void;
  disabled?: boolean;
};

export default function SmallButton({ text, onPress }: Props) {
  return (
    <Pressable accessibilityRole="button" onPress={onPress}>
      <Text style={styles.text}>{text}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  text: {
    color: colors.accent,
    fontSize: 14,
    fontWeight: "bold",
    marginVertical: 12,
  },
});
