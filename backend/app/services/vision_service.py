"""
이미지 분석 및 태깅: OpenAI GPT-4o Vision API 연동
업로드된 옷 사진에서 종류(상의/하의 등), 색상(HEX), 재질, 스타일을 JSON으로 추출
"""

import json
import base64
import re
from typing import Optional

from openai import OpenAI
from pydantic import ValidationError

from app.models.schemas import (
    ClothingAnalysisResponse,
    ColorInfo,
)


# Vision 분석용 시스템 프롬프트: JSON 구조를 엄격히 요구
VISION_SYSTEM_PROMPT = """You are a fashion expert and color analyst. Analyze the clothing in the image and return ONLY a valid JSON object with no markdown or extra text.

Required JSON structure:
{
  "category": "top" | "bottom" | "outer" | "shoes" | "accessory",
  "sub_category": "e.g. t-shirt, jeans, blazer (optional string)",
  "primary_color": { "hex": "#RRGGBB", "name": "e.g. Navy (optional)" },
  "secondary_colors": [ { "hex": "#RRGGBB", "name": "optional" }, ... ],
  "material": "e.g. cotton, wool, knit (optional)",
  "style_tags": ["casual", "formal", "minimal", "street", ... ],
  "raw_notes": "optional short description"
}

Rules:
- primary_color.hex MUST be a valid 6-digit hex color (#RRGGBB). Infer from the dominant color of the garment.
- secondary_colors: list other visible colors (pockets, prints, etc.). Each must have "hex".
- category must be exactly one of: top, bottom, outer, shoes, accessory.
- Return only the JSON object, no code block or explanation."""


def _extract_json_from_content(content: str) -> dict:
    """응답 텍스트에서 JSON 블록만 추출 (마크다운 코드블록 제거)"""
    text = content.strip()
    # ```json ... ``` 제거
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def analyze_clothing_image(
    client: OpenAI,
    *,
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> ClothingAnalysisResponse:
    """
    옷 이미지를 분석하여 카테고리, 색상(HEX), 재질, 스타일을 반환.
    image_url 또는 image_base64 중 하나 필수.
    """
    if not image_url and not image_base64:
        raise ValueError("image_url or image_base64 is required")

    # 메시지에 넣을 이미지 내용 구성
    image_content: list = []
    if image_url:
        image_content.append({"type": "image_url", "image_url": {"url": image_url}})
    else:
        # base64: data URL이면 제거 후 사용
        b64 = image_base64
        if b64.startswith("data:"):
            b64 = b64.split(",", 1)[-1]
        image_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
        })

    messages = [
        {"role": "system", "content": VISION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this clothing item and return the JSON only."},
                *image_content,
            ],
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
    )
    raw = response.choices[0].message.content
    data = _extract_json_from_content(raw)

    # HEX 정규화: # 없으면 붙이기
    def normalize_hex(hex_str: str) -> str:
        if not hex_str.startswith("#"):
            return "#" + hex_str
        return hex_str

    if "primary_color" in data and isinstance(data["primary_color"], dict):
        data["primary_color"]["hex"] = normalize_hex(data["primary_color"].get("hex", "#000000"))
    for c in data.get("secondary_colors") or []:
        if isinstance(c, dict) and "hex" in c:
            c["hex"] = normalize_hex(c["hex"])

    return ClothingAnalysisResponse(**data)
