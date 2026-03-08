"""
이미지 분석 API: 업로드된 옷 사진 → GPT-4o Vision으로 카테고리/색상(HEX)/재질/스타일 추출
"""

from fastapi import APIRouter, HTTPException
from openai import OpenAI
import os

from app.models.schemas import ClothingAnalysisRequest, ClothingAnalysisResponse
from app.services.vision_service import analyze_clothing_image

router = APIRouter(prefix="/analyze", tags=["analyze"])


def get_openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    return OpenAI(api_key=key)


@router.post("/clothing", response_model=ClothingAnalysisResponse)
def analyze_clothing(req: ClothingAnalysisRequest) -> ClothingAnalysisResponse:
    """
    옷 이미지를 분석하여 JSON 형태로 다음 정보를 반환합니다.
    - category: top | bottom | outer | shoes | accessory
    - sub_category: 티셔츠, 청바지 등
    - primary_color: { hex: "#RRGGBB", name: "네이비" }
    - secondary_colors: 부가 색상 배열
    - material: 면, 울, 니트 등
    - style_tags: 캐주얼, 포멀 등
    """
    if not req.image_url and not req.image_base64:
        raise HTTPException(status_code=400, detail="image_url or image_base64 required")
    try:
        client = get_openai_client()
        return analyze_clothing_image(
            client,
            image_url=req.image_url,
            image_base64=req.image_base64,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Vision API error: {e}")
