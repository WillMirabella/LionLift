import { View, StyleSheet, Text, Pressable } from "react-native";
import { colors } from "../constants/colors";
import { useState } from "react";

type Props = {
  label: string;
  value: string;
};

export default function RevealableLabeledText({
  label,
  value,
}: Props){
  const [revealed, setRevealed] = useState(false);

  return (
    <View style={styles.row}>
      <Text style={styles.heading}>{label}</Text>
      <View style={{ flex: 1 }} />
      <Pressable
        onPress={() => setRevealed(true)}
      >
        <Text style={styles.subheading}>
          {revealed ? value : "Tap to Reveal"}
        </Text>
      </Pressable>
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
