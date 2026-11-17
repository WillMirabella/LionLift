import Ionicons from '@expo/vector-icons/Ionicons';
import { useState } from 'react';
import { Modal, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { colors } from '../constants/colors';
import { shadowStyles } from '../constants/shadow';

export type BrowseOptions = {
  sort: '' | 'first_name' | '-first_name' | 'grad_year' | '-grad_year';
  role: '' | 'driver' | 'rider';
  graduationYear: string;
};

export const defaultBrowseOptions: BrowseOptions = {
  sort: '', role: '', graduationYear: '',
};

const sortOptions: { value: BrowseOptions['sort']; label: string }[] = [
  { value: '', label: 'Default order' },
  { value: 'first_name', label: 'First name: A–Z' },
  { value: '-first_name', label: 'First name: Z–A' },
  { value: 'grad_year', label: 'Graduation year: earliest first' },
  { value: '-grad_year', label: 'Graduation year: latest first' },
];
const roleOptions: { value: BrowseOptions['role']; label: string }[] = [
  { value: '', label: 'Everyone' },
  { value: 'driver', label: 'Drivers' },
  { value: 'rider', label: 'Riders' },
];

type Props = {
  options: BrowseOptions;
  onApply: (options: BrowseOptions) => void;
  expanded: boolean;
  onChange: (expanded: boolean) => void;
};

// The screen shares the selected view with every user card.
export default function UserViewSelector({ expanded, onChange, options, onApply }: Props) {
  const [open, setOpen] = useState(false);
  const insets = useSafeAreaInsets();
  const [draft, setDraft] = useState(options);
  const yearIsValid = draft.graduationYear === '' || /^\d{4}$/.test(draft.graduationYear);

  function openMenu() {
    // Reopening discards any edits that were dismissed without Apply.
    setDraft(options);
    setOpen(true);
  }

  function applyOptions() {
    if (!yearIsValid) return;
    onApply(draft);
    setOpen(false);
  }

  function resetOptions() {
    setDraft(defaultBrowseOptions);
    onApply(defaultBrowseOptions);
  }

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
        onPress={openMenu}
        style={styles.headerButton}
      >
        <Ionicons name="options-outline" size={24} color={colors.primary} />
      </Pressable>
      <Modal transparent visible={open} animationType="fade" onRequestClose={() => setOpen(false)}>
        <View style={[styles.overlay, { paddingBottom: insets.bottom + 12 }]}>
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
            <ScrollView keyboardShouldPersistTaps="handled">
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
            <Text accessibilityRole="header" style={[styles.sectionTitle, styles.sectionSpacing]}>Sort</Text>
            {sortOptions.map(option => (
              <Pressable key={option.value} accessibilityRole="button"
                accessibilityState={{ selected: draft.sort === option.value }}
                onPress={() => setDraft({ ...draft, sort: option.value })}
                style={[styles.option, draft.sort === option.value && styles.selectedOption]}>
                <Text style={styles.label}>{option.label}</Text>
                {draft.sort === option.value && <Ionicons name="checkmark" size={20} color={colors.primary} />}
              </Pressable>
            ))}
            <Text accessibilityRole="header" style={[styles.sectionTitle, styles.sectionSpacing]}>Filter</Text>
            {roleOptions.map(option => (
              <Pressable key={option.value} accessibilityRole="button"
                accessibilityState={{ selected: draft.role === option.value }}
                onPress={() => setDraft({ ...draft, role: option.value })}
                style={[styles.option, draft.role === option.value && styles.selectedOption]}>
                <Text style={styles.label}>{option.label}</Text>
                {draft.role === option.value && <Ionicons name="checkmark" size={20} color={colors.primary} />}
              </Pressable>
            ))}
            <Text style={[styles.sectionTitle, styles.sectionSpacing]}>Graduation year</Text>
            <TextInput accessibilityLabel="Graduation year" placeholder="Any year"
              placeholderTextColor={colors.secondary} keyboardType="number-pad" maxLength={4}
              value={draft.graduationYear}
              onChangeText={graduationYear => setDraft({ ...draft, graduationYear })}
              style={styles.yearInput} />
            {!yearIsValid && <Text accessibilityRole="alert" style={styles.note}>Enter a four-digit year or leave it blank.</Text>}
            <Text style={styles.note}>Preview: sorting and filtering do not change the sample cards yet.</Text>
            </ScrollView>
            <View style={styles.actions}>
              <Pressable accessibilityRole="button" onPress={resetOptions} style={styles.action}>
                <Text style={styles.label}>Reset</Text>
              </Pressable>
              <Pressable accessibilityRole="button" accessibilityState={{ disabled: !yearIsValid }}
                disabled={!yearIsValid} onPress={applyOptions}
                style={[styles.action, styles.selectedOption, !yearIsValid && styles.disabled]}>
                <Text style={styles.label}>Apply</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  headerButton: { width: 44, height: 44, marginRight: 16, alignItems: 'center', justifyContent: 'center' },
  overlay: { flex: 1, backgroundColor: '#00000033', alignItems: 'flex-end' },
  menu: { width: 300, maxWidth: '90%', flexShrink: 1, padding: 12, borderRadius: 12, backgroundColor: colors.background,
    ...shadowStyles },
  sectionTitle: { color: colors.secondary, marginBottom: 12, fontWeight: '600' },
  option: { flexDirection: 'row', alignItems: 'center', gap: 12, minHeight: 44, padding: 10, borderRadius: 6 },
  label: { flex: 1, color: colors.primary, fontSize: 16 },
  sectionSpacing: { marginTop: 16 },
  yearInput: { minHeight: 44, padding: 10, borderWidth: 1, borderColor: colors.border,
    borderRadius: 6, color: colors.primary, fontSize: 16 },
  note: { color: colors.secondary, fontSize: 13, marginTop: 12 },
  actions: { flexDirection: 'row', gap: 12, marginTop: 12 },
  action: { flex: 1, minHeight: 44, padding: 10, borderRadius: 6, alignItems: 'center' },
  disabled: { opacity: 0.5 },
  selectedOption: { backgroundColor: `${colors.accent}33` },
});
