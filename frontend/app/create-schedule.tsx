import { router, useLocalSearchParams } from "expo-router";
import { useState, useEffect, Fragment } from "react";
import {KeyboardAvoidingView, Platform, ScrollView, StatusBar, StyleSheet, Text, View,} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import BigButton from "../components/buttons/big-button";
import { colors } from "../constants/colors";
import Stepper from "../components/stepper";
import BackButton from "../components/buttons/back-button";
import ComplexSchedule from "../components/schedule/complex-schedule";

export default function CreateScheduleScreen() {
  const params = useLocalSearchParams<{
    email: string;
    firstName: string;
    lastName: string;
    major: string;
    graduationYear: string;
    street: string;
    city: string;
    state: string;
    zipCode: string;
    schedule?: string;
    driver?: string;
    carMake?: string;
    carModel?: string;
    carYear?: string;
    carColor?: string;
  }>();

  const [schedule, setSchedule] = useState(params.schedule ?? "");

  useEffect(() => {
    if (params.schedule !== undefined) {
      setSchedule(params.schedule);
    }
  }, [params.schedule]);

  function handleNext() {
    router.navigate({
      pathname: "/create-car",
      params: {
        ...params,
        schedule: schedule
      },
    });
  }

  function goBack(){
    router.navigate({
      pathname: "/create-address",
      params: {
        ...params,
        schedule: schedule
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
                <View style={styles.fields}>
                  <BackButton
                    onPress={goBack}
                  />
                  <Stepper
                    step={6}
                    steps={7}
                  />
                  <Text style={styles.heading}>Enter Schedule</Text>

                  <View style={styles.map}>
                    <ComplexSchedule/>
                  </View>

                </View>
                <BigButton text="Next" onPress={handleNext} />
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
  },
  map: {
    flex: 1,
    marginTop: 16,
  },
});