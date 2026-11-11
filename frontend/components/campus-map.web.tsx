import Ionicons from '@expo/vector-icons/Ionicons';
import type { ReactNode } from 'react';
import { ScrollView, Text, View } from 'react-native';
import { colors } from '../constants/colors';
import { screenStyles as styles } from '../constants/screen-styles';

type Props = {
  initialRegion?: unknown;
  children?: ReactNode;
};

// react-native-maps has no web version, so the web build shows a message instead.
// Metro picks this file over campus-map.tsx when building for web.
export default function CampusMap(_props: Props) {
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <View style={styles.card}>
        <View accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
          <Ionicons name="map-outline" size={48} color={colors.primary} />
        </View>
        <Text style={styles.cardTitle}>Map not available on web</Text>
        <Text style={styles.description}>
          The map works in the iOS and Android app. Open LionLift on your phone to see drivers near you.
        </Text>
      </View>
    </ScrollView>
  );
}
