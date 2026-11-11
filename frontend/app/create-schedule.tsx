import { router, useLocalSearchParams } from "expo-router";
import { useState } from "react";
import {Alert, KeyboardAvoidingView, Platform, Pressable, ScrollView, StatusBar, StyleSheet, Text, View,} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import BigButton from "../components/buttons/big-button";
import ScheduleFields, {type DaySchedule,type ScheduleTime,} from "../components/schedule/schedule-fields";
import { colors } from "../constants/colors";

export default function CreateScheduleScreen() {
  const params = useLocalSearchParams<{
    firstName: string;
    lastName: string;
    major: string;
    graduationYear: string;
    bio: string;
    street: string;
    city: string;
    state: string;
    zipCode: string;
  }>();

  const [schedule, setSchedule] = useState<DaySchedule[]>([]);
  const [plansToDrive, setPlansToDrive] = useState<boolean | null>(null);

  function timeToMinutes(time: ScheduleTime): number | null {
    const hour = Number(time.hour);
    const minute = Number(time.minute);

    if (
      !/^\d{1,2}$/.test(time.hour) ||
      !/^\d{1,2}$/.test(time.minute) ||
      hour < 1 ||
      hour > 12 ||
      minute < 0 ||
      minute > 59
    ) {
      return null;
    }

    return ((hour % 12) + (time.period === "PM" ? 12 : 0)) * 60 + minute;
  }

  function formatTime(time: ScheduleTime): string {
    return `${time.hour}:${time.minute.padStart(2, "0")} ${time.period}`;
  }

  function handleNext() {
    if (schedule.length === 0) {
      Alert.alert("Schedule", "Choose at least one commute day.");
      return;
    }

    for (const day of schedule) {
      const departure = timeToMinutes(day.departureTime);
      const returning = timeToMinutes(day.returnTime);

      if (departure === null || returning === null) {
        Alert.alert(
          "Schedule times",
          `Enter a valid departure and return time for ${day.day}.`
        );
        return;
      }

      if (returning <= departure) {
        Alert.alert(
          "Schedule times",
          `${day.day}: return time must be later than departure time.`
        );
        return;
      }
    }

    if (plansToDrive === null) {
      Alert.alert("Ride preferences", "Please choose Yes or No.");
      return;
    }

    const scheduleForRoute = schedule.map((day) => ({
      day: day.day,
      departureTime: formatTime(day.departureTime),
      returnTime: formatTime(day.returnTime),
    }));

    const setupParams = {
      firstName: params.firstName,
      lastName: params.lastName,
      major: params.major,
      graduationYear: params.graduationYear,
      bio: params.bio,
      street: params.street,
      city: params.city,
      state: params.state,
      zipCode: params.zipCode,
      schedule: JSON.stringify(scheduleForRoute),
      plansToDrive: String(plansToDrive),
    };

    if (plansToDrive) {
      router.push({ pathname: "/create-car", params: setupParams });
    } else {
      router.replace({ pathname: "/(app)/find-drivers", params: setupParams });
    }
  }

  return (
    <>
      <StatusBar barStyle="light-content" />
      <SafeAreaView style={styles.topSafeArea} />

      <View style={styles.container}>
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          style={styles.keyboardContainer}
        >
          <View style={styles.sheet}>
            <ScrollView
              contentContainerStyle={styles.content}
              keyboardShouldPersistTaps="handled"
            >
              <Text style={styles.heading}>Set your schedule</Text>

              <ScheduleFields schedule={schedule} onChange={setSchedule} />

              <Text style={styles.question}>Do you plan to offer rides?</Text>

              <View style={styles.answerRow}>
                {[true, false].map((answer) => {
                  const selected = plansToDrive === answer;
                  const label = answer ? "Yes" : "No";

                  return (
                    <Pressable
                      key={label}
                      onPress={() => setPlansToDrive(answer)}
                      accessibilityRole="radio"
                      accessibilityState={{ selected }}
                      style={[
                        styles.answerButton,
                        selected && styles.answerButtonSelected,
                      ]}
                    >
                      <Text style={styles.answerText}>{label}</Text>
                    </Pressable>
                  );
                })}
              </View>

              <View style={styles.nextButton}>
                <BigButton text="Next" onPress={handleNext} />
              </View>
            </ScrollView>
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
  },
  content: {
    paddingHorizontal: 20,
    paddingBottom: 32,
  },
  heading: {
    color: colors.primary,
    fontSize: 28,
    fontWeight: "bold",
    marginTop: 18,
  },
  question: {
    color: colors.secondary,
    fontSize: 13,
    fontWeight: "bold",
    marginTop: 12,
    marginBottom: 6,
  },
  answerRow: {
    flexDirection: "row",
    gap: 10,
  },
  answerButton: {
    flex: 1,
    alignItems: "center",
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
  },
  answerButtonSelected: {
    backgroundColor: colors.accent,
    borderColor: colors.secondary,
  },
  answerText: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: "600",
  },
  nextButton: {
    marginTop: 10,
  },
});