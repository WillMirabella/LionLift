import { router } from "expo-router/build/global-state/router";
import { Fragment, useState, useEffect } from "react";
import {
  Platform,
  StyleSheet,
  StatusBar,
  Text,
  View,
} from "react-native";
import { colors } from "../constants/colors";
import { KeyboardAvoidingView } from "react-native";
import SmallButton from "../components/buttons/small-button";
import { SafeAreaView } from "react-native-safe-area-context";
import { OtpInput } from "react-native-otp-entry";
import { useLocalSearchParams } from 'expo-router';
import Ionicons from '@expo/vector-icons/Ionicons';

const API_URL = process.env.EXPO_PUBLIC_API_URL;

export default function VerifyCodeScreen() {
  const { email } = useLocalSearchParams();
  const [cooldown, setCooldown] = useState(60);
  const [errorText, setErrorText] = useState("");

  // Trys to request another verification code
  const handleResendCode = async () => {
    // Check if cooldown is over
    if (cooldown > 0) return;

    // Set cooldown back to 60 seconds
    setCooldown(60);

    try {
      const response = await fetch(`${API_URL}/api/auth/request-code`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json',},
        body: JSON.stringify({ email: email }),
      });

      const result = await response.json();
      if (result['error']!=null) console.log(result['error']);

    } catch (error) {
      console.error('Error submitting data:', error);
    }
  }

  // Trys to verify a verification code
  const handleVerifyCode = async (code: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/verify`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json',},
        body: JSON.stringify({ email: email, code: code }),
      });

      const result = await response.json();
      if (result['error']!=null){
        console.log(result['error']);
        setErrorText(result['error']);
      }
      else router.replace("/(app)/find-drivers");
    } catch (error) {
      console.error('Error submitting data:', error);
    }
  }

  // Decrement cooldown
  useEffect(() => {
    if (cooldown === 0) return;

    const timer = setInterval(() => {
      setCooldown((prev) => Math.max(0, prev - 1));
    }, 1000);

    return () => clearInterval(timer);
  }, [cooldown]);

  return (
    <Fragment>
        <StatusBar barStyle="light-content" backgroundColor={colors.secondary} />
        <SafeAreaView style={{ flex: 0, backgroundColor: colors.secondary }} />
        <View style={{ flex: 1, backgroundColor: colors.secondary }}>
          <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined}  style={{ flex: 1 }}>
          <View style={styles.sheet}>
            <Text style={styles.heading}>Enter Code</Text>

            <View style={{gap: 6}}>
              <Text style={styles.text}>Enter the 6-Digit verfication code sent to: </Text>

              <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                <Ionicons name={"mail-outline"} size={24} color={colors.primary} /> 
                <Text style={styles.boldText}>{email}</Text>
              </View>
            </View>

            <View style={{ marginTop: 24 }}>
              <OtpInput 
                type="numeric"
                numberOfDigits={6}  
                focusColor={colors.secondary}
                theme={{
                  pinCodeContainerStyle: styles.pinCodeContainer,
                }}
                onFilled={(text) => {
                  handleVerifyCode(text);
                }}
              />
            </View>
            
            <View style={{ flexDirection: "row-reverse",  justifyContent: 'space-between' }}>
              <SmallButton
                text={cooldown > 0 ? `Resend Code (${cooldown}s)` : 'Resend Code'}
                disabled={cooldown > 0}
                onPress={() => handleResendCode()}
              ></SmallButton>
              {errorText.length > 0 && (
                <Text style={styles.errorText}>{errorText}</Text>
              )}
            </View>
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
    fontSize: 18,
  },
  boldText: {
    color: colors.primary,
    fontSize: 18,
    fontWeight: "bold",
  },
  pinCodeContainer: {
    borderWidth: 2,
    borderColor: colors.border,
    borderRadius: 16,
    marginVertical: 12,
    backgroundColor: colors.background,
  },
  errorText: {
    color: colors.error,
    fontSize: 14,
    fontWeight: "bold",
    marginVertical: 12,
  }
});
