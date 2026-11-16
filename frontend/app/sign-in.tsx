import { router } from "expo-router/build/global-state/router";
import { Fragment, useState } from "react";
import {
  Alert,
  Platform,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors } from "../constants/colors";
import CustomTextInput from "../components/custom-text-input";
import BigButton from "../components/buttons/big-button";
import SmallButton from "../components/buttons/small-button";
import Divider from "../components/divider";
import { KeyboardAvoidingView } from "react-native";

const API_URL = process.env.EXPO_PUBLIC_API_URL;

export default function SignInScreen() {
  const [errorText, setErrorText] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignIn = async () => {
    const normalizedEmail=email.trim().toLowerCase();
    const parts = normalizedEmail.split('@');

    if (!normalizedEmail || !password) {
      setErrorText('Enter an email and password');
      return;
    }
    else if(parts.length!=2 || parts[1]!="psu.edu"){
      setErrorText("Please use your @psu.edu email")
      return;
    };

    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json',},
      body: JSON.stringify({ email: normalizedEmail, password: password }),
    });
    const result = await response.json();
    if (result['error']!=null){
      console.log(result['error']);
      setErrorText(result['error']);
    }
    else{
      router.replace({
          pathname: '/(app)/find-drivers'
        });
      }
  }
      
  function handleSignUp(){
    router.replace("/verify-email");
  }
  return (
    // Why there are two SafeAreaViews: https://stackoverflow.com/a/52458846
    <Fragment>
      <StatusBar barStyle="light-content" backgroundColor={colors.secondary} />
      <SafeAreaView style={{ flex: 0, backgroundColor: colors.secondary }} />
      <View style={{ flex: 1, backgroundColor: colors.secondary }}>
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined}  style={{ flex: 1 }}>
          <View style={styles.titleContainer}>
            <Text style={styles.title}>Lion Lift</Text>
            <Text style={styles.subtitle}>PENN STATE ABINGTON</Text>
          </View>

          <View style={styles.sheet}>
            <Text style={styles.heading}>Sign In</Text>

            <CustomTextInput
              label="Penn State Email"
              placeholder="abc123@psu.edu"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
            />

            <CustomTextInput
              label="Password"
              placeholder="Enter your password"
              value={password}
              onChangeText={setPassword}
              isPassword={true}
              onSubmitEditing={handleSignIn}
            />

            <View style={{ flexDirection: "row-reverse",  justifyContent: 'space-between'}}>
              <SmallButton
                text="Forgot password?"
                onPress={() =>
                  Alert.alert(
                    "Forgot password",
                    "Password recovery will be added later.",
                  )
                }
              ></SmallButton>
              {errorText.length > 0 && (
                <Text style={styles.errorText}>{errorText}</Text>
              )}
            </View>

            <BigButton text="Sign in" onPress={handleSignIn} />

            <Divider />

            <BigButton
              text="Create account"
              onPress={handleSignUp}
              borderOnly={true}
            />
          </View>
        </KeyboardAvoidingView>
      </View>
    </Fragment>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    backgroundColor: colors.background,
    margin: 0,
  },
  titleContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.secondary,
    paddingVertical: 24,
  },
  title: {
    color: colors.background,
    fontSize: 40,
    fontWeight: "bold",
    marginBottom: 8,
  },
  subtitle: {
    color: colors.accent,
    fontSize: 16,
    letterSpacing: 2,
  },
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
