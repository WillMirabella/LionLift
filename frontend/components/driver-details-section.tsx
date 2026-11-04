import { Pressable, StyleSheet, Text, View } from "react-native";
import { colors } from "../constants/colors";
import CustomTextInput from "./custom-text-input";

export type CarDetails = {
  make: string;
  model: string;
  year: string;
  color: string;
  plate: string;
  seats: string;
};

type Props = {
  car: CarDetails;
  onCarChange: (field: keyof CarDetails, value: string) => void;
  payments: string[];
  onTogglePayment: (method: string) => void;
  documentsConfirmed: boolean;
  onDocumentsConfirmedChange: (confirmed: boolean) => void;
};

const paymentOptions = ["Venmo", "Cash", "Gas"];

export default function DriverDetailsSection({
  car,
  onCarChange,
  payments,
  onTogglePayment,
  documentsConfirmed,
  onDocumentsConfirmedChange,
}: Props) {
  return (
    <View>
      <Text style={styles.heading}>Please Enter Your Car Info</Text>

      <CustomTextInput
        label="Make"
        placeholder="Toyota"
        value={car.make}
        onChangeText={value => onCarChange("make", value)}
      />

      <CustomTextInput
        label="Model"
        placeholder="Corolla"
        value={car.model}
        onChangeText={value => onCarChange("model", value)}
      />

      <CustomTextInput
        label="Model year"
        placeholder="2020"
        value={car.year}
        onChangeText={value => onCarChange("year", value)}
        keyboardType="numeric"
      />

      <CustomTextInput
        label="Color"
        placeholder="Blue"
        value={car.color}
        onChangeText={value => onCarChange("color", value)}
      />

      <CustomTextInput
        label="License plate"
        placeholder="Plate number"
        value={car.plate}
        onChangeText={value => onCarChange("plate", value)}
      />

      <CustomTextInput
        label="Available passenger seats"
        placeholder="Do not include your seat"
        value={car.seats}
        onChangeText={value => onCarChange("seats", value)}
        keyboardType="numeric"
      />

      <Text style={styles.heading}>Preferred payment methods</Text>
      <Text style={styles.description}>Select all that apply.</Text>

      <View style={styles.paymentOptions}>
        {paymentOptions.map(method => {
          const selected = payments.includes(method);

          return (
            <Pressable
              key={method}
              onPress={() => onTogglePayment(method)}
              accessibilityRole="checkbox"
              accessibilityState={{ checked: selected }}
              style={[styles.payment, selected && styles.paymentSelected]}
            >
              <Text style={styles.optionText}>
                {selected ? "" : ""}
                {method}
              </Text>
            </Pressable>
          );
        })}
      </View>

      <Pressable
        style={styles.confirmation}
        onPress={() => onDocumentsConfirmedChange(!documentsConfirmed)}
        accessibilityRole="checkbox"
        accessibilityState={{ checked: documentsConfirmed }}
      >
        <View style={styles.checkbox}>
          <Text style={styles.optionText}>
            {documentsConfirmed ? "X" : ""}
          </Text>
        </View>

        <Text style={styles.confirmationText}>
          I confirm that my car registration, insurance, and driver’s license
          are up to date.
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  heading: {
    color: colors.primary,
    fontSize: 23,
    fontWeight: "bold",
    marginTop: 24,
    marginBottom: 16,
  },
  description: {
    color: colors.primary,
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 12,
  },
  paymentOptions: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  payment: {
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  paymentSelected: {
    backgroundColor: colors.accent,
    borderWidth: 2,
  },
  optionText: {
    color: colors.primary,
    fontSize: 16,
  },
  confirmation: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
    marginTop: 28,
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
  confirmationText: {
    flex: 1,
    color: colors.primary,
    fontSize: 15,
    lineHeight: 22,
  },
});