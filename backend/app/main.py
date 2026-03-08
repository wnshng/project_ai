"""
AI 스마트 클로젯 백엔드 진입점
- /analyze/clothing: 이미지 → 옷 메타데이터 (Vision API)
- /closet/items: 옷장 CRUD (Supabase)
- /recommend/outfit: 코디 추천 (색상 알고리즘 + GPT)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import analyze, closet, recommend

app = FastAPI(
    title="AI Smart Closet API",
    description="옷 이미지 분석, 가상 옷장, AI 코디 추천",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(closet.router)
app.include_router(recommend.router)


@app.get("/")
def root():
    return {"service": "AI Smart Closet API", "docs": "/docs"}
