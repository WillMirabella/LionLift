import { router, useLocalSearchParams } from "expo-router";
import { useState } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import BigButton from "../components/buttons/big-button";
import CustomTextInput from "../components/custom-text-input";
import { colors } from "../constants/colors";

export default function CreateAddressScreen() {
  const params = useLocalSearchParams<{
    firstName: string;
    lastName: string;
    major: string;
    graduationYear: string;
    bio: string;
  }>();

  const [street, setStreet] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [zipCode, setZipCode] = useState("");

  function handleNext() {
    if (
      !street.trim() ||
      !city.trim() ||
      !state.trim() ||
      !zipCode.trim()
    ) {
      Alert.alert(
        "Missing details",
        "Please enter your street, city, state, and ZIP code to continue."
      );
      return;
    }

    if (!/^\d{5}$/.test(zipCode.trim())) {
      Alert.alert("ZIP code", "Enter a valid five-digit ZIP code.");
      return;
    }

    router.push({
      pathname: "/create-schedule",
      params: {
        firstName: params.firstName,
        lastName: params.lastName,
        major: params.major,
        graduationYear: params.graduationYear,
        bio: params.bio,
        street: street.trim(),
        city: city.trim(),
        state: state.trim(),
        zipCode: zipCode.trim(),
      },
    });
  }

  return (
    <>
      <StatusBar barStyle="light-content" backgroundColor={colors.secondary} />
      <SafeAreaView style={styles.topSafeArea} />

      <View style={styles.container}>
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          style={styles.keyboardContainer}
        >
          <View style={styles.sheet}>
            <Text style={styles.heading}>Add your Address</Text>

            <View style={styles.fields}>
              <CustomTextInput
                label="Street address"
                placeholder="Street address"
                value={street}
                onChangeText={setStreet}
              />

              <CustomTextInput
                label="City"
                placeholder="City"
                value={city}
                onChangeText={setCity}
              />

              <CustomTextInput
                label="State"
                placeholder="State"
                value={state}
                onChangeText={setState}
              />

              <CustomTextInput
                label="ZIP code"
                placeholder="19001"
                value={zipCode}
                onChangeText={setZipCode}
                keyboardType="numeric"
              />
            </View>

            <View style={styles.button}>
              <BigButton text="Next" onPress={handleNext} />
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
  fields: {
    flex: 1,
  },
  button: {
    marginTop: -22,
    marginBottom: 22,
  },
});