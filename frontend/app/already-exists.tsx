import { router } from "expo-router/build/global-state/router";
import { Fragment} from "react";
import {
  Platform,
  StyleSheet,
  StatusBar,
  Text,
  View,
} from "react-native";
import { colors } from "../constants/colors";
import { KeyboardAvoidingView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams } from 'expo-router';
import Ionicons from '@expo/vector-icons/Ionicons';
import BigButton from "../components/buttons/big-button";

export default function AlreadyExistsScreen() {
  const { email } = useLocalSearchParams();

  return (
    <Fragment>
        <StatusBar barStyle="light-content" backgroundColor={colors.secondary} />
        <SafeAreaView style={{ flex: 0, backgroundColor: colors.secondary }} />
        <View style={{ flex: 1, backgroundColor: colors.secondary }}>
          <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined}  style={{ flex: 1 }}>
          <View style={styles.sheet}>
            <Text style={styles.heading}>Account Already Exists</Text>

            <View style={{gap: 6}}>
              <Text style={styles.text}>An account already exists with the email: </Text>

              <View style={{flexDirection: 'row', alignItems: 'center', gap: '6'}}>
                <Ionicons name={"mail-outline"} size={24} color={colors.primary} /> 
                <Text style={styles.boldText}>{email}</Text>
              </View>

              <BigButton
                  text="Return to Sign in"
                  onPress={() => router.replace("/sign-in")}
               />
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
  }
});
