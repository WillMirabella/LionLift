import { View, StyleSheet, Text } from "react-native";
import { colors } from "../../constants/colors";
import { shadowStyles } from "../../constants/shadow";
import BigButton from "../../components/buttons/big-button";
import Divider from "../../components/divider";
import LabeledText from "../../components/labeled-text";
import {
  SafeAreaView,
} from 'react-native-safe-area-context';

export default function ProfileScreen() {
  return (
    <SafeAreaView style={styles.screen} edges={['top', 'left', 'right']}>
      <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 16 }}>
        <View style={styles.profilePicture} />
        <Text style={styles.heading}>Placeholder Name</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.heading}>About</Text>
        <Text style={styles.subheading}>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua.
        </Text>
        <Divider />
        <LabeledText label="Age" value="20" />
        <LabeledText label="Gender" value="Male" />
        <LabeledText label="Major" value="Computer Science" />
        <LabeledText label="Graduation Year" value="2028" />
        <LabeledText label="Preferred Payment" value="Venmo" />
      </View>
      <BigButton text="Contact" onPress={() => {}} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 16,
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
    borderRadius: 24,
    marginVertical: 16,
    flex: 1,
    justifyContent: "space-between",
    ...shadowStyles,
  },
});
