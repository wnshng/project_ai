-- AI 스마트 클로젯: 가상 옷장 스키마
-- Supabase SQL Editor에서 실행

-- 사용자(앱 기준)는 Supabase Auth와 연동 가능. 여기서는 user_id만 참조.
-- 옷 카테고리 Enum (상의/하의/아우터/신발/악세서리 등)
CREATE TYPE clothing_category AS ENUM (
  'top',      -- 상의
  'bottom',   -- 하의
  'outer',    -- 아우터
  'shoes',    -- 신발
  'accessory' -- 악세서리
);

-- 계절성
CREATE TYPE season_type AS ENUM ('spring', 'summer', 'fall', 'winter', 'all');

-- 옷 아이템 테이블
CREATE TABLE closet_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,  -- Supabase auth.users(id) 참조 가능
  -- 이미지: Supabase Storage URL 또는 외부 URL
  image_url TEXT,
  -- AI/수동 입력 메타데이터
  category clothing_category NOT NULL,
  sub_category TEXT,           -- 예: 티셔츠, 청바지, 블레이저
  primary_color_hex CHAR(7),   -- 대표 색상 HEX (#RRGGBB)
  secondary_colors_hex TEXT[],  -- 부가 색상 배열
  material TEXT,               -- 면, 울, 니트 등
  style_tags TEXT[],           -- 캐주얼, 포멀, 미니멀 등
  brand TEXT,
  season season_type DEFAULT 'all',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 코디 추천 결과 저장 (선택: 사용자가 마음에 든 조합 저장)
CREATE TABLE outfit_saves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  item_ids UUID[] NOT NULL,    -- closet_items.id 배열
  recommendation_type TEXT,    -- tone_on_tone, complementary, analogous 등
  score FLOAT,                 -- 추천 점수
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 인덱스: 사용자별 옷장 조회, 색상/카테고리 필터
CREATE INDEX idx_closet_items_user_id ON closet_items(user_id);
CREATE INDEX idx_closet_items_category ON closet_items(category);
CREATE INDEX idx_closet_items_primary_color ON closet_items(primary_color_hex);
CREATE INDEX idx_outfit_saves_user_id ON outfit_saves(user_id);

-- RLS (Row Level Security) 예시: user_id로 본인 데이터만 접근
ALTER TABLE closet_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE outfit_saves ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own closet items"
  ON closet_items FOR ALL
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own outfit saves"
  ON outfit_saves FOR ALL
  USING (auth.uid() = user_id);

COMMENT ON TABLE closet_items IS '가상 옷장 아이템: AI Vision 추출 또는 수동 입력';
COMMENT ON TABLE outfit_saves IS '사용자가 저장한 코디 조합';
