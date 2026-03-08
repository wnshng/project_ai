"""
가상 옷장 API: 옷 등록/조회 (Supabase 연동)
실제 Supabase 클라이언트 주입은 main에서 하며, 여기서는 라우터만 정의.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import os

from app.models.schemas import ClosetItemCreate, ClosetItemResponse

router = APIRouter(prefix="/closet", tags=["closet"])

# Supabase는 선택적: 환경변수 없으면 메모리 저장으로 동작
try:
    from supabase import create_client, Client
    _supabase: Optional[Client] = None

    def get_supabase() -> Optional[Client]:
        global _supabase
        if _supabase is not None:
            return _supabase
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if url and key:
            _supabase = create_client(url, key)
        return _supabase
except ImportError:
    def get_supabase():
        return None


# 데모용 인메모리 저장 (Supabase 미설정 시)
_in_memory_closet: list[dict] = []


@router.post("/items", response_model=dict)
def create_closet_item(item: ClosetItemCreate) -> dict:
    """옷장에 아이템 등록 (이미지 분석 결과 또는 수동 입력)"""
    sb = get_supabase()
    payload = item.model_dump()
    if sb:
        row = sb.table("closet_items").insert(payload).execute()
        data = row.data
        if data:
            return data[0]
        raise HTTPException(status_code=500, detail="Insert failed")
    # 인메모리
    import uuid
    id_ = str(uuid.uuid4())
    rec = {"id": id_, **payload}
    _in_memory_closet.append(rec)
    return rec


@router.get("/items", response_model=list)
def list_closet_items(user_id: str, category: Optional[str] = None) -> list:
    """사용자별 옷장 목록 조회. category로 필터 가능."""
    sb = get_supabase()
    if sb:
        q = sb.table("closet_items").select("*").eq("user_id", user_id)
        if category:
            q = q.eq("category", category)
        row = q.execute()
        return row.data or []
    items = [x for x in _in_memory_closet if x.get("user_id") == user_id]
    if category:
        items = [x for x in items if x.get("category") == category]
    return items


@router.get("/items/{item_id}", response_model=dict)
def get_closet_item(item_id: str) -> dict:
    """단일 아이템 조회"""
    sb = get_supabase()
    if sb:
        row = sb.table("closet_items").select("*").eq("id", item_id).execute()
        if row.data:
            return row.data[0]
    for x in _in_memory_closet:
        if x.get("id") == item_id:
            return x
    raise HTTPException(status_code=404, detail="Item not found")
