import { Redirect } from 'expo-router';

// Opening the app at / sends the user to the Find Drivers tab.
export default function Index() {
  return <Redirect href="/(app)/profile" />;
}
