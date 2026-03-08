# Cursor 단계별 프롬프트 (복사용)

아래 프롬프트를 Cursor Composer(Ctrl+I) 또는 Chat에 붙여넣어 확장 개발할 수 있습니다.

---

## Step 1: 프로젝트 기초 뼈대 (완료됨)

> "위 프롬프트를 기반으로 Expo(React Native) 프로젝트의 초기 폴더 구조를 잡고, 필요한 라이브러리(lucide-react-native, axios, nativewind)가 포함된 package.json을 만들어줘."

→ 이미 `frontend/` 구조와 `package.json`에 반영되어 있음.

---

## Step 2: 옷 분석 로직 구현 (완료됨)

> "OpenAI Vision API를 사용해서 image_url을 받으면 옷의 색상과 카테고리를 JSON 형태로 반환하는 Python(FastAPI) 백엔드 함수를 작성해줘."

→ `backend/app/routers/analyze.py`, `backend/app/services/vision_service.py` 에 구현됨.  
- `POST /analyze/clothing` 에 `image_url` 또는 `image_base64` 전달.

---

## Step 3: 컬러 조합 알고리즘 (완료됨)

> "저장된 옷들의 색상(HEX 값)을 비교해서 '톤온톤(Tone on Tone)'이나 '보색 대비' 코디를 추천해주는 로직을 작성해. 색상 이론을 코드에 반영해줘."

→ `backend/app/services/color_algorithm.py` (HSV 기반 톤온톤/보색/유사색 점수),  
→ `backend/app/services/recommendation_service.py` (조합 생성 + GPT 추천 문장).

---

## 확장용 프롬프트 예시

- **이미지 전처리**: "remove.bg API를 연동해서 옷 사진 업로드 시 배경을 제거한 뒤 Vision API로 분석하도록 백엔드에 추가해줘."
- **날씨 연동**: "현재 위치 기온을 가져와서 '오늘 니트 추천' 같은 문장을 코디 추천 이유에 포함하는 로직을 추가해줘. Open-Meteo 또는 원하는 날씨 API 사용."
- **퍼스널 컬러**: "사용자 프로필 사진을 분석해서 웜톤/쿨톤을 판별하고, 그에 맞는 옷을 우선 추천하도록 recommend 서비스를 수정해줘."
