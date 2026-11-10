import { useState } from "react";
import { Tabs } from "expo-router";
import { ScrollView } from "react-native";
import UserViewSelector from "../../components/user-view-selector";
import UserCard from "../../components/user-card";
import { screenStyles as styles } from '../../constants/screen-styles';

export default function FindDriversScreen() {
  const [expanded, setExpanded] = useState(false);
  return (
    <>
      <Tabs.Screen options={{
        headerRight: () => <UserViewSelector expanded={expanded} onChange={setExpanded} />,
      }} />
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <UserCard expanded={expanded} />
        <UserCard expanded={expanded} />
      </ScrollView>
    </>
  );
}
