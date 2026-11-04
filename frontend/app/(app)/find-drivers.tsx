import { ScrollView, View } from "react-native";
import PlaceholderScreen from "../../components/placeholder-screen";
import UserCard from "../../components/user-card";
import { screenStyles as styles } from '../../constants/screen-styles';

export default function FindDriversScreen() {
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <UserCard/>
      <UserCard expanded />
    </ScrollView>
  );
}
