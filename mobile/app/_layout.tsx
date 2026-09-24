import { Tabs } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StyleSheet } from 'react-native';

import { TabIcon } from '../src/components/TabIcon';
import { colors } from '../src/constants/theme';

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={styles.root}>
      <SafeAreaProvider>
        <Tabs
          screenOptions={{
            headerShown: false,
            tabBarStyle: {
              backgroundColor: colors.surface,
              borderTopColor: colors.border,
            },
            tabBarActiveTintColor: colors.graphite,
            tabBarInactiveTintColor: colors.textSecondary,
            tabBarLabelStyle: { fontSize: 12, fontWeight: '600' },
          }}
        >
          <Tabs.Screen
            name="index"
            options={{
              title: 'EggVision',
              tabBarLabel: 'Home',
              tabBarIcon: ({ color }) => <TabIcon name="home" color={color} />,
            }}
          />
          <Tabs.Screen
            name="scan"
            options={{
              title: 'Scan',
              tabBarLabel: 'Scan',
              tabBarIcon: ({ color }) => <TabIcon name="scan" color={color} />,
            }}
          />
          <Tabs.Screen
            name="history"
            options={{
              title: 'Historial',
              tabBarLabel: 'History',
              tabBarIcon: ({ color }) => <TabIcon name="history" color={color} />,
            }}
          />
          <Tabs.Screen
            name="analytics"
            options={{
              title: 'Analítica',
              tabBarLabel: 'Analytics',
              tabBarIcon: ({ color }) => <TabIcon name="analytics" color={color} />,
            }}
          />
        </Tabs>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background,
  },
});
