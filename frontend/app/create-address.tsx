import { router, useLocalSearchParams } from "expo-router";
import { useState, useRef, Fragment, useEffect } from "react";
import {
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
import BackButton from "../components/buttons/back-button";

export default function CreateAddressScreen() {
  const params = useLocalSearchParams<{
    email: string;
    firstName: string;
    lastName: string;
    major: string;
    graduationYear: string;
    street?: string;
    city?: string;
    state?: string;
    zipCode?: string;
    schedule?: string;
    driver?: string;
    carMake?: string;
    carModel?: string;
    carYear?: string;
    carColor?: string;
  }>();

  const [street, setStreet] = useState(params.street ?? "");
  const [city, setCity] = useState(params.city ?? "");
  const [state, setState] = useState(params.state ?? "");
  const [zipCode, setZipCode] = useState(params.zipCode ?? "");

  useEffect(() => {
    if (params.street !== undefined) setStreet(params.street);
    if (params.city !== undefined) setCity(params.city);
    if (params.state !== undefined) setState(params.state);
    if (params.zipCode !== undefined) setZipCode(params.zipCode);
  }, [params.street, params.city, params.state, params.zipCode]);

  const inputs = useRef<Array<TextInputInstance | null>>([]);
  const [errorText, setErrorText] = useState("");

  function handleNext() {
    if (
      !street.trim() ||
      !city.trim() ||
      !state.trim() ||
      !zipCode.trim()
    ) {
      setErrorText("Enter all information to continue");
      return;
    }

    if (!/^\d{5}$/.test(zipCode.trim())) {
      setErrorText("Enter a valid five-digit ZIP Code");
      return;
    }

    router.navigate({
      pathname: "/create-schedule",
      params: {
        ...params,
        street: street.trim(),
        city: city.trim(),
        state: state.trim(),
        zipCode: zipCode.trim(),
      },
    });
  }

  function goBack(){
    router.navigate({
      pathname: "/create-profile",
      params: {
        ...params,
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
            <BackButton
              onPress={goBack}
            />
            <Stepper
                step={5}
                steps={7}
            />
            <Text style={styles.heading}>Enter Address</Text>

            <View style={styles.fields}>
              <View style={{ flexDirection: "row", gap: 12  }}>
                <View style={{ flex: 1 }}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[0] = el; }}
                    label="Street Address"
                    placeholder="1600 Woodland Rd"
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
                    placeholder="Abington"
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
                    placeholder="PA"
                    value={state}
                    onChangeText={setState}
                    returnKeyType="next"
                    onSubmitEditing={() => inputs.current[3]?.focus()}
                  />
                </View>
                <View style={{ flex: 1 }}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[3] = el; }}
                    label="ZIP Code"
                    placeholder="19001"
                    value={zipCode}
                    onChangeText={setZipCode}
                    keyboardType="numeric"
                    returnKeyType="done"
                    onSubmitEditing={handleNext}
                  />
                </View>
              </View>
              {errorText.length > 0 && (
                <Text style={styles.errorText}>{errorText}</Text>
              )}
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
  },
  errorText: {
    color: colors.error,
    fontSize: 14,
    fontWeight: "bold"
  },
});