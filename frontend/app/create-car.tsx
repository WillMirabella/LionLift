import { router, useLocalSearchParams } from "expo-router";
import { useState } from "react";
import {Alert,KeyboardAvoidingView,Platform, StatusBar, StyleSheet,Text, View, } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import BigButton from "../components/buttons/big-button";
import DriverDetailsSection, {type CarDetails,} from "../components/driver-details-section";
import { colors } from "../constants/colors";

export default function CreateCarScreen() {
  const params = useLocalSearchParams<{
    firstName: string;
    lastName: string;
    major: string;
    graduationYear: string;
    bio: string;
    street: string;
    city: string;
    state: string;
    zipCode: string;
    schedule: string;
    plansToDrive: string;
  }>();

  const [car, setCar] = useState<CarDetails>({
    make: "",
    model: "",
    year: "",
    color: "",
  });
  const [documentsConfirmed, setDocumentsConfirmed] = useState(false);

  function updateCar(field: keyof CarDetails, value: string) {
    setCar((current) => ({ ...current, [field]: value }));
  }

  function handleFinish() {
    if (
      !car.make.trim() ||
      !car.model.trim() ||
      !car.year.trim() ||
      !car.color.trim()
    ) {
      Alert.alert("Missing details", "Please complete all car fields.");
      return;
    }

    const modelYear = Number(car.year.trim());

    if (
      !/^\d{4}$/.test(car.year.trim()) ||
      modelYear < 1998 ||
      modelYear > new Date().getFullYear() + 1
    ) {
      Alert.alert("Model year", "Enter a valid four-digit model year.");
      return;
    }

    if (!documentsConfirmed) {
      Alert.alert(
        "Driver confirmation",
        "Please confirm your license, insurance, and registration are up to date."
      );
      return;
    }

    router.replace({
      pathname: "/(app)/find-drivers",
      params: {
        ...params,
        carMake: car.make.trim(),
        carModel: car.model.trim(),
        carYear: car.year.trim(),
        carColor: car.color.trim(),
        documentsConfirmed: "true",
      },
    });
  }

  return (
    <>
      <StatusBar barStyle="light-content" />
      <SafeAreaView style={styles.topSafeArea} />

      <View style={styles.container}>
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          style={styles.keyboardContainer}
        >
          <View style={styles.sheet}>
            <Text style={styles.heading}>Driver information</Text>

            <View style={styles.fields}>
              <DriverDetailsSection
                car={car}
                onCarChange={updateCar}
                documentsConfirmed={documentsConfirmed}
                onDocumentsConfirmedChange={setDocumentsConfirmed}
              />
            </View>

            <View style={styles.button}>
              <BigButton text="Next" onPress={handleFinish} />
            </View>
          </View>
        </KeyboardAvoidingView>
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  topSafeArea: {
    flex: 0,
    backgroundColor: colors.secondary,
  },
  container: {
    flex: 1,
    backgroundColor: colors.secondary,
  },
  keyboardContainer: {
    flex: 1,
  },
  sheet: {
    flex: 1,
    backgroundColor: colors.background,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    overflow: "hidden",
    paddingHorizontal: 24,
    paddingBottom: 20,
  },
  heading: {
    color: colors.primary,
    fontSize: 32,
    fontWeight: "bold",
    marginTop: 24,
  },
  fields: {},
  button: {
    marginTop: 0,
  },
});