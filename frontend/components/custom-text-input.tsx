import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { colors } from "../constants/colors";
import { useState, Ref, ComponentRef } from "react";
import Ionicons from '@expo/vector-icons/Ionicons';

type Props = {
  label: string;
  placeholder: string;
  value: string;
  onChangeText: (value: string) => void;
  keyboardType?: "default" | "email-address" | "numeric" | "phone-pad" ; // If this ever has to be used with more keyboard types, we can add them here.
  onSubmitEditing?: () => void;
  isPassword?: boolean;
  returnKeyType?: "next" | "done" | "go" | "none";
  ref?: Ref<ComponentRef<typeof TextInput>>;
};

export default function CustomTextInput({
  label,
  placeholder,
  value,
  onChangeText,
  keyboardType,
  onSubmitEditing,
  isPassword,
  returnKeyType,
  ref
}: Props){
  const [showPassword, setShowPassword] = useState(false);

  return (
    <View>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.container}>
        <TextInput
          style={styles.input}
          placeholder={placeholder}
          placeholderTextColor="#8592A8"
          value={value}
          onChangeText={onChangeText}
          keyboardType={keyboardType || "default"}
          autoCapitalize="none"
          autoCorrect={false}
          accessibilityLabel={label}
          returnKeyType={returnKeyType || "next"}
          onSubmitEditing={onSubmitEditing}
          secureTextEntry={isPassword ? !showPassword : false}
          ref={ref}
        />

        {isPassword && (
          <Pressable
            onPress={() => setShowPassword(!showPassword)}
            accessibilityRole="button"
            accessibilityLabel={showPassword ? "Hide" : "Show"}
          >
            <Ionicons
              name={showPassword ? "eye-off" : "eye"}
              size={24}
              color={colors.accent}
              style={styles.passwordToggle}
            />
          </Pressable>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 2,
    borderColor: colors.border,
    borderRadius: 16,
    marginVertical: 12,
    backgroundColor: colors.background,
  },
  label: {
    color: colors.secondary,
    fontSize: 14,
    fontWeight: "bold",
    marginTop: 12,
  },
  input: {
    flex: 1,
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 16,
    color: colors.primary,
    fontSize: 16,
  },
  passwordToggle: {
    paddingHorizontal: 16,
    paddingVertical: 12, // This is 12 because 24 + 12 + 12 = 48, which is the height of the input field.
  },
});
