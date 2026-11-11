import { router } from "expo-router";
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

export default function CreateProfileScreen() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [major, setMajor] = useState("");
  const [graduationYear, setGraduationYear] = useState("");
  const [bio, setBio] = useState("");

  function handleNext() {
    if (
      !firstName.trim() ||
      !lastName.trim() ||
      !major.trim() ||
      !graduationYear.trim() ||
      !bio.trim()
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
        graduationYear: graduationYear.trim(),
        bio: bio.trim(),
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
            <Text style={styles.heading}>Create your profile</Text>

            <View style={styles.fields}>
              <CustomTextInput
                label="First name"
                placeholder="Your first name"
                value={firstName}
                onChangeText={setFirstName}
              />

              <CustomTextInput
                label="Last name"
                placeholder="Your last name"
                value={lastName}
                onChangeText={setLastName}
              />

              <CustomTextInput
                label="Major"
                placeholder="Your major"
                value={major}
                onChangeText={setMajor}
              />

              <CustomTextInput
                label="Graduation year"
                placeholder="2027"
                value={graduationYear}
                onChangeText={setGraduationYear}
                keyboardType="numeric"
              />

              <CustomTextInput
                label="Bio"
                placeholder="Tell other students about yourself"
                value={bio}
                onChangeText={setBio}
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
  fields: {
    flex: 1,
  },
  heading: {
    color: colors.primary,
    fontSize: 32,
    fontWeight: "bold",
    marginTop: 24,
  },
  button: {
  marginTop: -14,
  marginBottom: 14,
},
});