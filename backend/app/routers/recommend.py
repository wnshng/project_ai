"""
AI 코디 추천 API: 옷장 아이템 기반 톤온톤/보색/유사색 조합 추천
"""

from fastapi import APIRouter, HTTPException
import os

from openai import OpenAI

from app.models.schemas import OutfitRecommendation, OutfitRecommendationItem, OutfitRecommendationRequest
from app.routers.closet import get_supabase, _in_memory_closet, list_closet_items
from app.services.recommendation_service import (
    build_outfit_combinations,
    generate_recommendation_reason,
)

router = APIRouter(prefix="/recommend", tags=["recommend"])


def get_openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    return OpenAI(api_key=key)


@router.post("/outfit", response_model=list[OutfitRecommendation])
def recommend_outfit(req: OutfitRecommendationRequest) -> list[OutfitRecommendation]:
    """
    현재 옷장 아이템 중에서 색상 대비(보색, 유사색) 및 톤온톤을 고려해
    착장 조합을 추천합니다. preference로 타입 지정 가능.
    """
    user_id = req.user_id
    # 옷장 목록 가져오기
    items = list_closet_items(user_id)
    if len(items) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least 2 items in closet (e.g. top + bottom)",
        )
    # dict 리스트로 통일 (Supabase는 snake_case)
    item_list = []
    for it in items:
        if isinstance(it, dict):
            item_list.append({
                "id": str(it.get("id")),
                "category": it.get("category") or "top",
                "primary_color_hex": it.get("primary_color_hex"),
                "sub_category": it.get("sub_category"),
            })
        else:
            item_list.append({
                "id": str(getattr(it, "id", "")),
                "category": getattr(it, "category", "top"),
                "primary_color_hex": getattr(it, "primary_color_hex", None),
                "sub_category": getattr(it, "sub_category", None),
            })

    types = None
    if req.preference and req.preference in ("tone_on_tone", "complementary", "analogous"):
        types = [req.preference]

    combos = build_outfit_combinations(item_list, top_k=5, types=types)
    if not combos:
        raise HTTPException(status_code=404, detail="No valid outfit combination found")

    client = get_openai_client()
    result: list[OutfitRecommendation] = []
    for c in combos:
        reason = generate_recommendation_reason(client, c, c["recommendation_type"])
        result.append(OutfitRecommendation(
            item_ids=c["item_ids"],
            items=[
                OutfitRecommendationItem(
                    id=x["id"],
                    category=x.get("category", "top"),
                    primary_color_hex=x.get("primary_color_hex"),
                    sub_category=x.get("sub_category"),
                )
                for x in c["items"]
            ],
            recommendation_type=c["recommendation_type"],
            reason=reason,
            score=c["score"],
        ))
    return result
