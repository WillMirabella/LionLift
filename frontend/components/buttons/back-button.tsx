import { Pressable, StyleSheet, Text } from "react-native";
import React, { useState } from 'react';
import { colors } from "../../constants/colors";


type Props = {
  onPress: () => void;
};


export default function BackButton({onPress}: Props) {

  const [isPressed, setIsPressed] = useState(false);

  return (
    <Pressable 
      accessibilityRole="button" 
      onPressIn={() => setIsPressed(true)}
      onPressOut={() => setIsPressed(false)}
      onPress={onPress}>
      <Text style={[styles.text, isPressed && styles.textPressed]}>{"←"}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  text: {
    color: colors.secondary,
    fontSize: 36,
    fontWeight: "bold",
    marginVertical: 24,
    position:'absolute'
  },
  textPressed: {
    color: colors.accent
  },
});