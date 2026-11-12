import { router } from "expo-router";
import { useState, Fragment, useRef, ComponentRef } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TextInput
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import BigButton from "../components/buttons/big-button";
import CustomTextInput from "../components/custom-text-input";
import { colors } from "../constants/colors";
import Stepper from "../components/stepper";

type TextInputInstance = ComponentRef<typeof TextInput>;

export default function CreateProfileScreen() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [major, setMajor] = useState("");
  const [graduationYear, setGraduationYear] = useState("");

  const inputs = useRef<Array<TextInputInstance | null>>([]);

  
  function handleNext() {
    if (
      !firstName.trim() ||
      !lastName.trim() ||
      !major.trim() ||
      !graduationYear.trim()
    ) {
      Alert.alert("Missing details", "Please complete every field to continue.");
      return;
    }

    if (!/^\d{4}$/.test(graduationYear.trim())) {
      Alert.alert("Graduation year", "Enter a four-digit year, such as 2027.");
      return;
    }

    router.push({
      pathname: "/create-address",
      params: {
        firstName: firstName.trim(),
        lastName: lastName.trim(),
        major: major.trim(),
        graduationYear: graduationYear.trim()
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
                step={4}
                steps={7}
            />
            <Text style={styles.heading}>Enter Information</Text>

            <View style={styles.fields}>
              <View style={{ flexDirection: "row", gap: 12  }}>
                <View style={{ flex: 1 }}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[0] = el; }}
                    label="First Name"
                    placeholder="First Name"
                    value={firstName}
                    onChangeText={setFirstName}
                    returnKeyType="next"
                    onSubmitEditing={() => inputs.current[1]?.focus()}
                  />
                </View>
                <View style={{ flex: 1 }}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[1] = el; }}
                    label="Last Name"
                    placeholder="Last Name"
                    value={lastName}
                    onChangeText={setLastName}
                    returnKeyType="next"
                    onSubmitEditing={() => inputs.current[2]?.focus()}
                  />
                </View>
              </View>

              <View style={{ flexDirection: "row", gap: 12  }}>
                <View style={{ flex: 1 }}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[2] = el; }}
                    label="Major"
                    placeholder="Major"
                    value={major}
                    onChangeText={setMajor}
                    returnKeyType="next"
                    onSubmitEditing={() => inputs.current[3]?.focus()}
                  />
                </View>
                <View style={{ flex: 1, maxWidth:"35%"}}>
                  <CustomTextInput
                    ref={(el) => { inputs.current[3] = el; }}
                    label="Graduation Year"
                    placeholder="2030"
                    value={graduationYear}
                    onChangeText={setGraduationYear}
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
  fields: {
    flex: 1,
  },
  heading: {
    color: colors.primary,
    fontSize: 32,
    fontWeight: "bold",
    marginTop: 24,
  }
});
