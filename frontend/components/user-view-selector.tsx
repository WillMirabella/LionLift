import Ionicons from '@expo/vector-icons/Ionicons';
import { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { colors } from '../constants/colors';
import { shadowStyles } from '../constants/shadow';

type Props = {
  expanded: boolean;
  onChange: (expanded: boolean) => void;
};

// The screen shares the selected view with every user card.
export default function UserViewSelector({ expanded, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const insets = useSafeAreaInsets();

  function selectView(value: boolean) {
    onChange(value);
    setOpen(false);
  }

  return (
    <>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Display options"
        accessibilityState={{ expanded: open }}
        onPress={() => setOpen(true)}
        style={styles.headerButton}
      >
        <Ionicons name="options-outline" size={24} color={colors.primary} />
      </Pressable>
      <Modal transparent visible={open} animationType="fade" onRequestClose={() => setOpen(false)}>
        <View style={styles.overlay}>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Dismiss display options"
            onPress={() => setOpen(false)}
            style={StyleSheet.absoluteFill}
          />
          <View
            accessibilityViewIsModal
            style={[styles.menu, { marginTop: insets.top + 56, marginRight: insets.right + 12 }]}
          >
            {/* Sorting and filtering can be added as sections in this menu. */}
            <Text accessibilityRole="header" style={styles.sectionTitle}>View</Text>
            <Pressable accessibilityRole="button" accessibilityLabel="Compact cards"
              accessibilityState={{ selected: !expanded }} onPress={() => selectView(false)}
              style={[styles.option, !expanded && styles.selectedOption]}>
              <Ionicons name="reorder-two-outline" size={22} color={colors.primary} />
              <Text style={styles.label}>Compact</Text>
              {!expanded && <Ionicons name="checkmark" size={20} color={colors.primary} />}
            </Pressable>
            <Pressable accessibilityRole="button" accessibilityLabel="Expanded cards"
              accessibilityState={{ selected: expanded }} onPress={() => selectView(true)}
              style={[styles.option, expanded && styles.selectedOption]}>
              <Ionicons name="reorder-four-outline" size={22} color={colors.primary} />
              <Text style={styles.label}>Expanded</Text>
              {expanded && <Ionicons name="checkmark" size={20} color={colors.primary} />}
            </Pressable>
          </View>
        </View>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  headerButton: { width: 44, height: 44, marginRight: 16, alignItems: 'center', justifyContent: 'center' },
  overlay: { flex: 1, backgroundColor: '#00000033', alignItems: 'flex-end' },
  menu: { width: 260, maxWidth: '90%', padding: 12, borderRadius: 12, backgroundColor: colors.background,
    ...shadowStyles },
  sectionTitle: { color: colors.secondary, marginBottom: 12, fontWeight: '600' },
  option: { flexDirection: 'row', alignItems: 'center', gap: 12, minHeight: 44, padding: 10, borderRadius: 6 },
  label: { flex: 1, color: colors.primary, fontSize: 16 },
  selectedOption: { backgroundColor: `${colors.accent}33` },
});
