/**
 * 백엔드 API 클라이언트
 * EXPO_PUBLIC_API_URL 또는 기본 localhost:8000 사용
 */

import axios from "axios";

const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

/** 옷 이미지 분석 (Vision API) */
export async function analyzeClothing(imageBase64: string) {
  const { data } = await api.post("/analyze/clothing", {
    image_base64: imageBase64,
  });
  return data;
}

/** 옷장에 아이템 등록 */
export async function createClosetItem(userId: string, item: Record<string, unknown>) {
  const { data } = await api.post("/closet/items", {
    user_id: userId,
    ...item,
  });
  return data;
}

/** 옷장 목록 조회 */
export async function listClosetItems(userId: string, category?: string) {
  const params = category ? { user_id: userId, category } : { user_id: userId };
  const { data } = await api.get("/closet/items", { params });
  return data;
}

/** 코디 추천 */
export async function recommendOutfit(userId: string, preference?: string) {
  const { data } = await api.post("/recommend/outfit", {
    user_id: userId,
    preference: preference || null,
  });
  return data;
}
