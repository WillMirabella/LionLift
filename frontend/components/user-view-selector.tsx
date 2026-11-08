import Ionicons from '@expo/vector-icons/Ionicons';
import { Pressable, StyleSheet, View } from 'react-native';
import { colors } from '../constants/colors';

type Props = {
  expanded: boolean;
  onChange: (expanded: boolean) => void;
};

// The screen shares this selected view with every user card.
export default function UserViewSelector({ expanded, onChange }: Props) {
  return (
    <View style={styles.buttons}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Compact cards"
        accessibilityState={{ selected: !expanded }}
        onPress={() => onChange(false)}
        style={[styles.button, !expanded && styles.selectedButton]}
      >
        <Ionicons name="list-outline" size={22} color={colors.primary} />
      </Pressable>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Expanded cards"
        accessibilityState={{ selected: expanded }}
        onPress={() => onChange(true)}
        style={[styles.button, expanded && styles.selectedButton]}
      >
        <Ionicons name="reader-outline" size={22} color={colors.primary} />
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  buttons: {
    flexDirection: 'row',
    alignSelf: 'flex-end',
    gap: 2,
    padding: 3,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
  },
  button: {
    width: 44,
    height: 44,
    borderRadius: 5,
    alignItems: 'center',
    justifyContent: 'center',
  },
  selectedButton: { backgroundColor: `${colors.accent}33` },
});
