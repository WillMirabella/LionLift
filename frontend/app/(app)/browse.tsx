import { useEffect, useState } from 'react';
import { Tabs } from 'expo-router';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import UserViewSelector from '../../components/user-view-selector';
import { defaultBrowseOptions } from '../../services/browse-options';
import { fetchBrowseUsers, type BrowseUser } from '../../services/browse-users';
import { screenStyles } from '../../constants/screen-styles';
import { colors } from '../../constants/colors';

export default function BrowseScreen() {
  const [expanded, setExpanded] = useState(false);
  const [options, setOptions] = useState(defaultBrowseOptions);
  const [users, setUsers] = useState<BrowseUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [request, setRequest] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError('');
    setUsers([]);
    fetchBrowseUsers(options, controller.signal)
      .then(results => {
        if (!controller.signal.aborted) setUsers(results);
      })
      .catch(error => {
        if (!controller.signal.aborted) {
          setError(error instanceof Error ? error.message : 'Could not load users. Please try again.');
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    // Ignore an older response if filters change or the screen unmounts.
    return () => controller.abort();
  }, [options, request]);

  return (
    <>
      <Tabs.Screen options={{
        headerRight: () => <UserViewSelector expanded={expanded} onChange={setExpanded}
          options={options} onApply={value => { setOptions(value); setRequest(count => count + 1); }} />,
      }} />
      <ScrollView style={screenStyles.screen} contentContainerStyle={screenStyles.content}>
        {loading ? <View style={styles.message}>
          <ActivityIndicator accessibilityLabel="Loading users" color={colors.primary} />
          <Text style={styles.text}>Loading users…</Text>
        </View> : error ? <View style={styles.message}>
          <Text accessibilityRole="alert" style={styles.text}>{error}</Text>
          <Pressable accessibilityRole="button" onPress={() => setRequest(count => count + 1)} style={styles.retry}>
            <Text style={styles.text}>Try again</Text>
          </Pressable>
        </View> : users.length === 0 ?
          <Text style={styles.text}>No users found. Try changing or resetting your filters.</Text> : <>
            <Text style={styles.text}>{users.length} users found</Text>
            <Text style={styles.note}>Results preview — full user cards will be connected next.</Text>
            {users.map(user => <View key={user.id} style={styles.result}>
              <Text style={styles.name}>{[user.first_name, user.last_name].filter(Boolean).join(' ') || 'Unnamed user'}</Text>
              {expanded && <>
                <Text style={styles.text}>{user.major || 'Major not provided'}</Text>
                <Text style={styles.text}>Graduation year: {user.grad_year ?? 'Not provided'}</Text>
                <Text style={styles.text}>{user.car_id === null ? 'Rider' : 'Driver'}</Text>
              </>}
            </View>)}
          </>}
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  message: { alignItems: 'center', gap: 12, paddingVertical: 24 },
  text: { color: colors.primary, fontSize: 16 },
  note: { color: colors.secondary, marginVertical: 12 },
  name: { color: colors.primary, fontSize: 18, fontWeight: '600' },
  result: { paddingVertical: 16, gap: 8, borderBottomWidth: 1, borderColor: colors.border },
  retry: { minHeight: 44, padding: 12, borderRadius: 6, backgroundColor: `${colors.accent}33` },
});
