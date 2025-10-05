# 터치 기반 객체 인식 API 가이드

## 📖 개요

사용자가 작품의 특정 위치를 터치하면, 해당 위치의 객체를 자동으로 인식하고 LLM이 생성한 상세한 설명을 제공합니다.

## 🚀 API 사용 방법

### 1. 서버 실행

```bash
python api.py
```

서버가 실행되면 다음 주소에서 사용할 수 있습니다:
- **API 서버**: http://localhost:14723
- **API 문서**: http://localhost:14723/docs
- **ReDoc**: http://localhost:14723/redoc

### 2. 터치 기반 객체 인식 엔드포인트

#### `POST /touch`

작품의 특정 좌표를 터치하면 해당 위치의 객체를 인식하고 LLM으로 설명을 생성합니다.

**요청 형식:**

```json
{
  "art_name": "시녀들",
  "x": 0.5,
  "y": 0.5
}
```

**파라미터:**
- `art_name` (string, 필수): 작품명 (한글)
- `x` (float, 필수): x 좌표 (0~1, 0=왼쪽, 1=오른쪽)
- `y` (float, 필수): y 좌표 (0~1, 0=위, 1=아래)

**응답 형식 (객체 발견):**

```json
{
  "found": true,
  "object_name": "마르가리타 공주",
  "object_info": "작품 중앙의 주인공으로...",
  "description": "마르가리타 공주는 이 작품의 중심 인물로 당시 스페인 왕실의 공주이며 화가가 중앙에 배치하여 그녀의 중요성을 강조했습니다.",
  "art_name": "시녀들",
  "art_name_en": "Las Meninas"
}
```

**응답 형식 (객체 없음):**

```json
{
  "found": false,
  "message": "해당 위치에 인식된 객체가 없습니다."
}
```

### 3. 객체 목록 조회 엔드포인트

#### `POST /objects`

작품의 모든 객체 목록을 조회합니다.

**요청 형식:**

```json
{
  "art_name": "시녀들"
}
```

**응답 형식:**

```json
{
  "art_name": "시녀들",
  "art_name_en": "Las Meninas",
  "object_count": 11,
  "objects": [
    {
      "mask_id": 1,
      "name": "마르가리타 공주",
      "description": "...",
      "art_name": "시녀들",
      "art_name_en": "Las Meninas"
    },
    ...
  ]
}
```

## 💻 Python 클라이언트 예시

### 기본 사용

```python
import requests

BASE_URL = "http://localhost:14723"

# 터치 API 호출
response = requests.post(
    f"{BASE_URL}/touch",
    json={
        "art_name": "시녀들",
        "x": 0.5,  # 가로 중앙
        "y": 0.5   # 세로 중앙
    }
)

result = response.json()

if result["found"]:
    print(f"객체명: {result['object_name']}")
    print(f"설명: {result['description']}")
else:
    print(result["message"])
```

### 전체 테스트 실행

```bash
python client.py
```

## 🎨 지원 작품 목록

1. 프리마베라
2. 비너스의 탄생
3. 파리스의 심판
4. 아담의 창조
5. 최후의 만찬
6. 성 마태를 부르심
7. 아테네 학당
8. 회화의 기술
9. 시녀들
10. 야경

## 📊 좌표 시스템

터치 좌표는 **정규화된 좌표**를 사용합니다 (0~1):

- **x 좌표**: 
  - 0 = 이미지 왼쪽 끝
  - 0.5 = 이미지 가로 중앙
  - 1 = 이미지 오른쪽 끝

- **y 좌표**: 
  - 0 = 이미지 위쪽 끝
  - 0.5 = 이미지 세로 중앙
  - 1 = 이미지 아래쪽 끝

이 방식은 화면 크기나 이미지 해상도에 관계없이 동일한 위치를 가리킬 수 있습니다.

## 🔧 커스터마이징

### LLM 프롬프트 수정

`api.py`의 `touch_object_recognition` 함수에서 프롬프트를 수정할 수 있습니다:

```python
prompt = f"""당신은 미술관 큐레이터입니다.

작품명: {art_name_en} (한국어 작품명: {request.art_name})
객체명: {object_name}
객체 정보: {object_description}

관람객이 작품에서 "{object_name}"을(를) 터치했습니다.
이 객체에 대해 간결하게 설명해주세요.

**분량 제약: 정확히 1문장**
[프롬프트 내용...]
"""
```

### 응답 형식 커스터마이징

반환 딕셔너리를 수정하여 필요한 정보를 추가하거나 제거할 수 있습니다:

```python
return {
    "found": True,
    "object_name": object_name,
    "object_info": object_description,
    "description": llm_description,
    "art_name": request.art_name,
    "art_name_en": art_name_en,
    # 추가 필드...
}
```

## 🎯 사용 시나리오

### 1. XR 미술관 경험
```
사용자가 VR/AR 환경에서 작품의 특정 부분을 응시하거나 컨트롤러로 터치
→ 시선/터치 좌표를 정규화하여 API 호출
→ LLM 생성 설명을 TTS로 음성 재생
```

### 2. 모바일 앱
```
사용자가 스마트폰으로 작품 이미지를 터치
→ 터치 위치를 이미지 크기로 정규화
→ API 호출하여 객체 설명 표시
```

### 3. 터치스크린 키오스크
```
관람객이 대형 터치스크린에서 작품의 특정 부분 터치
→ 터치 좌표를 정규화하여 API 호출
→ 화면에 객체 설명과 하이라이트 표시
```

## 🔍 트러블슈팅

### 1. "해당 위치에 인식된 객체가 없습니다"

- 터치한 위치에 인식 가능한 객체가 없습니다.
- 다른 위치를 시도하거나 `/objects` 엔드포인트로 사용 가능한 객체 목록을 확인하세요.

### 2. "TouchRecognition 초기화에 실패했습니다"

- `vision/` 디렉토리 구조가 올바른지 확인하세요.
- 필요한 마스크 데이터 파일이 존재하는지 확인하세요.

### 3. "CurationTypes 초기화에 실패했습니다"

- `OPENAI_API_KEY` 환경 변수가 설정되어 있는지 확인하세요.
- `assets/llm/transformed_pair.json` 파일이 존재하는지 확인하세요.

## 📝 참고

- LLM 생성 설명은 TTS(음성 합성)에 최적화되어 있습니다.
- 모든 설명은 "~니다" 체로 작성됩니다.
- 따옴표, 괄호 등 특수 기호는 사용하지 않습니다.
