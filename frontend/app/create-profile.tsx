import { useState } from "react";
import {Alert, KeyboardAvoidingView, Modal, Platform, Pressable, ScrollView, StatusBar, StyleSheet, Text, View,} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import BigButton from "../components/buttons/big-button";
import SmallButton from "../components/buttons/small-button";
import CustomTextInput from "../components/custom-text-input";
import DriverDetailsSection, {type CarDetails,} from "../components/driver-details-section";
import { colors } from "../constants/colors";

const majors = [
  "Accounting",
  "American Studies",
  "Art",
  "Biology",
  "Business",
  "Computer Science",
  "Corporate Communication",
  "Criminal Justice",
  "Cybersecurity Analytics and Operations",
  "Data Sciences",
  "Elementary and Early Childhood Education",
  "Engineering",
  "English",
  "Finance",
  "Health Humanities",
  "History",
  "Information Technology",
  "Integrative Arts",
  "Integrative Science",
  "Multidisciplinary Studies",
  "Project and Supply Chain Management",
  "Psychological and Social Sciences",
  "Race and Ethnic Studies",
  "Recreation, Park and Tourism Management",
  "Rehabilitation and Human Services",
  "Undecided",
  "Other / 2+2 program",
];

export default function CreateProfileScreen() {
  const [plansToDrive, setPlansToDrive] = useState<boolean | null>(null);

  const [profile, setProfile] = useState({
    firstName: "",
    lastName: "",
    gradYear: "",
    gender: "",
    major: "",
    description: "",
    address: "",
    phone: "",
  });

  const [car, setCar] = useState<CarDetails>({
    make: "",
    model: "",
    year: "",
    color: "",
    plate: "",
    seats: "",
  });

  const [majorPickerOpen, setMajorPickerOpen] = useState(false);
  const [payments, setPayments] = useState<string[]>([]);
  const [documentsConfirmed, setDocumentsConfirmed] = useState(false);

  function updateProfile(field: keyof typeof profile, value: string) {
    setProfile(current => ({ ...current, [field]: value }));
  }

  function updateCar(field: keyof CarDetails, value: string) {
    setCar(current => ({ ...current, [field]: value }));
  }

  function togglePayment(method: string) {
    setPayments(current =>
      current.includes(method)
        ? current.filter(item => item !== method)
        : [...current, method]
    );
  }

  function handleContinue() {
    const requiredFields = [
      profile.firstName,
      profile.lastName,
      profile.gradYear,
      profile.gender,
      profile.major,
      profile.description,
    ];

    if (requiredFields.some(value => !value.trim())) {
      Alert.alert("Missing details", "Please complete all fields that aren't marked optional.");
      return;
    }

    if (!/^\d{4}$/.test(profile.gradYear.trim())) {
      Alert.alert("Graduation year", "Enter a four-digit year, such as 2027.");
      return;
    }

    if (plansToDrive === null) {
      Alert.alert("Ride preferences", "Please choose Yes or No.");
      return;
    }

    if (plansToDrive) {
      if (Object.values(car).some(value => !value.trim())) {
        Alert.alert("Car details", "Please complete your car information.");
        return;
      }

      const modelYear = Number(car.year);

      if (
        !/^\d{4}$/.test(car.year.trim()) ||
        modelYear < 1998 ||
        modelYear > new Date().getFullYear() + 1
      ) {
        Alert.alert("Model year", "Please enter a valid car model year.");
        return;
      }

      if (!/^[1-8]$/.test(car.seats.trim())) {
        Alert.alert("Passenger seats", "Enter 1–8 available seats, excluding the driver.");
        return;
      }

      if (payments.length === 0) {
        Alert.alert("Payment methods", "Choose at least one preferred payment method.");
        return;
      }

      if (!documentsConfirmed) {
        Alert.alert("Driver confirmation", "Please confirm your registration, insurance, and license are up to date.");
        return;
      }
    }

    Alert.alert("Schedule will be added next!");
  }

  return (
    <>
      <StatusBar
        barStyle="light-content"
        backgroundColor={colors.secondary}
      />
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
              <Text style={styles.heading}>Create your profile</Text>

              <CustomTextInput
                label="First name"
                placeholder="First name"
                value={profile.firstName}
                onChangeText={value => updateProfile("firstName", value)}
              />

              <CustomTextInput
                label="Last name"
                placeholder="Last name"
                value={profile.lastName}
                onChangeText={value => updateProfile("lastName", value)}
              />

              <CustomTextInput
                label="Graduation year"
                placeholder="2027"
                value={profile.gradYear}
                onChangeText={value => updateProfile("gradYear", value)}
                keyboardType="numeric"
              />

              <CustomTextInput
                label="Gender"
                placeholder="Your gender, or prefer not to say"
                value={profile.gender}
                onChangeText={value => updateProfile("gender", value)}
              />

              <Text style={styles.label}>Major</Text>

              <Pressable
                style={styles.dropdown}
                onPress={() => setMajorPickerOpen(true)}
                accessibilityRole="button"
                accessibilityLabel="Choose your major"
              >
                <Text style={styles.optionText}>
                  {profile.major || "Select your major"}
                </Text>
                <Text style={styles.optionText}>⌄</Text>
              </Pressable>

              <CustomTextInput
                label="About you"
                placeholder="Tell us a little about yourself"
                value={profile.description}
                onChangeText={value => updateProfile("description", value)}
              />

              <CustomTextInput
                label="Address (optional)"
                placeholder="Street address"
                value={profile.address}
                onChangeText={value => updateProfile("address", value)}
              />

              <CustomTextInput
                label="Phone number (optional)"
                placeholder="Phone number"
                value={profile.phone}
                onChangeText={value => updateProfile("phone", value)}
                keyboardType="phone-pad"
              />

              <Text style={styles.label}>Do you plan to offer rides?</Text>

              <View style={styles.rideOptions}>
                <View style={styles.rideOption}>
                  <BigButton
                    text="Yes"
                    borderOnly={plansToDrive !== true}
                    onPress={() => setPlansToDrive(true)}
                  />
                </View>

                <View style={styles.rideOption}>
                  <BigButton
                    text="No"
                    borderOnly={plansToDrive !== false}
                    onPress={() => setPlansToDrive(false)}
                  />
                </View>
              </View>

              {plansToDrive === true && (
                <DriverDetailsSection
                  car={car}
                  onCarChange={updateCar}
                  payments={payments}
                  onTogglePayment={togglePayment}
                  documentsConfirmed={documentsConfirmed}
                  onDocumentsConfirmedChange={setDocumentsConfirmed}
                />
              )}

              <View style={styles.continueButton}>
                <BigButton text="Next" onPress={handleContinue} />
              </View>
            </ScrollView>
          </View>
        </KeyboardAvoidingView>

        <Modal
          visible={majorPickerOpen}
          transparent
          animationType="fade"
          onRequestClose={() => setMajorPickerOpen(false)}
        >
          <View style={styles.overlay}>
            <View style={styles.majorModal}>
              <Text style={styles.sectionHeading}>Choose your major</Text>

              <ScrollView>
                {majors.map(major => (
                  <Pressable
                    key={major}
                    style={styles.majorOption}
                    accessibilityRole="button"
                    onPress={() => {
                      updateProfile("major", major);
                      setMajorPickerOpen(false);
                    }}
                  >
                    <Text style={styles.optionText}>{major}</Text>
                  </Pressable>
                ))}
              </ScrollView>

              <SmallButton
                text="Cancel"
                onPress={() => setMajorPickerOpen(false)}
              />
            </View>
          </View>
        </Modal>
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
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  heading: {
    color: colors.primary,
    fontSize: 32,
    fontWeight: "bold",
    marginVertical: 24,
  },
  sectionHeading: {
    color: colors.primary,
    fontSize: 23,
    fontWeight: "bold",
    marginTop: 24,
    marginBottom: 16,
  },
  label: {
    color: colors.primary,
    fontSize: 16,
    fontWeight: "600",
    marginTop: 12,
    marginBottom: 8,
  },
  dropdown: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  optionText: {
    color: colors.primary,
    fontSize: 16,
    flexShrink: 1,
  },
  rideOptions: {
    flexDirection: "row",
    gap: 12,
  },
  rideOption: {
    flex: 1,
  },
  continueButton: {
    marginTop: 32,
  },
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.45)",
    justifyContent: "center",
    padding: 24,
  },
  majorModal: {
    backgroundColor: colors.background,
    borderRadius: 20,
    padding: 20,
    maxHeight: "80%",
  },
  majorOption: {
    paddingVertical: 16,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.primary,
  },
});