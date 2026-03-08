/**
 * 옷장 화면: 카드 뷰 형식으로 등록된 옷 목록 표시
 * 사진 촬영/갤러리에서 선택 → API 분석 → 옷장에 추가
 */

import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as FileSystem from "expo-file-system";
import { Plus, Shirt } from "lucide-react-native";
import { listClosetItems, createClosetItem, analyzeClothing } from "../../lib/api";

const DEMO_USER_ID = "demo-user-1";

export default function ClosetScreen() {
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadCloset = useCallback(async () => {
    try {
      const data = await listClosetItems(DEMO_USER_ID);
      setItems(Array.isArray(data) ? data : []);
    } catch (e) {
      console.warn("Closet load failed", e);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCloset();
  }, [loadCloset]);

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("권한 필요", "갤러리 접근 권한을 허용해 주세요.");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      base64: true,
      quality: 0.8,
    });
    if (result.canceled || !result.assets[0].base64) return;
    await addItemFromBase64(result.assets[0].base64);
  };

  const addItemFromBase64 = async (base64: string) => {
    setUploading(true);
    try {
      const analysis = await analyzeClothing(base64);
      const payload = {
        category: analysis.category,
        sub_category: analysis.sub_category ?? undefined,
        primary_color_hex: analysis.primary_color?.hex ?? undefined,
        secondary_colors_hex: (analysis.secondary_colors ?? []).map((c: { hex: string }) => c.hex),
        material: analysis.material ?? undefined,
        style_tags: analysis.style_tags ?? [],
        season: "all",
      };
      await createClosetItem(DEMO_USER_ID, payload);
      await loadCloset();
    } catch (e) {
      console.error(e);
      Alert.alert("등록 실패", "이미지 분석 또는 저장에 실패했습니다.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <View className="flex-1 bg-closet-surface">
      <View className="flex-row items-center justify-between px-4 py-3 bg-closet-primary">
        <Text className="text-lg font-semibold text-white">내 옷장</Text>
        <TouchableOpacity
          onPress={pickImage}
          disabled={uploading}
          className="flex-row items-center gap-2 rounded-lg bg-white/20 px-3 py-2"
        >
          {uploading ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <Plus size={20} color="#fff" />
          )}
          <Text className="text-white font-medium">추가</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color="#2D3142" />
        </View>
      ) : (
        <ScrollView
          className="flex-1 px-4 py-4"
          contentContainerStyle={{ flexDirection: "row", flexWrap: "wrap", gap: 12, paddingBottom: 24 }}
        >
          {items.length === 0 ? (
            <View className="flex-1 items-center justify-center py-16">
              <Shirt size={64} color="#BFC0C0" />
              <Text className="mt-4 text-closet-secondary text-center">
                옷 사진을 추가하면 AI가 분석해 등록해요.
              </Text>
              <TouchableOpacity
                onPress={pickImage}
                className="mt-4 rounded-xl bg-closet-primary px-6 py-3"
              >
                <Text className="text-white font-semibold">사진에서 추가하기</Text>
              </TouchableOpacity>
            </View>
          ) : (
            items.map((item: Record<string, unknown>) => (
              <View
                key={String(item.id)}
                className="w-[47%] rounded-xl bg-white p-3 shadow-sm"
              >
                {item.image_url ? (
                  <Image
                    source={{ uri: item.image_url as string }}
                    className="h-32 w-full rounded-lg bg-closet-accent"
                    resizeMode="cover"
                  />
                ) : (
                  <View
                    className="h-32 w-full rounded-lg items-center justify-center"
                    style={{
                      backgroundColor: (item.primary_color_hex as string) || "#BFC0C0",
                    }}
                  >
                    <Shirt size={40} color="#fff" />
                  </View>
                )}
                <Text className="mt-2 font-semibold text-closet-primary">
                  {String(item.sub_category || item.category)}
                </Text>
                <Text className="text-sm text-closet-secondary">
                  {(item.primary_color_hex as string) || "-"}
                </Text>
              </View>
            ))
          )}
        </ScrollView>
      )}
    </View>
  );
}
