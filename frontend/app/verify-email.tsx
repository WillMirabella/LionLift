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

export default function VerifyEmailScreen() {
  const [email, setEmail] = useState("");
  const [errorText, setErrorText] = useState("");

  const handleSendCode = async () => {
    // Check email format on the frontend in the interest of redundancy
    const normalizedEmail=email.trim().toLowerCase();
    const parts = normalizedEmail.split('@');
    if(normalizedEmail==""){
      setErrorText("Email is required")
      return;
    }
    else if(parts.length!=2 || parts[1]!="psu.edu"){
      setErrorText("Please use your @psu.edu email")
      return;
    };

    // Try to request a verification code
    try {
      const response = await fetch(`${API_URL}/api/auth/request-code`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json',},
        body: JSON.stringify({ email: email }),
      });

      const result = await response.json();
      if (result['error']!=null){
        setErrorText(result['error']);
        console.log(result['error']);
      }
      else{
        if(result['status']=="already_verified"){
          setErrorText("An account already exists with this email");
          console.log(result['status']);
        }else{
          router.replace({
            pathname: '/verify-code',
            params: { email: email },
          });
        }
      }
    } catch (error) {
      console.error('Error submitting data:', error);
    }
  }

  function goBack(){
    router.replace({
            pathname: '/sign-in',
            params: { email: email },
          });
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
            <Stepper
              step={1}
              steps={7}
            />
            <Text style={styles.heading}>Verify Email</Text>
            <CustomTextInput
              label="Penn State Email"
              placeholder="abc123@psu.edu"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
            />
            {errorText.length > 0 && (
               <Text style={styles.errorText}>{errorText}</Text>
            )}

            <BigButton
              text="Send Verification Email"
              onPress={() => handleSendCode()}
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
  errorText: {
    color: colors.error,
    fontSize: 14,
    fontWeight: "bold",
    marginVertical: 12,
  }
});
