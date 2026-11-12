import { router, useLocalSearchParams } from "expo-router";
import { useState, useRef } from "react";
import {Alert,KeyboardAvoidingView,Pressable,Platform, TextInputInstance, StatusBar, StyleSheet,Text, View, } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import BigButton from "../components/buttons/big-button";
import { colors } from "../constants/colors";
import Stepper from "../components/stepper";
import CustomTextInput from "../components/custom-text-input";

export default function CreateCarScreen() {
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
    schedule: string;
  }>();

  const [car, setCar] = useState({
    make: "",
    model: "",
    year: "",
    color: "",
  }); 
  
  const inputs = useRef<Array<TextInputInstance | null>>([]);

  const [driver, setDriver] = useState(false);
  const [confirmed, setConfirm] = useState(false);

  function updateCar(field: keyof typeof car, value: string) {
    setCar((current) => ({ ...current, [field]: value }));
  }
 
  function handleConfirm() {
    setConfirm(previousState => !previousState);
  }

  function handleFinish() {
    if(driver){
      if (
        !car.make.trim() ||
        !car.model.trim() ||
        !car.year.trim() ||
        !car.color.trim()
      ) {
        Alert.alert("Missing details", "Please complete all car fields.");
        return;
      }

      const modelYear = Number(car.year.trim());

      if (
        !/^\d{4}$/.test(car.year.trim()) ||
        modelYear < 1998 ||
        modelYear > new Date().getFullYear() + 1
      ) {
        Alert.alert("Model year", "Enter a valid four-digit model year.");
        return;
      }

      if (!confirmed) {
        Alert.alert(
          "Driver confirmation",
          "Please confirm your license, insurance, and registration are up to date."
        );
        return;
      }
    }

    router.replace({
      pathname: "/welcome",
      params: {
        ...params,
        carMake: car.make.trim(),
        carModel: car.model.trim(),
        carYear: car.year.trim(),
        carColor: car.color.trim(),
        documentsConfirmed: "true",
      },
    });
  }
  function handleYes(){
    setDriver(true);
  }
  function handleNo(){
    setDriver(false);
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
            <Stepper
                step={7}
                steps={7}
            />
            <Text style={styles.heading}>Enter Car Information</Text>
             <Text style={styles.label}>Do you want to offer rides?</Text>

              <View style={{ flexDirection: "row", gap: 12  }}>
                <View style={{ flex: 1 }}>
                  {driver ? (
                    <BigButton text="Yes" onPress={handleYes} borderOnly={false}/>
                  ):
                  (
                    <BigButton text="Yes" onPress={handleYes} borderOnly={true}/>
                  )}
                </View>
                <View style={{ flex: 1 }}>
                  {driver ? (
                    <BigButton text="No" onPress={handleNo} borderOnly={true}/>
                  ):
                  (
                    <BigButton text="No" onPress={handleNo} borderOnly={false}/>
                  )}
                </View>
              </View>
              
              {driver && (
                <View>
                  <View style={{ flexDirection: "row", gap: 12  }}>
                    <View style={{ flex: 1 }}>
                      <CustomTextInput
                        ref={(el) => { inputs.current[0] = el; }}
                        label="Make"
                        placeholder="Toyota"
                        value={car.make}
                        onChangeText={(value) => updateCar("make", value)}
                        returnKeyType="next"
                        onSubmitEditing={() => inputs.current[1]?.focus()}
                      />
                    </View>
                    <View style={{ flex: 1 }}>
                      <CustomTextInput
                        ref={(el) => { inputs.current[1] = el; }}
                        label="Model"
                        placeholder="Corolla"
                        value={car.model}
                        onChangeText={(value) => updateCar("model", value)}
                        returnKeyType="next"
                        onSubmitEditing={() => inputs.current[2]?.focus()}
                      />
                    </View>
                  </View>
                  <View style={{ flexDirection: "row", gap: 12  }}>
                    <View style={{ flex: 1 }}>
                      <CustomTextInput
                        ref={(el) => { inputs.current[2] = el; }}
                        label="Year"
                        placeholder="2020"
                        value={car.year}
                        onChangeText={(value) => updateCar("year", value)}
                        keyboardType="numeric"
                        returnKeyType="next"
                        onSubmitEditing={() => inputs.current[3]?.focus()}
                      />
                    </View>
                    <View style={{ flex: 1 }}>
                      <CustomTextInput
                        ref={(el) => { inputs.current[3] = el; }}
                        label="Color"
                        placeholder="Blue"
                        value={car.color}
                        onChangeText={(value) => updateCar("color", value)}
                        returnKeyType="done"
                      />
                    </View>
                  </View>
                    <View style={{ flexDirection: "row", gap: 12  }}>
                      <View style={{aspectRatio: "1/1", marginVertical:12, top:-12}}>
                        {confirmed ? (
                          <BigButton text="" onPress={handleConfirm} borderOnly={false}/>
                        ):
                        (
                          <BigButton text="" onPress={handleConfirm} borderOnly={true}/>
                        )}
                      </View>
                      <View style={{flex: 1}}>
                        <Text style={styles.text}>
                          I confirm my driver’s license, car insurance, and registration are
                          up to date.
                        </Text>
                      </View>
                    </View>

                </View>
              )}
              <BigButton text="Next" onPress={handleFinish} />
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
  heading: {
    color: colors.primary,
    fontSize: 32,
    fontWeight: "bold",
    marginTop: 24,
  },
  label: {
    color: colors.secondary,
    fontSize: 14,
    fontWeight: "bold",
    marginTop: 12,
  },
  text: {
    color: colors.primary,
    fontSize: 14,
    marginVertical: 12,
  },
  checkbox: {
    width: 26,
    height: 26,
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: 5,
    alignItems: "center",
    justifyContent: "center",
  },
  checkmark: {
    color: colors.primary,
    fontSize: 18,
    fontWeight: "bold",
  },
});