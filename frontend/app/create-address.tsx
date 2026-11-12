import { router, useLocalSearchParams } from "expo-router";
import { useState, useRef, Fragment } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TextInputInstance
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import BigButton from "../components/buttons/big-button";
import CustomTextInput from "../components/custom-text-input";
import { colors } from "../constants/colors";
import Stepper from "../components/stepper";

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

  const inputs = useRef<Array<TextInputInstance | null>>([]);

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
    <Fragment>
      <StatusBar barStyle="light-content" backgroundColor={colors.secondary} />
      <SafeAreaView style={{ flex: 0, backgroundColor: colors.secondary }} />
      <View style={styles.container}>
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined}  style={{ flex: 1 }}>
          <View style={styles.sheet}>
            <Stepper
                step={5}
                steps={7}
            />
            <Text style={styles.heading}>Add your Address</Text>

            <View style={styles.fields}>
              <View style={{ flexDirection: "row", gap: 12  }}>
                <View style={{ flex: 1 }}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[0] = el; }}
                    label="Street address"
                    placeholder="Street address"
                    value={street}
                    onChangeText={setStreet}
                    returnKeyType="next"
                    onSubmitEditing={() => inputs.current[1]?.focus()}
                  />
                </View>
                <View style={{ flex: 1 }}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[1] = el; }}
                    label="City"
                    placeholder="City"
                    value={city}
                    onChangeText={setCity}
                    returnKeyType="next"
                    onSubmitEditing={() => inputs.current[2]?.focus()}
                  />
                </View>
              </View>
              <View style={{ flexDirection: "row", gap: 12  }}>
                <View style={{ flex: 1 }}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[2] = el; }}
                    label="State"
                    placeholder="State"
                    value={state}
                    onChangeText={setState}
                    returnKeyType="next"
                    onSubmitEditing={() => inputs.current[3]?.focus()}
                  />
                </View>
                <View style={{ flex: 1 }}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[3] = el; }}
                    label="ZIP code"
                    placeholder="19001"
                    value={zipCode}
                    onChangeText={setZipCode}
                    keyboardType="numeric"
                    returnKeyType="done"
                    onSubmitEditing={handleNext}
                  />
                </View>
              </View>
              <BigButton text="Next" onPress={handleNext} />
            </View>
          </View>
        </KeyboardAvoidingView>
      </View>
    </Fragment>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.secondary,
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
  }
});