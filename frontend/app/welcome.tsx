import { router } from "expo-router/build/global-state/router";
import { Fragment, useState } from "react";
import {
  Platform,
  StyleSheet,
  StatusBar,
  Text,
  View,
} from "react-native";
import { colors } from "../constants/colors";
import CustomTextInput from "../components/custom-text-input";
import BigButton from "../components/buttons/big-button";
import { KeyboardAvoidingView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import Stepper from "../components/stepper";
import BackButton from "../components/buttons/back-button";

const API_URL = process.env.EXPO_PUBLIC_API_URL;

function handleContinue(){
    router.replace({pathname: '/(app)/find-drivers'});
}
export default function Welcome() {
  return (
    <Fragment>
        <StatusBar barStyle="light-content" backgroundColor={colors.secondary} />
        <SafeAreaView style={{ flex: 0, backgroundColor: colors.secondary }} />
        <View style={{ flex: 1, backgroundColor: colors.secondary }}>
          <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined}  style={{ flex: 1 }}>
          <View style={styles.sheet}>
            <Text style={styles.heading}>Welcome</Text>
            <BigButton
              text="Continue to app"
              onPress={() => handleContinue()}
            />
          </View>
        </KeyboardAvoidingView>
      </View>
    </Fragment>
  );
}

const styles = StyleSheet.create({
  sheet: {
    flex: 4,
    backgroundColor: colors.background,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 24,
  },
  heading: {
    color: colors.primary,
    fontSize: 32,
    fontWeight: "bold",
    marginVertical: 24,
  },
});
