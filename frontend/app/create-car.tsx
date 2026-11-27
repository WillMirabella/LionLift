import { router, useLocalSearchParams } from "expo-router";
import { useState, useRef, useEffect } from "react";
import {KeyboardAvoidingView,Platform, TextInputInstance, StatusBar, StyleSheet,Text, View, } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import BigButton from "../components/buttons/big-button";
import { colors } from "../constants/colors";
import Stepper from "../components/stepper";
import CustomTextInput from "../components/custom-text-input";
import BackButton from "../components/buttons/back-button";

const API_URL = process.env.EXPO_PUBLIC_API_URL;

export default function CreateCarScreen() {
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
    schedule: string;
    driver?: string;
    carMake?: string;
    carModel?: string;
    carYear?: string;
    carColor?: string;
  }>();
  
  const [car, setCar] = useState({
    make: params.carMake ?? "",
    model: params.carModel ?? "",
    year: params.carYear ?? "",
    color: params.carColor ?? "",
  });

  const [driver, setDriver] = useState(params.driver === "true");
  const [confirmed, setConfirm] = useState(false);

  const inputs = useRef<Array<TextInputInstance | null>>([]);
  const [errorText, setErrorText] = useState("");

  useEffect(() => {
    setCar({
      make: params.carMake ?? "",
      model: params.carModel ?? "",
      year: params.carYear ?? "",
      color: params.carColor ?? "",
    });
    if (params.driver !== undefined) {
      setDriver(params.driver === "true");
    }
  }, [params.carMake, params.carModel, params.carYear, params.carColor, params.driver]);


  function updateCar(field: keyof typeof car, value: string) {
    setCar((current) => ({ ...current, [field]: value }));
  }
 
  function handleConfirm() {
    setConfirm(previousState => !previousState);
  }

  function handleYes(){
    setDriver(true);
  }
  function handleNo(){
    setDriver(false);
  }

  const handleFinish = async () => {
    if(driver){
      if (
        !car.make.trim() ||
        !car.model.trim() ||
        !car.year.trim() ||
        !car.color.trim()
      ) {
        setErrorText("Enter all information to continue");
        return;
      }

      const modelYear = Number(car.year.trim());

      if (
        !/^\d{4}$/.test(car.year.trim()) ||
        modelYear < 1998 ||
        modelYear > new Date().getFullYear() + 1
      ) {
        setErrorText("Enter a valid four-digit model year");
        return;
      }

      if (!confirmed) {
        setErrorText("Confirm above to continue");
        return;
      }
    }

    const response = await fetch(`${API_URL}/api/users/update-user`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json',},
      body: JSON.stringify({ email: params.email, first_name:params.firstName, last_name:params.lastName, major:params.major, graduation_year:params.graduationYear,
                              street:params.street, city:params.city, state:params.state, zip_code:params.zipCode, schedule:params.schedule, 
                              driver:params.driver, car_make:params.carMake, car_model:params.carModel, car_year:params.carYear, car_color:params.carColor,
      }),
    });
    const result = await response.json();

    if (result['error']!=null){
      console.log(result['error']);
      setErrorText(result['error']);
    }
    else{
      router.navigate({
        pathname: "/welcome",
        params: {
          ...params,
          driver: String(driver),
          carMake: car.make.trim(),
          carModel: car.model.trim(),
          carYear: car.year.trim(),
          carColor: car.color.trim(),
        },
      });
    }
  }
  function goBack(){
    router.navigate({
      pathname: '/create-schedule',
      params: {
        ...params,
        driver: String(driver),
        carMake: car.make.trim(),
        carModel: car.model.trim(),
        carYear: car.year.trim(),
        carColor: car.color.trim(),
      },
    });
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
            <BackButton
              onPress={goBack}
            />
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
              {errorText.length > 0 && (
                <Text style={styles.errorText}>{errorText}</Text>
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
  errorText: {
    color: colors.error,
    fontSize: 14,
    fontWeight: "bold"
  },
});