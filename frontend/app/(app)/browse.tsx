import { useState } from "react";
import { Tabs } from "expo-router";
import { ScrollView } from "react-native";
import UserViewSelector, { defaultBrowseOptions } from "../../components/user-view-selector";
import UserCard from "../../components/user-card";
import { screenStyles as styles } from '../../constants/screen-styles';

export default function BrowseScreen() {
  const [expanded, setExpanded] = useState(false);
  // Saved menu choices; API integration will use these to request users.
  const [options, setOptions] = useState(defaultBrowseOptions);
  return (
    <>
      <Tabs.Screen options={{
        headerRight: () => <UserViewSelector expanded={expanded} onChange={setExpanded}
          options={options} onApply={setOptions} />,
      }} />
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <UserCard expanded={expanded} />
        <UserCard expanded={expanded} />
      </ScrollView>
    </>
  );
}
