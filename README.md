# AI 스마트 클로젯 (Smart Closet)

사진/텍스트로 옷을 등록하고, AI가 퍼스널 컬러·스타일 조합을 제안하는 앱입니다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | React Native (Expo), NativeWind (Tailwind CSS) |
| Backend | Python 3.11+, FastAPI |
| Database | Supabase (PostgreSQL) |
| AI | OpenAI API (GPT-4o Vision, GPT-4o) |

## 프로젝트 구조

```
project_ai/
├── frontend/                 # React Native (Expo) 앱
│   ├── app/
│   │   ├── (tabs)/
│   │   │   ├── closet.tsx    # 옷장 화면
│   │   │   └── recommend.tsx # 코디 추천 피드
│   │   └── _layout.tsx
│   ├── components/
│   ├── lib/
│   └── package.json
├── backend/                  # FastAPI 서버
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── services/
│   │   └── models/
│   ├── requirements.txt
│   └── .env.example
├── supabase/
│   └── migrations/          # DB 스키마
└── README.md
```

## 초기 환경 설정

### 1. 사전 요구사항

- Node.js 18+
- Python 3.11+
- [Expo CLI](https://docs.expo.dev/get-started/installation/) (`npm i -g expo-cli`)
- Supabase 계정, OpenAI API 키

### 2. 백엔드 설정

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # .env에 OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY 입력
uvicorn app.main:app --reload
```

서버: http://localhost:8000  
API 문서: http://localhost:8000/docs

### 3. 프론트엔드 설정

```bash
cd frontend
npm install
npx expo start
```

### 4. Supabase 설정

1. [Supabase](https://supabase.com)에서 프로젝트 생성
2. SQL Editor에서 `supabase/migrations/001_initial_schema.sql` 실행
3. `.env`에 `SUPABASE_URL`, `SUPABASE_ANON_KEY` 설정

### 5. 환경 변수 (.env)

**backend/.env**

```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

**frontend/.env**

```
EXPO_PUBLIC_API_URL=http://localhost:8000
```

---

## 핵심 기능

1. **이미지 분석**: 업로드한 사진 → GPT-4o Vision으로 종류·색상(HEX)·재질·스타일 추출
2. **가상 옷장**: Supabase에 옷 메타데이터 저장·조회
3. **AI 코디**: 톤온톤·보색 대비 등 색상 이론 기반 착장 추천
4. **UI**: 옷장 카드 뷰, 코디 추천 피드

## 추가 확장 아이디어

- **remove.bg**: 배경 제거로 옷장 UI 정리
- **날씨 API**: 기온에 맞춘 코디 추천
- **퍼스널 컬러**: 프로필 사진 분석 → 웜톤/쿨톤 기반 추천
