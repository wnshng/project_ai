import { Tabs } from "expo-router";
import { Closet, Sparkles } from "lucide-react-native";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#2D3142",
        tabBarInactiveTintColor: "#BFC0C0",
        headerStyle: { backgroundColor: "#2D3142" },
        headerTintColor: "#EFEFEF",
        tabBarStyle: { backgroundColor: "#EFEFEF" },
      }}
    >
      <Tabs.Screen
        name="closet"
        options={{
          title: "내 옷장",
          tabBarIcon: ({ color, size }) => <Closet color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="recommend"
        options={{
          title: "코디 추천",
          tabBarIcon: ({ color, size }) => <Sparkles color={color} size={size} />,
        }}
      />
    </Tabs>
  );
}
