import { useState } from "react";
import { ScrollView } from "react-native";
import UserViewSelector from "../../components/user-view-selector";
import UserCard from "../../components/user-card";
import { screenStyles as styles } from '../../constants/screen-styles';

export default function FindDriversScreen() {
  const [expanded, setExpanded] = useState(false);
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <UserViewSelector expanded={expanded} onChange={setExpanded} />
      <UserCard expanded={expanded} />
      <UserCard expanded={expanded} />
    </ScrollView>
  );
}
