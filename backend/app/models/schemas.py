# Pydantic 스키마: API 요청/응답 및 옷/코디 데이터 구조

from typing import Optional
from pydantic import BaseModel, Field


# ----- 이미지 분석 (Vision API) -----

class ClothingAnalysisRequest(BaseModel):
    """이미지 URL 또는 base64를 받아 옷 정보 추출 요청"""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None  # data URL 제거한 순수 base64


class ColorInfo(BaseModel):
    """색상 정보 (HEX 등)"""
    hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    name: Optional[str] = None  # 예: 네이비, 베이지


class ClothingAnalysisResponse(BaseModel):
    """Vision API 분석 결과: 옷 종류, 색상, 재질, 스타일"""
    category: str  # top, bottom, outer, shoes, accessory
    sub_category: Optional[str] = None  # 티셔츠, 청바지 등
    primary_color: ColorInfo
    secondary_colors: list[ColorInfo] = []
    material: Optional[str] = None
    style_tags: list[str] = []
    raw_notes: Optional[str] = None  # 모델이 추가로 적은 설명


# ----- 옷장 아이템 (DB ↔ API) -----

class ClosetItemCreate(BaseModel):
    """옷 등록 시 사용 (이미지 분석 결과 또는 수동 입력)"""
    user_id: str
    image_url: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    primary_color_hex: Optional[str] = None
    secondary_colors_hex: list[str] = []
    material: Optional[str] = None
    style_tags: list[str] = []
    brand: Optional[str] = None
    season: str = "all"
    notes: Optional[str] = None


class ClosetItemResponse(BaseModel):
    """옷장 아이템 조회 응답"""
    id: str
    user_id: str
    image_url: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    primary_color_hex: Optional[str] = None
    secondary_colors_hex: list[str] = []
    material: Optional[str] = None
    style_tags: list[str] = []
    brand: Optional[str] = None
    season: str = "all"
    notes: Optional[str] = None


# ----- 코디 추천 -----

class OutfitRecommendationRequest(BaseModel):
    """코디 추천 요청"""
    user_id: str
    preference: Optional[str] = None  # "tone_on_tone", "complementary", "analogous" 등


class OutfitRecommendationItem(BaseModel):
    """추천된 한 벌에 포함된 아이템 요약"""
    id: str
    category: str
    primary_color_hex: Optional[str] = None
    sub_category: Optional[str] = None


class OutfitRecommendation(BaseModel):
    """한 벌 코디 추천 결과"""
    item_ids: list[str]
    items: list[OutfitRecommendationItem]
    recommendation_type: str  # tone_on_tone, complementary, analogous
    reason: Optional[str] = None  # 추천 이유 문장
    score: float = 0.0
