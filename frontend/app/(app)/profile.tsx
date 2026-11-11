import { View, StyleSheet, Text } from "react-native";
import { colors } from "../../constants/colors";
import { shadowStyles } from "../../constants/shadow";
import BigButton from "../../components/buttons/big-button";
import Divider from "../../components/divider";
import LabeledText from "../../components/labeled-text";
import {
  SafeAreaView,
} from 'react-native-safe-area-context';
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { Carousel } from "react-native-reanimated-carousel";

export default function ProfileScreen() {

  const cards = [
    <View style={styles.card}>
      <View style={{ flex: 1 }}>
        <Text style={styles.heading}>About</Text>
        <Text style={styles.subheading}>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
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

    <View style={styles.card}>
      <Text style={styles.heading}>Schedule</Text>
      <View style={styles.map}>
      </View>
    </View>,

    <View style={styles.card}>
      <Text style={styles.heading}>Map</Text>
      <View style={styles.map}>
      </View>
    </View>
  ];

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaView style={styles.screen} edges={['top', 'left', 'right']}>
        <View style={{ flexDirection: "row", alignItems: "center", margin: 24 }}>
          <View style={styles.profilePicture} />
          <Text style={styles.heading}>Placeholder Name</Text>
        </View>
        <Carousel
          data={cards}
          style={{ flex: 1 }}
          renderItem={({ item }) => (
              <View style={{ flex: 1 }}>
                {item}
              </View>
          )}
        />
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
});
