import { Stack } from 'expo-router';

// Extremely helpful documentation on adding authentication to this:
// https://docs.expo.dev/router/advanced/authentication/

export default function Root() {
  return (
    <Stack>
        <Stack.Screen name="sign-in" options={{ headerShown: false }} />
        <Stack.Screen name="verify-email" options={{ headerShown: false }} />
        <Stack.Screen name="verify-code" options={{ headerShown: false }} />
        <Stack.Screen name="already-exists" options={{ headerShown: false }} />
        <Stack.Screen name="(app)" options={{ headerShown: false }} />
    </Stack>
  );
}
