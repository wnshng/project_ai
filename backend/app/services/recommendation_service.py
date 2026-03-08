"""
AI 코디 추천: 옷장 아이템 목록을 받아 색상 대비/스타일 일관성을 고려한 착장 추천.
Supabase에서 user_id로 아이템을 가져온 뒤, 색상 알고리즘으로 조합 후 GPT로 이유 문장 생성 가능.
"""

import random
from typing import Optional

from openai import OpenAI

from app.services.color_algorithm import score_outfit

# 추천 타입 라벨 (한글 설명용)
RECOMMENDATION_LABELS = {
    "tone_on_tone": "톤온톤",
    "complementary": "보색 대비",
    "analogous": "유사색 조화",
}


def build_outfit_combinations(
    items: list[dict],
    *,
    top_k: int = 10,
    types: Optional[list[str]] = None,
) -> list[dict]:
    """
    옷장 아이템 리스트에서 상의/하의/아우터 등 카테고리별로 1개씩 뽑아 조합 후,
    색상 점수로 정렬해 상위 top_k개 반환.
    items: DB에서 가져온 closet_items (id, category, primary_color_hex 등 포함)
    """
    if types is None:
        types = ["tone_on_tone", "complementary", "analogous"]

    by_cat: dict[str, list[dict]] = {}
    for it in items:
        cat = it.get("category") or "top"
        by_cat.setdefault(cat, []).append(it)

    # 최소한 상의+하의는 있어야 함
    if "top" not in by_cat or "bottom" not in by_cat:
        return []

    combos: list[dict] = []
    # 간단히: top 1개, bottom 1개, outer 0~1개 조합 (반복 횟수 제한)
    tops = by_cat.get("top", [])[:15]
    bottoms = by_cat.get("bottom", [])[:15]
    outers = by_cat.get("outer", [])[:5]

    for _ in range(50):  # 최대 50개 조합 시도
        top = random.choice(tops)
        bottom = random.choice(bottoms)
        combo = [top, bottom]
        if outers and random.random() > 0.5:
            combo.append(random.choice(outers))
        # 중복 조합 제거용 키
        key = tuple(sorted([c["id"] for c in combo]))
        if key in [tuple(sorted([x["id"] for x in c["items"]])) for c in combos]:
            continue

        best_type = None
        best_score = -1.0
        for t in types:
            s = score_outfit(
                [{"primary_color_hex": x.get("primary_color_hex") for x in combo],
                t,
            )
            if s > best_score:
                best_score = s
                best_type = t

        combos.append({
            "items": combo,
            "item_ids": [c["id"] for c in combo],
            "recommendation_type": best_type or "tone_on_tone",
            "score": best_score,
        })

    # 점수 내림차순, 상위 top_k
    combos.sort(key=lambda x: x["score"], reverse=True)
    return combos[:top_k]


def generate_recommendation_reason(
    client: OpenAI,
    outfit: dict,
    recommendation_type: str,
) -> str:
    """
    추천된 한 벌 코디에 대해 GPT로 짧은 추천 이유 문장 생성.
    """
    label = RECOMMENDATION_LABELS.get(recommendation_type, recommendation_type)
    items_desc = []
    for it in outfit.get("items", []):
        color = it.get("primary_color_hex") or "?"
        cat = it.get("sub_category") or it.get("category")
        items_desc.append(f"- {cat} ({color})")
    text = (
        f"Recommendation type: {label}. Items: " + " | ".join(items_desc)
        + ". Write one short Korean sentence (under 50 chars) explaining why this outfit works."
    )
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}],
            max_tokens=80,
        )
        return (r.choices[0].message.content or "").strip()
    except Exception:
        return f"{label} 조합으로 색감이 잘 맞아요."
