import { Pressable, StyleSheet, Text, View } from "react-native";
import { colors } from "../constants/colors";
import CustomTextInput from "./custom-text-input";
export type CarDetails = {make: string; model: string; year: string; color: string;};

type Props = {
  car: CarDetails;
  onCarChange: (field: keyof CarDetails, value: string) => void;
  documentsConfirmed: boolean;
  onDocumentsConfirmedChange: (confirmed: boolean) => void;
};

export default function DriverDetailsSection({
  car,
  onCarChange,
  documentsConfirmed,
  onDocumentsConfirmedChange,
}: Props) {
  return (
    <View>
      <CustomTextInput
        label="Make"
        placeholder="Toyota"
        value={car.make}
        onChangeText={(value) => onCarChange("make", value)}
      />

      <CustomTextInput
        label="Model"
        placeholder="Corolla"
        value={car.model}
        onChangeText={(value) => onCarChange("model", value)}
      />

      <CustomTextInput
        label="Year"
        placeholder="2020"
        value={car.year}
        onChangeText={(value) => onCarChange("year", value)}
        keyboardType="numeric"
      />

      <CustomTextInput
        label="Color"
        placeholder="Blue"
        value={car.color}
        onChangeText={(value) => onCarChange("color", value)}
      />

      <Pressable
        style={styles.confirmation}
        onPress={() =>
          onDocumentsConfirmedChange(!documentsConfirmed)
        }
        accessibilityRole="checkbox"
        accessibilityState={{ checked: documentsConfirmed }}
      >
        <View style={styles.checkbox}>
          {documentsConfirmed && (
            <Text style={styles.checkmark}>X</Text>
          )}
        </View>

        <Text style={styles.confirmationText}>
          I confirm my driver’s license, car insurance, and registration are
          up to date.
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  confirmation: {
  flexDirection: "row",
  alignItems: "center",
  gap: 12,
  marginTop: 0,
},
  checkbox: {
    width: 26,
    height: 26,
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: 5,
    alignItems: "center",
    justifyContent: "center",
  },
  checkmark: {
    color: colors.primary,
    fontSize: 18,
    fontWeight: "bold",
  },
  confirmationText: {
    flex: 1,
    color: colors.primary,
    fontSize: 14,
    lineHeight: 20,
  },
});