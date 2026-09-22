import { Tabs } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StyleSheet } from 'react-native';

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={styles.root}>
      <SafeAreaProvider>
        <Tabs
          screenOptions={{
            headerTitleStyle: { fontWeight: '600' },
            tabBarLabelStyle: { fontSize: 12 },
          }}
        >
          <Tabs.Screen name="index" options={{ title: 'Home', tabBarLabel: 'Home' }} />
          <Tabs.Screen name="scan" options={{ title: 'Scan', tabBarLabel: 'Scan' }} />
          <Tabs.Screen
            name="history"
            options={{ title: 'History', tabBarLabel: 'History' }}
          />
          <Tabs.Screen
            name="analytics"
            options={{ title: 'Analytics', tabBarLabel: 'Analytics' }}
          />
        </Tabs>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
});
