
import { useState } from "react";
import { View, StyleSheet, Text } from "react-native";
import { colors } from "../../constants/colors";
import { shadowStyles } from "../../constants/shadow";
import BigButton from "../../components/buttons/big-button";
import Divider from "../../components/divider";
import LabeledText from "../../components/labeled-text";
import { SafeAreaView } from "react-native-safe-area-context";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { Carousel } from "react-native-reanimated-carousel";
import ComplexSchedule from "../../components/schedule/complex-schedule";

export default function ProfileScreen() {
  // Track the current carousel page
  const [activeIndex, setActiveIndex] = useState(0);

  // Profile carousel cards
  const cards = [
    // Card 1: About
    <View style={styles.card}>
      <View style={{ flex: 1 }}>
        <Text style={styles.heading}>About</Text>
        <Text style={styles.subheading}>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua.
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua.
        </Text>
      </View>

      <Divider />

      <View style={{ flex: 1 }}>
        <LabeledText label="Age" value="20" />
        <LabeledText label="Gender" value="Male" />
        <LabeledText label="Major" value="Computer Science" />
        <LabeledText label="Graduation Year" value="2028" />
        <LabeledText label="Preferred Payment" value="Venmo" />
      </View>
    </View>,

    // Card 2: Schedule
    <View style={styles.card}>
      <View style={styles.map}>
        <ComplexSchedule />
      </View>
    </View>,

    // Card 3: Map
    <View style={styles.card}>
      <Text style={styles.heading}>Map</Text>
      <View style={styles.map}></View>
    </View>,
  ];

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaView
        style={styles.screen}
        edges={["top", "left", "right"]}
      >
        {/* Profile Header */}
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            margin: 24,
          }}
        >
          <View style={styles.profilePicture} />
          <Text style={styles.heading}>Placeholder Name</Text>
        </View>

        {/* Carousel Stepper - TOP */}
        <View style={styles.stepperContainer}>
          {cards.map((_, index) => (
            <View
              key={index}
              style={[
                styles.stepperDot,
                index === activeIndex && styles.activeDot,
              ]}
            />
          ))}
        </View>

        {/* Carousel */}
        <Carousel
          data={cards}
          style={{ flex: 1 }}
          onSnapToItem={(index) => setActiveIndex(index)}
          renderItem={({ item }) => (
            <View style={{ flex: 1 }}>
              {item}
            </View>
          )}
        />

        {/* Contact Button */}
        <View style={{ marginHorizontal: 24, marginBottom: 16 }}>
          <BigButton text="Contact" onPress={() => {}} />
        </View>
      </SafeAreaView>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },

  profilePicture: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.border,
    marginRight: 16,
  },

  heading: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.primary,
  },

  subheading: {
    fontSize: 18,
    fontWeight: "500",
    color: colors.secondary,
  },

  card: {
    backgroundColor: colors.background,
    borderWidth: 0,
    borderColor: colors.secondary,
    padding: 16,
    margin: 24,
    borderRadius: 24,
    marginVertical: 16,
    marginBottom: 56 + 16,
    flex: 1,
    justifyContent: "space-between",
    ...shadowStyles,
  },

  map: {
    borderRadius: 8,
    flex: 1,
    marginTop: 16,
    backgroundColor: colors.border,
  },

  // Carousel Stepper Styles
  stepperContainer: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
    gap: 6,
  },

  stepperDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.background,
    borderWidth: 1.5,
    borderColor: colors.primary,
  },

  activeDot: {
    backgroundColor: colors.primary,
  },
});
