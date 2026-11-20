import { router } from "expo-router/build/global-state/router";
import { Fragment, useState } from "react";
import {
  Alert,
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
import { Ionicons } from "@expo/vector-icons";
import Stepper from "../components/stepper";
import BackButton from "../components/buttons/back-button";
import { useLocalSearchParams } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL;

export default function SetPasswordScreen() {
  // token comes from verify-code, mode=reset means this is "Forgot password?" instead of sign up
  const { token, mode } = useLocalSearchParams<{ email: string; token: string; mode?: string }>();
  const isReset = mode === "reset";
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorText, setErrorText] = useState("");

  const handleSetPassword = async () => {
    if(!passwordsMatch()) setErrorText("Passwords must match");
    else if(!meetsRequirements(password)) setErrorText("Password must meet requirements");
    else{
      const endpoint = isReset ? "reset-password" : "set-password";
      const response = await fetch(`${API_URL}/api/auth/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ password: password }),
      });
      const result = await response.json();
      if (result['error']!=null){
        console.log(result['error']);
        setErrorText(result['error']);
      }
      else if (isReset) {
        Alert.alert("Password reset", "You can now sign in with your new password.");
        router.replace({
          pathname: '/sign-in'
        });
      }
      else{
        router.replace({
          pathname: '/(app)/browse'
        });
      }
    }
  }

  // The code was already used up on verify-code, so going back means starting from the email screen
  // (also how the user recovers if their token expired)
  function goBack(){
    router.replace({
      pathname: '/verify-email',
      params: isReset ? { mode: "reset" } : {},
    });
  }

  function passwordsMatch(){
    return (password == confirmPassword);
  }
  function meetsRequirements(text: string){
    return hasLettersAndNumbers(text) &&
           hasUpperCaseAndLowerCase(text) &&
           hasSpecialCharacters(text)
  }

  function hasLettersAndNumbers(text: string) {
    return /^(?=.*[A-Za-z])(?=.*\d)/.test(text);
  }

  function hasUpperCaseAndLowerCase(text: string) {
    return /[a-z]/.test(text) && /[A-Z]/.test(text);
  }

  function hasSpecialCharacters(text: string) {
    return /[^a-zA-Z0-9 ]/.test(text);
  }

  return (
    <Fragment>
        <StatusBar barStyle="light-content" backgroundColor={colors.secondary} />
        <SafeAreaView style={{ flex: 0, backgroundColor: colors.secondary }} />
        <View style={{ flex: 1, backgroundColor: colors.secondary }}>
          <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined}  style={{ flex: 1 }}>
            <View style={styles.sheet}>
              <BackButton
                onPress={goBack}
              />
              {!isReset && (
                <Stepper
                  step={3}
                  steps={5}
                />
              )}
              <Text style={styles.heading}>{isReset ? "New Password" : "Set Password"}</Text>

              <CustomTextInput
                label="Password"
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                keyboardType="default"
                isPassword={true}
              />
              
              {meetsRequirements(password) ? (
              <View>
                  <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                      <Ionicons name={"checkmark-outline"} size={24} color={colors.success} /> 
                      <Text style={styles.successText}>Meets all requirements</Text>
                  </View>
              </View>
                ) : (
                <View>
                    {password.length < 8 ? (
                      <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                        <Ionicons name={"close-outline"} size={24} color={colors.error} /> 
                        <Text style={styles.errorText}>Contains at least 8 characters</Text>
                      </View>
                    ) : (
                      <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                        <Ionicons name={"checkmark-outline"} size={24} color={colors.success} /> 
                        <Text style={styles.successText}>Contains at least 8 characters</Text>
                      </View>
                    )}
                    {!hasUpperCaseAndLowerCase(password) ? (
                      <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                        <Ionicons name={"close-outline"} size={24} color={colors.error} /> 
                        <Text style={styles.errorText}>Contains upper and lower case</Text>
                      </View>
                    ) : (
                      <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                        <Ionicons name={"checkmark-outline"} size={24} color={colors.success} /> 
                        <Text style={styles.successText}>Contains upper and lower case</Text>
                      </View>
                    )}
                    {!hasLettersAndNumbers(password) ? (
                      <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                        <Ionicons name={"close-outline"} size={24} color={colors.error} /> 
                        <Text style={styles.errorText}>Contains letters and numbers</Text>
                      </View>
                    ) : (
                      <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                        <Ionicons name={"checkmark-outline"} size={24} color={colors.success} /> 
                        <Text style={styles.successText}>Contains letters and numbers</Text>
                      </View>
                    )}
                    {!hasSpecialCharacters(password) ? (
                      <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                        <Ionicons name={"close-outline"} size={24} color={colors.error} /> 
                        <Text style={styles.errorText}>Contains a special character ($, !, @, #) </Text>
                      </View>
                    ) : (
                      <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                        <Ionicons name={"checkmark-outline"} size={24} color={colors.success} /> 
                        <Text style={styles.successText}>Contains a special character ($, !, @, #)</Text>
                      </View>
                    )}
                </View>
             )}
              <CustomTextInput
                label="Confirm Password"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                keyboardType="default"
                isPassword={true}
              />
              {errorText.length > 0 && (
                <Text style={styles.errorText}>{errorText}</Text>
              )}
              <BigButton
                text={isReset ? "Reset Password" : "Set Password"}
                onPress={() => handleSetPassword()}
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
  text: {
    color: colors.primary,
    fontSize: 14,
    marginVertical: 12,
  },
  boldText: {
    color: colors.secondary,
    fontSize: 14,
    fontWeight: "bold",
    marginVertical: 12,
  },
  errorText: {
    color: colors.error,
    fontSize: 14,
    fontWeight: "bold"
  },
  successText: {
    color: colors.success,
    fontSize: 14,
    fontWeight: "bold"
  }
});
