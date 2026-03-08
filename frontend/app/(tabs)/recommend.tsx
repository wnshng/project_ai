/**
 * 코디 추천 피드: 옷장 아이템 기반 톤온톤/보색/유사색 추천 카드
 */

import { useState, useCallback, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { Sparkles } from "lucide-react-native";
import { recommendOutfit } from "../../lib/api";

const DEMO_USER_ID = "demo-user-1";

const TYPE_LABELS: Record<string, string> = {
  tone_on_tone: "톤온톤",
  complementary: "보색 대비",
  analogous: "유사색 조화",
};

type OutfitItem = {
  id: string;
  category: string;
  primary_color_hex?: string;
  sub_category?: string;
};

type Recommendation = {
  item_ids: string[];
  items: OutfitItem[];
  recommendation_type: string;
  reason?: string;
  score: number;
};

export default function RecommendScreen() {
  const [list, setList] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchRecommendations = useCallback(async () => {
    setLoading(true);
    try {
      const data = await recommendOutfit(DEMO_USER_ID);
      setList(Array.isArray(data) ? data : []);
    } catch (e) {
      console.warn("Recommend failed", e);
      setList([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchRecommendations();
  };

  // 탭 진입 시 한 번 자동 요청
  useEffect(() => {
    fetchRecommendations();
  }, []);

  return (
    <View className="flex-1 bg-closet-surface">
      <View className="px-4 py-3 bg-closet-primary">
        <Text className="text-lg font-semibold text-white">오늘의 코디 추천</Text>
        <Text className="mt-1 text-sm text-white/80">
          색상 이론 기반 톤온톤·보색·유사색 조합
        </Text>
      </View>

      {loading && list.length === 0 ? (
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color="#2D3142" />
          <Text className="mt-4 text-closet-secondary">추천 생성 중...</Text>
        </View>
      ) : list.length === 0 ? (
        <View className="flex-1 items-center justify-center px-8">
          <Sparkles size={56} color="#BFC0C0" />
          <Text className="mt-4 text-center text-closet-secondary">
            옷장에 상의·하의를 2개 이상 등록하면{"\n"}코디 추천을 받을 수 있어요.
          </Text>
          <TouchableOpacity
            onPress={fetchRecommendations}
            className="mt-6 rounded-xl bg-closet-primary px-6 py-3"
          >
            <Text className="text-white font-semibold">다시 시도</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView
          className="flex-1 px-4 py-4"
          contentContainerStyle={{ paddingBottom: 100 }}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          {list.map((rec, idx) => (
            <View
              key={idx}
              className="mb-4 rounded-xl bg-white p-4 shadow-sm"
            >
              <View className="flex-row items-center justify-between mb-3">
                <Text className="font-semibold text-closet-primary">
                  {TYPE_LABELS[rec.recommendation_type] || rec.recommendation_type}
                </Text>
                <View className="rounded-full bg-closet-accent px-2 py-0.5">
                  <Text className="text-xs text-closet-secondary">
                    {(rec.score * 100).toFixed(0)}점
                  </Text>
                </View>
              </View>
              {rec.reason ? (
                <Text className="mb-3 text-sm text-closet-secondary">
                  {rec.reason}
                </Text>
              ) : null}
              <View className="flex-row flex-wrap gap-2">
                {rec.items.map((it) => (
                  <View
                    key={it.id}
                    className="rounded-lg px-3 py-2"
                    style={{
                      backgroundColor: it.primary_color_hex || "#E0E0E0",
                    }}
                  >
                    <Text className="text-sm font-medium text-white">
                      {it.sub_category || it.category}
                    </Text>
                    <Text className="text-xs text-white/80">
                      {it.primary_color_hex || "-"}
                    </Text>
                  </View>
                ))}
              </View>
            </View>
          ))}
        </ScrollView>
      )}

      {list.length > 0 && !loading && (
        <View className="absolute bottom-6 left-0 right-0 px-4">
          <TouchableOpacity
            onPress={onRefresh}
            className="rounded-xl bg-closet-primary py-3 items-center"
          >
            <Text className="text-white font-semibold">다른 코디 보기</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}
